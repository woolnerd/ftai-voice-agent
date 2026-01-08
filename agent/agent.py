"""FTAI Voice Agent - Main entry point."""

import os
import re
import time
import logging
from datetime import datetime, timedelta
from typing import Annotated
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    AgentSession, Agent, RoomInputOptions,
    RunContext, function_tool,
    UserInputTranscribedEvent, AgentStateChangedEvent
)
from livekit.plugins import noise_cancellation, silero, openai, deepgram, cartesia, groq

from config import config
from calendar_service import calendar_service
from email_service import email_service

# Load environment variables
load_dotenv()

# Set up logging - use print for visibility in dev mode
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("latency")

def log(msg):
    """Print to stdout for visibility in dev mode."""
    print(msg, flush=True)


# -----------------------------------------------------------------------------
# Booking Tools
# -----------------------------------------------------------------------------

def parse_date(date_str: str) -> datetime:
    """Parse a natural language date into a datetime object."""
    today = datetime.now()
    date_lower = date_str.lower().strip()

    # Handle relative dates
    if date_lower == "today":
        return today
    elif date_lower == "tomorrow":
        return today + timedelta(days=1)

    # Handle day names (e.g., "Thursday", "this Thursday")
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(days):
        if day in date_lower:
            current_day = today.weekday()
            days_ahead = i - current_day
            if days_ahead <= 0:  # Target day already passed this week
                days_ahead += 7
            return today + timedelta(days=days_ahead)

    # Try to parse "January 15" or "Jan 15" style dates
    try:
        # Try full month name
        parsed = datetime.strptime(date_str, "%B %d")
        return parsed.replace(year=today.year)
    except ValueError:
        pass

    try:
        # Try abbreviated month
        parsed = datetime.strptime(date_str, "%b %d")
        return parsed.replace(year=today.year)
    except ValueError:
        pass

    # Default to tomorrow if we can't parse
    return today + timedelta(days=1)


@function_tool()
async def check_availability(
    context: RunContext,
    date: Annotated[str, "The date to check availability for, e.g. 'tomorrow', 'Thursday', or 'January 15'"],
) -> str:
    """Check available appointment slots for a given date. Always call this before offering times to the caller."""
    log(f"[TOOL] check_availability called for date: {date}")

    target_date = parse_date(date)
    day_name = target_date.strftime("%A")
    date_str = target_date.strftime("%B %d")

    # Check if it's a closed day (Sunday/Monday)
    if target_date.weekday() in [6, 0]:  # Sunday=6, Monday=0
        return f"The spa is closed on {day_name}s. We're open Tuesday through Saturday, 9am to 6pm."

    # Try to get real availability from Google Calendar
    if calendar_service.calendar_id:
        available_slots = calendar_service.get_available_slots(target_date)
        if available_slots:
            slots_str = ", ".join(available_slots[:5])  # Limit to 5 slots for voice
            return f"Available slots on {day_name}, {date_str}: {slots_str}"
        elif available_slots == []:
            return f"I'm sorry, we're fully booked on {day_name}, {date_str}. Would you like to check another day?"

    # Fallback to mock data if calendar not configured
    log("[TOOL] Using mock availability (calendar not configured)")
    mock_slots = ["10:00 AM", "11:30 AM", "2:00 PM", "3:30 PM"]
    slots_str = ", ".join(mock_slots)
    return f"Available slots on {day_name}, {date_str}: {slots_str}"


def parse_time(time_str: str) -> tuple[int, int]:
    """Parse a time string into hours and minutes (24h format)."""
    time_str = time_str.strip().upper()

    # Handle "2:00 PM", "2 PM", "14:00" formats
    match = re.match(r"(\d{1,2}):?(\d{2})?\s*(AM|PM)?", time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)

        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0

        return hour, minute

    return 9, 0  # Default to 9 AM


