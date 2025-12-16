"""Configuration management for the voice agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # LiveKit Configuration
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "devkey")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "secret")

    # OpenRouter Configuration (LLM)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-4o")

    # Deepgram Configuration (STT)
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")

    # Cartesia Configuration (TTS)
    CARTESIA_API_KEY: str = os.getenv("CARTESIA_API_KEY", "")

    # Agent Configuration
    AGENT_NAME: str = os.getenv("AGENT_NAME", "FTAI Voice Assistant")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    BASE_DIR: Path = Path(__file__).parent
    PROMPTS_DIR: Path = BASE_DIR / "prompts"

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration. Returns list of missing keys."""
        missing = []
        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        if not cls.DEEPGRAM_API_KEY:
            missing.append("DEEPGRAM_API_KEY")
        if not cls.CARTESIA_API_KEY:
            missing.append("CARTESIA_API_KEY")
        return missing

    @classmethod
    def load_prompt(cls, name: str = "default") -> str:
        """Load a prompt from the prompts directory."""
        prompt_file = cls.PROMPTS_DIR / f"{name}.txt"
        if prompt_file.exists():
            return prompt_file.read_text().strip()
        return cls.get_default_prompt()

    @staticmethod
    def get_default_prompt() -> str:
        """Return the default system prompt."""
        return """You are a helpful, friendly voice assistant.

Keep your responses concise and conversational - aim for 1-2 sentences unless more detail is specifically needed.

Be natural and engaging, like talking to a knowledgeable friend.

If you don't know something, say so honestly rather than making things up."""


config = Config()
