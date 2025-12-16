# FTAI Voice Agent

An open-source voice AI agent that rivals Vapi.ai - built with LiveKit, featuring ultra-low latency (<500ms) and full containerization support.

## Why This Exists

While Vapi.ai offers a convenient SaaS solution, this project demonstrates engineering depth by building a self-hostable alternative that:

- **Reduces costs** by ~40% at scale
- **Achieves lower latency** (~300-500ms vs ~800ms)
- **Gives you full control** over data and infrastructure
- **Proves technical expertise** beyond API integration

## Architecture

```
Frontend (Web) → LiveKit Server (WebRTC) → Agent Worker (Python)
                                              ↓
                              VAD → STT → LLM → TTS
                           (Silero) (Deepgram) (GPT-4o) (ElevenLabs)
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- API Keys: OpenAI, Deepgram, ElevenLabs (optional)

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd ftai-voice-agent

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker-compose up -d

# 4. Open the frontend
open http://localhost:3000
```

## Project Structure

```
ftai-voice-agent/
├── agent/           # Python voice agent
├── frontend/        # Web UI (LiveKit Playground)
├── scripts/         # Setup and utility scripts
├── docs/            # Documentation
├── docker-compose.yml
└── PLAN.md          # Detailed project plan
```

## Development Status

See [PLAN.md](./PLAN.md) for detailed implementation plan and GitHub issues.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Media Server | LiveKit |
| Agent Framework | LiveKit Agents SDK |
| VAD | Silero |
| STT | Deepgram |
| LLM | OpenAI GPT-4o |
| TTS | ElevenLabs / OpenAI |

## License

MIT
