"""FTAI Voice Agent - Main entry point."""

import os
import time
import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    AgentSession, Agent, RoomInputOptions,
    UserInputTranscribedEvent, AgentStateChangedEvent
)
from livekit.plugins import noise_cancellation, silero, openai, deepgram, cartesia, groq

from config import config

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("latency")


class VoiceAssistant(Agent):
    """Custom voice assistant agent."""

    def __init__(self) -> None:
        super().__init__(
            instructions=config.load_prompt("default"),
        )


async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for the voice agent."""

    # Validate configuration
    missing = config.validate()
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # Create LLM - use Groq for ultra-fast inference
    llm_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    logger.info(f"[CONFIG] Using Groq LLM model: {llm_model}")
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
                logger.info(f"[METRICS] LLM TTFT: {ttft*1000:.0f}ms")
        elif "TTS" in metrics_type:
            ttfb = getattr(metrics, 'ttfb', None)  # time to first byte
            if ttfb:
                logger.info(f"[METRICS] TTS TTFB: {ttfb*1000:.0f}ms")
        elif "STT" in metrics_type:
            duration = getattr(metrics, 'duration', None)
            if duration:
                logger.info(f"[METRICS] STT duration: {duration*1000:.0f}ms")

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        nonlocal user_finished_time
        if event.is_final:
            user_finished_time = time.time()
            transcript = event.transcript[:50] + "..." if len(event.transcript) > 50 else event.transcript
            logger.info(f"[LATENCY] User speech final: '{transcript}'")

    @session.on("agent_state_changed")
    def on_agent_state_changed(event: AgentStateChangedEvent):
        nonlocal user_finished_time, thinking_start_time
        new_state = str(event.new_state)
        logger.info(f"[LATENCY] Agent state: {event.old_state} -> {new_state}")

        # Track when agent starts thinking (processing user input)
        if "thinking" in new_state:
            thinking_start_time = time.time()
            if user_finished_time:
                stt_latency = (thinking_start_time - user_finished_time) * 1000
                logger.info(f"[LATENCY] STT->Think: {stt_latency:.0f}ms")

        # Track when agent starts speaking (end-to-end latency)
        elif "speaking" in new_state:
            now = time.time()
            if thinking_start_time:
                think_to_speak = (now - thinking_start_time) * 1000
                logger.info(f"[LATENCY] Think->Speak: {think_to_speak:.0f}ms (LLM + TTS)")
            if user_finished_time:
                total_latency = (now - user_finished_time) * 1000
                logger.info(f"[LATENCY] *** TOTAL: {total_latency:.0f}ms *** (user done -> agent speaks)")
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
        instructions="Greet the user warmly and introduce yourself as FTAI Voice Assistant. Ask how you can help them today."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
