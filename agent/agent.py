"""FTAI Voice Agent - Main entry point."""

import os
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

@function_tool()
async def check_availability(
    context: RunContext,
    date: Annotated[str, "The date to check availability for, e.g. 'tomorrow', 'Thursday', or 'January 15'"],
) -> str:
    """Check available appointment slots for a given date. Always call this before offering times to the caller."""
    log(f"[TOOL] check_availability called for date: {date}")

    # TODO: Replace with actual Google Calendar lookup
    # For now, return mock availability
    today = datetime.now()

    # Parse relative dates
    if date.lower() == "tomorrow":
        target_date = today + timedelta(days=1)
    elif date.lower() == "today":
        target_date = today
    else:
        # For demo, just use tomorrow
        target_date = today + timedelta(days=1)

    day_name = target_date.strftime("%A")
    date_str = target_date.strftime("%B %d")

    # Check if it's a closed day (Sunday/Monday)
    if target_date.weekday() in [6, 0]:  # Sunday=6, Monday=0
        return f"The spa is closed on {day_name}s. We're open Tuesday through Saturday, 9am to 6pm."

    # Mock available slots
    available_slots = ["10:00 AM", "11:30 AM", "2:00 PM", "3:30 PM"]
    slots_str = ", ".join(available_slots)

    return f"Available slots on {day_name}, {date_str}: {slots_str}"


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

    # TODO: Replace with actual Google Calendar booking and Gmail confirmation
    # For now, simulate a successful booking

    return f"Appointment confirmed! {customer_name} is booked for {service} on {date} at {time}. A confirmation email will be sent to {customer_email}."


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