@function_tool()
async def book_appointment(
    context: RunContext,
    customer_name: Annotated[str, "The customer's full name"],
    customer_email: Annotated[str, "The customer's email address"],
    service: Annotated[str, "The service being booked, e.g. 'Botox', 'HydraFacial', 'consultation'"],
    date: Annotated[str, "The appointment date, e.g. 'Thursday, January 16'"],
    time: Annotated[str, "The appointment time, e.g. '2:00 PM'"],
) -> str:
    """Book an appointment for the customer. Call this after confirming all details with the caller."""
    log(f"[TOOL] book_appointment called:")
    log(f"  - Customer: {customer_name}")
    log(f"  - Email: {customer_email}")
    log(f"  - Service: {service}")
    log(f"  - Date/Time: {date} at {time}")

    # Parse the date and time
    target_date = parse_date(date)
    hour, minute = parse_time(time)
    start_time = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Format for response
    day_name = target_date.strftime("%A")
    date_str = target_date.strftime("%B %d")
    time_str = start_time.strftime("%-I:%M %p")

    # Try to create the calendar event
    if calendar_service.calendar_id:
        result = calendar_service.create_appointment(
            customer_name=customer_name,
            customer_email=customer_email,
            service_type=service,
            start_time=start_time,
        )
        if result:
            log(f"[TOOL] Calendar event created: {result}")

            # Send confirmation email
            email_sent = email_service.send_confirmation_email(
                customer_name=customer_name,
                customer_email=customer_email,
                service_type=service,
                appointment_date=start_time,
            )
            if email_sent:
                log(f"[TOOL] Confirmation email sent to {customer_email}")

            return f"Appointment confirmed! {customer_name} is booked for {service} on {day_name}, {date_str} at {time_str}. A confirmation email has been sent to {customer_email}."
        else:
            return f"I'm sorry, there was an issue booking that time slot. It may have just been taken. Would you like to try a different time?"

    # Fallback if calendar not configured (still try to send email)
    log("[TOOL] Using mock booking (calendar not configured)")
    email_service.send_confirmation_email(
        customer_name=customer_name,
        customer_email=customer_email,
        service_type=service,
        appointment_date=start_time,
    )
    return f"Appointment confirmed! {customer_name} is booked for {service} on {day_name}, {date_str} at {time_str}. A confirmation email will be sent to {customer_email}."


class VoiceAssistant(Agent):
    """Custom voice assistant agent."""

    def __init__(self) -> None:
        super().__init__(
            instructions=config.load_prompt("medspa"),
            tools=[check_availability, book_appointment],
        )


async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for the voice agent."""

    # Validate configuration
    missing = config.validate()
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # Create LLM - use Groq for ultra-fast inference
    llm_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    log(f"[CONFIG] Using Groq LLM model: {llm_model}")
    llm = groq.LLM(model=llm_model)

    # Create the agent session with STT-LLM-TTS pipeline
    session = AgentSession(
        stt=deepgram.STT(),
        llm=llm,
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
    )

    # Track timing for latency measurements
    user_finished_time = None
    thinking_start_time = None

    @session.on("metrics_collected")
    def on_metrics_collected(event):
        metrics = event.metrics
        metrics_type = type(metrics).__name__

        if "LLM" in metrics_type:
            ttft = getattr(metrics, 'ttft', None)  # time to first token
            if ttft:
                log(f"[METRICS] LLM TTFT: {ttft*1000:.0f}ms")
        elif "TTS" in metrics_type:
            ttfb = getattr(metrics, 'ttfb', None)  # time to first byte
            if ttfb:
                log(f"[METRICS] TTS TTFB: {ttfb*1000:.0f}ms")
        elif "STT" in metrics_type:
            duration = getattr(metrics, 'duration', None)
            if duration:
                log(f"[METRICS] STT duration: {duration*1000:.0f}ms")

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        nonlocal user_finished_time
        if event.is_final:
            user_finished_time = time.time()
            transcript = event.transcript[:50] + "..." if len(event.transcript) > 50 else event.transcript
            log(f"[LATENCY] User speech final: '{transcript}'")

    @session.on("agent_state_changed")
    def on_agent_state_changed(event: AgentStateChangedEvent):
        nonlocal user_finished_time, thinking_start_time
        new_state = str(event.new_state)
        log(f"[LATENCY] Agent state: {event.old_state} -> {new_state}")

        # Track when agent starts thinking (processing user input)
        if "thinking" in new_state:
            thinking_start_time = time.time()
            if user_finished_time:
                stt_latency = (thinking_start_time - user_finished_time) * 1000
                log(f"[LATENCY] STT->Think: {stt_latency:.0f}ms")

        # Track when agent starts speaking (end-to-end latency)
        elif "speaking" in new_state:
            now = time.time()
            if thinking_start_time:
                think_to_speak = (now - thinking_start_time) * 1000
                log(f"[LATENCY] Think->Speak: {think_to_speak:.0f}ms (LLM + TTS)")
            if user_finished_time:
                total_latency = (now - user_finished_time) * 1000
                log(f"[LATENCY] *** TOTAL: {total_latency:.0f}ms *** (user done -> agent speaks)")
                user_finished_time = None

    # Start the session
    await session.start(
        room=ctx.room,
        agent=VoiceAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the caller warmly and introduce yourself as Nicki from Glow Medical Spa. Ask how you can help them today."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
