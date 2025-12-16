"""FTAI Voice Agent - Main entry point."""

import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, silero, openai, deepgram, cartesia

from config import config

# Load environment variables
load_dotenv()


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

    # Create LLM - use OpenRouter
    llm = openai.LLM.with_openrouter(
        model=os.getenv("LLM_MODEL", "openai/gpt-4o"),
        fallback_models=["anthropic/claude-sonnet-4", "openai/gpt-4o-mini"],
    )

    # Create the agent session with STT-LLM-TTS pipeline
    session = AgentSession(
        stt=deepgram.STT(),
        llm=llm,
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
    )

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
