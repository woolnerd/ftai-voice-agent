# FTAI Voice Agent - Project Plan

## Vision
Build an open-source voice AI agent that rivals Vapi.ai in quality and latency, demonstrating engineering expertise beyond simple API integration. The goal is to create a containerized, self-hostable solution that proves technical depth while offering significant cost savings at scale.

---

## V1 Milestone: "Wow Factor" Demo

**Objective:** Create a working voice agent demo with sub-500ms latency that can be shown to potential clients.

**Success Criteria:**
- End-to-end voice conversation working locally
- Latency < 500ms (measured from end-of-speech to start-of-response)
- Clean, professional frontend for demos
- Containerized and ready for cloud deployment

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Web)                           │
│                   (LiveKit Agent Playground)                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WebRTC
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LiveKit Server                               │
│              (Media Server - WebRTC Rails)                      │
│         Local: Docker | Cloud: GKE/LiveKit Cloud                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WebSocket
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Worker (Python)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   VAD    │→ │   STT    │→ │   LLM    │→ │   TTS    │        │
│  │ (Silero) │  │(Deepgram)│  │ (GPT-4o) │  │(ElevenLabs)│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Infrastructure
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Media Server | LiveKit Server | Open-source WebRTC, ultra-low latency |
| Agent Framework | LiveKit Agents SDK | Production-ready, well-documented |
| Containerization | Docker + Docker Compose | Easy local dev, cloud-portable |

### AI Pipeline
| Component | Primary Choice | Alternative | Rationale |
|-----------|----------------|-------------|-----------|
| VAD | Silero VAD | WebRTC VAD | Best accuracy, runs locally |
| STT | Deepgram | Whisper (local) | Speed + accuracy balance |
| LLM | OpenAI GPT-4o | Groq (Llama 3.1) | Quality for demos, Groq for speed |
| TTS | ElevenLabs | Cartesia / OpenAI TTS | Quality voice output |

### Frontend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Web UI | LiveKit Agent Playground | Pre-built, brandable, saves 5+ hours |
| Framework | Next.js | Standard, easy to customize |

---

## Phase 1: Local Development Setup

### Issue 1: Project Initialization
**Priority:** P0 (Critical)
**Estimate:** 1 hour

- [ ] Initialize Python project with Poetry/pip
- [ ] Create project structure
- [ ] Set up environment variable management (.env)
- [ ] Create requirements.txt with core dependencies
- [ ] Add .gitignore for Python/Node projects

**Dependencies:**
```
livekit-agents>=0.8.0
livekit-plugins-openai
livekit-plugins-deepgram
livekit-plugins-silero
livekit-plugins-elevenlabs
python-dotenv
```

---

### Issue 2: LiveKit Server Local Setup
**Priority:** P0 (Critical)
**Estimate:** 1-2 hours

- [ ] Create docker-compose.yml for LiveKit Server
- [ ] Configure TURN/STUN servers for WebRTC
- [ ] Generate API keys and secrets
- [ ] Test server connectivity
- [ ] Document local server URLs and ports

**Key Ports:**
- 7880: HTTP API
- 7881: WebRTC (TCP)
- 7882: WebRTC (UDP)
- 7883-7884: TURN

---

### Issue 3: Basic Agent Implementation
**Priority:** P0 (Critical)
**Estimate:** 2-3 hours

- [ ] Create `agent.py` with VoicePipelineAgent
- [ ] Implement VAD (Silero)
- [ ] Integrate STT (Deepgram)
- [ ] Connect LLM (OpenAI GPT-4o)
- [ ] Add TTS (ElevenLabs or OpenAI)
- [ ] Test end-to-end voice conversation

**Agent Configuration:**
```python
agent = VoicePipelineAgent(
    vad=silero.VAD.load(),
    stt=deepgram.STT(),
    llm=openai.LLM(model="gpt-4o"),
    tts=elevenlabs.TTS(),
)
```

---

### Issue 4: Custom System Prompt & Personality
**Priority:** P1 (High)
**Estimate:** 1 hour

- [ ] Create configurable system prompt
- [ ] Add personality/tone settings
- [ ] Implement context management
- [ ] Add conversation memory (basic)
- [ ] Test different personas

---

### Issue 5: Frontend Setup
**Priority:** P1 (High)
**Estimate:** 2 hours

- [ ] Fork/clone LiveKit Agent Playground
- [ ] Configure to connect to local LiveKit server
- [ ] Add basic branding (logo, colors)
- [ ] Test WebRTC connection in browser
- [ ] Ensure microphone permissions work

---

## Phase 2: Optimization & Polish

