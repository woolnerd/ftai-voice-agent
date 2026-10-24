# FTAI Voice Agent

A self-hostable voice AI agent built on LiveKit Agents, as an open-source alternative to hosted platforms like Vapi.ai. Runs fully in Docker Compose.

## Why This Exists

Hosted voice platforms like Vapi.ai are convenient, but you pay per minute and give up control of the stack. This project explores the self-hosted alternative:

- **Full control** over data, models, and infrastructure
- **Swappable providers** for speech-to-text (Deepgram), LLM (Groq, originally OpenRouter), and text-to-speech (Cartesia)
- **Real tool calls**: books appointments in Google Calendar and sends email confirmations
- **Latency logging**: records speech-to-thinking and thinking-to-speaking time for each turn

Simple turns felt fast in testing, but tool calls added noticeable delay. No latency or cost benchmarks against Vapi have been published.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│  LiveKit Server │◀────│   Voice Agent   │
│  (Browser UI)   │     │    (WebRTC)     │     │    (Python)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              │                         │                         │
                              ▼                         ▼                         ▼
                        ┌──────────┐             ┌──────────┐             ┌──────────┐
                        │   STT    │             │   LLM    │             │   TTS    │
                        │(Deepgram)│             │(OpenRouter)│           │(Cartesia)│
                        └──────────┘             └──────────┘             └──────────┘
```

## Quick Start

### 1. Get API Keys

| Service | Purpose | Sign Up |
|---------|---------|---------|
| OpenRouter | LLM (GPT-4o, Claude, etc.) | https://openrouter.ai/keys |
| Deepgram | Speech-to-Text | https://console.deepgram.com ($200 free) |
| Cartesia | Text-to-Speech | https://play.cartesia.ai/ |

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
```

### 3. Start Services

```bash
# Start all services (LiveKit, Agent, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f agent
```

### 4. Use the Voice Agent

Open http://localhost:3000 in your browser and click "Connect" to start talking!

## Project Structure

```
ftai-voice-agent/
├── agent/               # Python voice agent
│   ├── agent.py         # Main agent code
│   ├── config.py        # Configuration management
│   ├── prompts/         # System prompts
│   └── Dockerfile
├── frontend/            # Web UI (LiveKit Playground)
├── scripts/             # Setup scripts
├── docker-compose.yml   # One-command startup
├── livekit.yaml         # LiveKit server config
└── PLAN.md              # Detailed project plan
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Media Server | LiveKit | WebRTC infrastructure |
| Agent Framework | LiveKit Agents SDK v1.2 | Voice pipeline orchestration |
| VAD | Silero | Voice activity detection |
| STT | Deepgram | Speech-to-text |
| LLM | OpenRouter | Access to GPT-4o, Claude, etc. |
| TTS | Cartesia | Text-to-speech |

## Development

### Running Locally (without Docker)

```bash
# Terminal 1: Start LiveKit server
docker run --rm -p 7880:7880 -p 7881:7881 -p 50000-50100:50000-50100/udp \
  -v $(pwd)/livekit.yaml:/etc/livekit.yaml \
  livekit/livekit-server --config /etc/livekit.yaml

# Terminal 2: Start the agent
cd agent
pip install -r requirements.txt
python agent.py dev

# Terminal 3: Start the frontend
cd frontend
pnpm install
pnpm dev
```

### Customizing the Agent

Edit `agent/prompts/default.txt` to change the agent's personality and instructions.

## Roadmap

See [GitHub Issues](https://github.com/woolnerd/ftai-voice-agent/issues) for planned features:

- [ ] Latency optimization (<500ms)
- [ ] Error handling & resilience
- [ ] GCP Cloud Run deployment
- [ ] Full GKE production setup

## License

MIT