### Issue 6: Latency Optimization
**Priority:** P1 (High)
**Estimate:** 2-3 hours

- [ ] Measure baseline latency (end-to-end)
- [ ] Implement streaming TTS (if not default)
- [ ] Tune VAD sensitivity
- [ ] Test Groq as LLM alternative (faster)
- [ ] Add latency metrics/logging
- [ ] Target: < 500ms response time

---

### Issue 7: Error Handling & Resilience
**Priority:** P1 (High)
**Estimate:** 2 hours

- [ ] Handle API failures gracefully
- [ ] Implement retry logic
- [ ] Add fallback responses
- [ ] Handle connection drops
- [ ] Add health checks

---

### Issue 8: Logging & Observability
**Priority:** P2 (Medium)
**Estimate:** 1-2 hours

- [ ] Add structured logging
- [ ] Log conversation transcripts
- [ ] Track latency metrics
- [ ] Create simple dashboard (optional)

---

## Phase 3: Containerization

### Issue 9: Agent Dockerization
**Priority:** P1 (High)
**Estimate:** 1-2 hours

- [ ] Create Dockerfile for agent
- [ ] Optimize image size (multi-stage build)
- [ ] Configure environment variables
- [ ] Test container locally
- [ ] Document build and run commands

---

### Issue 10: Full Stack Docker Compose
**Priority:** P1 (High)
**Estimate:** 2 hours

- [ ] Create docker-compose.yml with all services
- [ ] LiveKit Server container
- [ ] Agent container
- [ ] Frontend container (optional)
- [ ] Redis for state (if needed)
- [ ] One-command local startup

---

## Phase 4: Cloud Deployment (Future)

### Issue 11: GCP Cloud Run Deployment
**Priority:** P2 (Medium - Post V1)
**Estimate:** 3-4 hours

- [ ] Configure Google Artifact Registry
- [ ] Set up Cloud Run service
- [ ] Configure environment variables
- [ ] Set up CI/CD (Cloud Build)
- [ ] Document deployment process

---

### Issue 12: LiveKit Cloud Integration (Alternative)
**Priority:** P2 (Medium - Post V1)
**Estimate:** 1-2 hours

- [ ] Sign up for LiveKit Cloud (free tier)
- [ ] Configure agent to use cloud server
- [ ] Update frontend configuration
- [ ] Test cloud-hosted demo

---

### Issue 13: Full GKE Deployment (Production)
**Priority:** P3 (Low - Future)
**Estimate:** 15-20 hours

- [ ] Set up GKE cluster
- [ ] Deploy LiveKit with Helm
- [ ] Configure UDP ingress
- [ ] Set up Redis
- [ ] Configure SSL/TLS
- [ ] Implement autoscaling
- [ ] Set up monitoring

---

## File Structure

```
ftai-voice-agent/
├── README.md
├── PLAN.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── agent/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── agent.py
│   ├── config.py
│   └── prompts/
│       └── default.txt
├── frontend/
│   └── (LiveKit Playground fork)
├── scripts/
│   ├── setup.sh
│   └── generate-keys.sh
└── docs/
    ├── LOCAL_SETUP.md
    └── DEPLOYMENT.md
```

---

## API Keys Required

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| OpenAI | LLM (GPT-4o) | Pay-as-you-go |
| Deepgram | STT | $200 free credit |
| ElevenLabs | TTS | 10k chars/month free |
| LiveKit Cloud | Media Server (optional) | 50GB/month free |

---

## Quick Start Commands (Target)

```bash
# 1. Clone and setup
git clone <repo>
cd ftai-voice-agent
cp .env.example .env
# Edit .env with API keys

# 2. Start everything
docker-compose up -d

# 3. Open frontend
open http://localhost:3000
```

---

## Success Metrics for V1 Demo

1. **Latency:** < 500ms from end-of-speech to start-of-response
2. **Quality:** Natural conversation flow, no awkward pauses
3. **Reliability:** No crashes during 5-minute demo
4. **Presentation:** Professional-looking frontend
5. **Portability:** Works on any machine with Docker

---

## Timeline Summary

| Phase | Effort | Outcome |
|-------|--------|---------|
| Phase 1 | 4-6 hours | Working local demo |
| Phase 2 | 4-5 hours | Polished, low-latency |
| Phase 3 | 3-4 hours | Containerized |
| Phase 4 | 4-20 hours | Cloud deployed |

**V1 Total:** ~12-15 hours for a "wow factor" local demo

---

## References

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit Agent Playground](https://github.com/livekit/agents-playground)
- [Deepgram API](https://developers.deepgram.com/)
- [ElevenLabs API](https://docs.elevenlabs.io/)
