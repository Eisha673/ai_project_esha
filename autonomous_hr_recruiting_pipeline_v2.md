# Autonomous HR Recruiting Pipeline — Enterprise Web Application
**Project #17 | Full Blueprint v2 — Vercel Deployment + NVIDIA NIM**

---

## 1. Project Overview

An end-to-end AI-powered recruiting platform automating the entire hiring lifecycle through five specialized AI agents orchestrated by LangGraph. Built for **Vercel-first deployment** with a serverless-compatible architecture. NVIDIA NIM APIs handle the compute-heavy screening and reasoning tasks using the latest Nemotron models, while Claude 3.5 drives language generation and offer writing.

**Core Value Proposition:**
- Reduce time-to-hire from weeks to days
- Eliminate repetitive recruiter admin work
- NVIDIA Nemotron reasoning for high-accuracy candidate scoring
- Full audit trail of every AI decision, deployed globally on Vercel Edge

---

## 2. Tech Stack (Vercel-Optimized)

| Layer | Technology | Vercel Fit | Notes |
|---|---|---|---|
| Frontend | Vue.js 3 + Vite | ✅ Static deploy on Vercel CDN | Composition API + Pinia |
| Backend API | FastAPI (Python 3.12) | ✅ Vercel Serverless Functions | Entry at `api/index.py` |
| Database | Neon Postgres (Serverless) | ✅ Serverless-native | Replaces self-hosted PostgreSQL |
| Background Jobs | Upstash QStash | ✅ HTTP-based, no TCP worker | Replaces Celery + Redis |
| Caching / Rate Limits | Upstash Redis | ✅ HTTP API, zero cold-start issues | Replaces self-hosted Redis |
| Agent Orchestration | LangGraph (Python) | ✅ Runs inside serverless functions | Stateful via Neon checkpoints |
| Primary LLM | Claude 3.5 (Anthropic) | ✅ API call from serverless | JD writing, offer drafting |
| NVIDIA NIM | Nemotron models | ✅ External API call | Resume scoring, assessment gen |
| Secondary LLM | GPT-4o (OpenAI) | ✅ API call | Interview question banks |
| ATS | Greenhouse Harvest API v3 | ✅ External REST call | Candidate pipeline management |
| Scheduling | Calendly API | ✅ External REST + Webhooks | Interview booking links |
| Candidate Source | LinkedIn API | ✅ External REST call | Profile search + InMail |
| Auth | JWT (python-jose) | ✅ Stateless, fits serverless | No session state needed |
| ORM | SQLAlchemy 2.0 (async) | ✅ Works with asyncpg + Neon | Connection pooling via Neon |

---

## 3. NVIDIA NIM Integration — Model Selection

NVIDIA NIM exposes models via an **OpenAI-compatible API** (`https://integrate.api.nvidia.com/v1`), making integration trivial — same SDK, different base URL and key.

### Models Used Per Agent

| Agent | NVIDIA NIM Model | Model ID | Why |
|---|---|---|---|
| Search Agent (Resume Scoring) | **Llama 3.3 Nemotron Super 49B** | `nvidia/llama-3.3-nemotron-super-49b-v1` | Leading accuracy for reasoning + structured JSON output; best for nuanced resume evaluation |
| Assessment Agent | **Mistral-Nemotron** | `mistralai/mistral-nemotron` | Built for agentic workflows, excels at instruction following + function calling; ideal for generating structured assessments |
| Safety / Bias Check | **Llama 3.1 Nemotron Safety Guard 8B** | `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` | Runs on every AI output to flag biased or discriminatory language before it reaches candidates |
| JD Quality Check (optional) | **Nemotron Nano 9B v2** | `nvidia/nvidia-nemotron-nano-9b-v2` | Lightweight, fast reasoning for quick validation passes; cost-effective at scale |

### NVIDIA NIM Client Wrapper

```python
# backend/integrations/nvidia_nim.py
from openai import AsyncOpenAI
from config import settings

nim_client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=settings.NVIDIA_API_KEY,
)

async def score_resume(resume_text: str, job_requirements: str) -> dict:
    """Uses Nemotron Super 49B for high-accuracy resume scoring."""
    response = await nim_client.chat.completions.create(
        model="nvidia/llama-3.3-nemotron-super-49b-v1",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert HR analyst. Evaluate resumes with strict objectivity. "
                    "Respond ONLY with valid JSON. No preamble or markdown."
                )
            },
            {
                "role": "user",
                "content": f"""
Job Requirements:
{job_requirements}

Resume:
{resume_text}

Return JSON:
{{
  "score": <integer 0-100>,
  "strengths": ["...", "..."],
  "gaps": ["...", "..."],
  "recommendation": "advance|reject|review",
  "reasoning": "<2-3 sentence explanation>"
}}
"""
            }
        ],
        temperature=0.1,
        max_tokens=512,
    )
    import json
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)


async def generate_assessment(role: str, seniority: str, skills: list[str]) -> dict:
    """Uses Mistral-Nemotron for structured assessment generation."""
    response = await nim_client.chat.completions.create(
        model="mistralai/mistral-nemotron",
        messages=[
            {
                "role": "system",
                "content": "You are a senior technical recruiter. Generate role-specific assessments. JSON only."
            },
            {
                "role": "user",
                "content": f"""
Role: {role} ({seniority})
Key Skills Required: {', '.join(skills)}

Generate a JSON assessment:
{{
  "title": "...",
  "duration_minutes": <int>,
  "sections": [
    {{
      "type": "technical|behavioral|situational",
      "question": "...",
      "evaluation_criteria": "..."
    }}
  ]
}}
Provide 4-6 questions total.
"""
            }
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    import json
    return json.loads(response.choices[0].message.content.strip())


async def check_bias(text: str) -> dict:
    """Uses Nemotron Safety Guard to screen output for discriminatory language."""
    response = await nim_client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-safety-guard-8b-v3",
        messages=[
            {"role": "user", "content": text}
        ],
        max_tokens=200,
    )
    result = response.choices[0].message.content.strip().lower()
    is_safe = "safe" in result or "no violation" in result
    return {"is_safe": is_safe, "raw": result}
```

---

## 4. Five-Agent Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     LangGraph Supervisor                         │
│           (State Machine persisted in Neon Postgres)             │
└────┬────────┬──────────┬──────────────┬─────────────────────────┘
     │        │          │              │              │
     ▼        ▼          ▼              ▼              ▼
[Agent 1]  [Agent 2]  [Agent 3]   [Agent 4]      [Agent 5]
  JD        Search    Assessment  Interview        Offer
 Agent      Agent      Agent       Agent           Agent
 Claude     NVIDIA     NVIDIA      GPT-4o          Claude
  3.5       Nemotron   Nemotron    + Calendly       3.5
            Super 49B  Mistral-
                       Nemotron
```

### Agent 1 — JD Agent
- **LLM:** Claude 3.5 (`claude-sonnet-4-20250514`)
- **NVIDIA NIM role:** Nemotron Nano 9B v2 runs a quick quality/bias check on the final JD before posting
- **Actions:** Generate JD → bias check via NIM Safety Guard → post to Greenhouse → syndicate to LinkedIn

### Agent 2 — Search Agent (Resume Screening)
- **LLM:** NVIDIA NIM — **Nemotron Super 49B** (primary scorer)
- **Actions:**
  - Pull applications from Greenhouse Ingestion API
  - For each resume: call `score_resume()` → Nemotron Super 49B returns 0–100 JSON score
  - Run `check_bias()` on the reasoning text → flag any discriminatory language
  - Advance ≥60-scoring candidates in Greenhouse; auto-reject below threshold
- **Why Nemotron Super 49B here:** Highest accuracy reasoning model available on NIM; structured JSON output; handles nuanced evaluation of career gaps, transferable skills, and seniority signals

### Agent 3 — Assessment Agent
- **LLM:** NVIDIA NIM — **Mistral-Nemotron** (assessment generator)
- **Actions:**
  - Call `generate_assessment()` → role-specific test (coding / case study / situational)
  - Send assessment to candidates via Greenhouse email templates
  - Grade submitted responses with Mistral-Nemotron and produce a structured score JSON
- **Why Mistral-Nemotron here:** Purpose-built for enterprise agentic tasks, excellent at structured instruction following and function calling

### Agent 4 — Interview Agent
- **LLM:** GPT-4o (via OpenAI API) — for behavioral interview question generation
- **Actions:** Generate tailored question bank → create Calendly links → send invites → log to Greenhouse

### Agent 5 — Offer Agent
- **LLM:** Claude 3.5 — for high-quality, professional offer letter prose
- **Actions:** Draft compensation package → NIM Safety Guard check on offer language → push to Greenhouse → send for e-signature

---

## 5. Vercel Deployment Architecture

### The Problem Vercel Solves
Traditional Docker + Celery requires you to maintain servers 24/7. On Vercel:
- **No servers to manage** — FastAPI runs as Python Serverless Functions
- **Auto-scaling** — Vercel scales to zero and up automatically
- **Global CDN** — Vue.js frontend delivered from Vercel's edge network worldwide
- **Preview deployments** — Every Git branch gets its own live URL automatically

### Key Serverless Constraints & How We Handle Them

| Constraint | Problem | Our Solution |
|---|---|---|
| 300s function timeout | LangGraph pipeline takes 2-10 min | QStash fires each agent as a separate HTTP job |
| No persistent TCP | Celery/Redis use TCP connections | Upstash Redis (HTTP-based) + Upstash QStash |
| No long-running processes | Celery worker can't run | QStash delivers jobs to `/api/agents/{agent_name}` endpoints |
| Cold starts | Python functions have slow cold starts | Keep functions lightweight; NIM/Claude are external calls |
| No WebSockets | Real-time push impossible | Frontend polls `/api/pipeline/{job_id}/status` every 3 seconds |

### Architecture Flow on Vercel

```
[Recruiter Browser]
      │  (1) POST /api/pipeline/start
      ▼
[Vercel Function: pipeline.py]
      │  (2) Saves initial state to Neon Postgres
      │  (3) POSTs job to Upstash QStash → /api/agents/jd
      ▼
[Upstash QStash]
      │  (4) Delivers HTTP request to /api/agents/jd
      ▼
[Vercel Function: agents/jd.py]
      │  (5) Runs JD Agent → calls Claude 3.5 API
      │  (6) Updates state in Neon
      │  (7) On success: POSTs next job to QStash → /api/agents/search
      ▼
[... continues agent-by-agent]
      │
      ▼
[Recruiter Browser polls /api/pipeline/{id}/status every 3s]
      │  (8) Reads current state from Neon Postgres
      ▼
[Vue.js Dashboard updates live]
```

---

## 6. Vercel Project Structure

```
autonomous-hr-pipeline/
│
├── api/                              ← Vercel Python Serverless Functions
│   ├── index.py                      ← FastAPI app entry (Vercel entry point)
│   ├── config.py                     ← Settings via pydantic-settings
│   ├── database.py                   ← SQLAlchemy async engine → Neon
│   ├── auth/
│   │   └── jwt.py                    ← JWT stateless auth
│   ├── models/
│   │   ├── job.py
│   │   ├── candidate.py
│   │   ├── interview.py
│   │   └── offer.py
│   ├── schemas/
│   │   ├── job.py
│   │   ├── candidate.py
│   │   └── offer.py
│   ├── routers/
│   │   ├── jobs.py                   ← POST/GET /jobs
│   │   ├── candidates.py
│   │   ├── pipeline.py               ← POST /pipeline/start, GET /status
│   │   ├── interviews.py
│   │   └── offers.py
│   ├── agents/
│   │   ├── state.py                  ← RecruitingState TypedDict
│   │   ├── jd_agent.py               ← Claude 3.5 + NIM Safety Guard
│   │   ├── search_agent.py           ← NIM Nemotron Super 49B
│   │   ├── assessment_agent.py       ← NIM Mistral-Nemotron
│   │   ├── interview_agent.py        ← GPT-4o + Calendly
│   │   └── offer_agent.py            ← Claude 3.5 + NIM Safety Guard
│   ├── integrations/
│   │   ├── nvidia_nim.py             ← NVIDIA NIM client (all model calls)
│   │   ├── anthropic_client.py       ← Claude 3.5 wrapper
│   │   ├── openai_client.py          ← GPT-4o wrapper
│   │   ├── greenhouse.py             ← Harvest API v3
│   │   ├── linkedin.py               ← LinkedIn Jobs + RSC API
│   │   ├── calendly.py               ← Calendly scheduling API
│   │   └── qstash.py                 ← Upstash QStash job dispatcher
│   ├── webhooks/
│   │   └── calendly.py               ← Calendly webhook handler
│   └── requirements.txt
│
├── frontend/                         ← Vue.js 3 SPA (Vercel static build)
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/index.js
│   │   ├── stores/
│   │   │   ├── jobs.js
│   │   │   ├── candidates.js
│   │   │   └── pipeline.js
│   │   ├── views/
│   │   │   ├── DashboardView.vue
│   │   │   ├── JobsView.vue
│   │   │   ├── PipelineView.vue      ← Real-time agent progress
│   │   │   ├── CandidatesView.vue
│   │   │   └── OffersView.vue
│   │   ├── components/
│   │   │   ├── AgentStatusCard.vue
│   │   │   ├── NimScoreBadge.vue     ← Shows Nemotron score + reasoning
│   │   │   ├── CandidateKanban.vue
│   │   │   ├── PipelineTimeline.vue
│   │   │   └── OfferModal.vue
│   │   └── api/index.js
│   ├── vite.config.js
│   └── package.json
│
├── vercel.json                       ← Vercel routing config
├── pyproject.toml                    ← Points Vercel to api/index.py
├── .env.example
└── README.md
```

---

## 7. Vercel Configuration Files

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/dist/$1"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 300
    }
  }
}
```

### `pyproject.toml`
```toml
[tool.vercel]
entrypoint = "api/index.py"
```

### `api/index.py` (FastAPI entry point)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import jobs, candidates, pipeline, interviews, offers
from webhooks import calendly as calendly_webhook

app = FastAPI(title="HR Recruiting Pipeline API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your Vercel domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/v1")
app.include_router(candidates.router, prefix="/api/v1")
app.include_router(pipeline.router, prefix="/api/v1")
app.include_router(interviews.router, prefix="/api/v1")
app.include_router(offers.router, prefix="/api/v1")
app.include_router(calendly_webhook.router, prefix="/api/webhooks")
```

---

## 8. QStash Agent Dispatcher (Replaces Celery)

```python
# api/integrations/qstash.py
import httpx
from config import settings

QSTASH_URL = "https://qstash.upstash.io/v2/publish"

async def dispatch_agent(agent_name: str, job_id: str, payload: dict):
    """
    Fire-and-forget: sends a job to QStash which delivers it to
    the agent endpoint. QStash handles retries automatically.
    """
    target_url = f"{settings.VERCEL_URL}/api/v1/agents/{agent_name}"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{QSTASH_URL}/{target_url}",
            headers={
                "Authorization": f"Bearer {settings.QSTASH_TOKEN}",
                "Content-Type": "application/json",
                "Upstash-Retries": "3",
                "Upstash-Delay": "0s",
            },
            json={"job_id": job_id, **payload},
        )
        response.raise_for_status()
        return response.json()
```

Each agent endpoint is a simple POST route:
```python
# api/routers/pipeline.py (agent trigger endpoints)
@router.post("/agents/jd")
async def run_jd_agent_endpoint(payload: dict):
    state = await load_state(payload["job_id"])
    updated_state = await run_jd_agent(state)
    await save_state(updated_state)
    if not updated_state.get("errors"):
        await dispatch_agent("search", payload["job_id"], {})
    return {"status": "ok"}
```

---

## 9. Database Schema (Neon Postgres)

```sql
-- Neon Postgres: same schema as before, now serverless
-- Use connection string from Neon dashboard with ?sslmode=require

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    seniority VARCHAR(50),
    greenhouse_id VARCHAR(100),
    linkedin_job_url TEXT,
    jd_text TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    full_name VARCHAR(255),
    email VARCHAR(255),
    linkedin_url TEXT,
    greenhouse_application_id VARCHAR(100),
    resume_text TEXT,
    -- NVIDIA NIM Nemotron scores
    nim_screen_score INTEGER,
    nim_screen_reasoning TEXT,
    nim_screen_strengths JSONB,
    nim_screen_gaps JSONB,
    nim_bias_flagged BOOLEAN DEFAULT FALSE,
    -- Assessment
    assessment_score INTEGER,
    assessment_pass BOOLEAN,
    stage VARCHAR(50) DEFAULT 'applied',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id),
    calendly_link TEXT,
    scheduled_at TIMESTAMPTZ,
    question_bank JSONB,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id),
    base_salary NUMERIC(12,2),
    equity_percentage NUMERIC(5,2),
    bonus_percentage NUMERIC(5,2),
    offer_letter_text TEXT,
    greenhouse_offer_id VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pipeline state (LangGraph checkpoint store)
CREATE TABLE pipeline_states (
    job_id UUID PRIMARY KEY REFERENCES jobs(id),
    current_stage VARCHAR(50),
    state_json JSONB,
    human_approved BOOLEAN DEFAULT FALSE,
    errors JSONB DEFAULT '[]',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent run logs
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    agent_name VARCHAR(100),
    llm_provider VARCHAR(50),  -- 'nvidia_nim' | 'anthropic' | 'openai'
    nim_model VARCHAR(100),    -- e.g. 'nvidia/llama-3.3-nemotron-super-49b-v1'
    status VARCHAR(50),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 10. Environment Variables (`.env.example`)

```env
# ── Neon Postgres (serverless PostgreSQL) ──────────────────────────
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.neon.tech/hr_pipeline?sslmode=require

# ── Upstash (serverless Redis + QStash) ───────────────────────────
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_redis_token
QSTASH_TOKEN=your_qstash_token
QSTASH_CURRENT_SIGNING_KEY=your_signing_key
QSTASH_NEXT_SIGNING_KEY=your_next_signing_key

# ── NVIDIA NIM ─────────────────────────────────────────────────────
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxx
# Base URL is always: https://integrate.api.nvidia.com/v1

# ── Anthropic (Claude 3.5) ─────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx

# ── OpenAI (GPT-4o) ───────────────────────────────────────────────
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# ── Greenhouse Harvest API v3 ──────────────────────────────────────
GREENHOUSE_API_KEY=your_harvest_v3_key
GREENHOUSE_BASE_URL=https://harvest.greenhouse.io/v1

# ── LinkedIn ───────────────────────────────────────────────────────
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token

# ── Calendly ──────────────────────────────────────────────────────
CALENDLY_ACCESS_TOKEN=your_calendly_token
CALENDLY_USER_URI=https://api.calendly.com/users/your_user_id
CALENDLY_WEBHOOK_SIGNING_KEY=your_webhook_key

# ── App ────────────────────────────────────────────────────────────
SECRET_KEY=your_jwt_secret_key_min_32_chars
VERCEL_URL=https://your-project.vercel.app
```

> **How to add to Vercel:** Dashboard → Project → Settings → Environment Variables. Add all of the above. Never commit `.env` to Git.

---

## 11. Backend `requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
alembic==1.13.2
pydantic==2.8.2
pydantic-settings==2.4.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.27.0
anthropic==0.34.0
openai==1.45.0
langgraph==0.2.0
langchain==0.3.0
langchain-anthropic==0.2.0
langchain-openai==0.2.0
upstash-redis==1.1.0
```

> **Note:** No Celery, no redis-py TCP client — Upstash replaces both with HTTP-based equivalents that are serverless-compatible.

---

## 12. Frontend `package.json` Dependencies

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.2.0",
    "axios": "^1.7.0",
    "@vueuse/core": "^11.0.0",
    "chart.js": "^4.4.0",
    "vue-chartjs": "^5.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "vite": "^5.4.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

### `vite.config.js` (for Vercel)
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000'  // local dev only
    }
  }
})
```

---

## 13. Vercel Deployment Steps

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/autonomous-hr-pipeline.git
git push -u origin main
```

### Step 2 — Create Managed Services
1. **Neon Postgres** → [neon.tech](https://neon.tech) → Create project → copy `DATABASE_URL`
2. **Upstash Redis** → [upstash.com](https://upstash.com) → Create database → copy REST URL + token
3. **Upstash QStash** → Same Upstash account → QStash tab → copy token + signing keys
4. **NVIDIA NIM** → [build.nvidia.com](https://build.nvidia.com) → Get API key → starts with `nvapi-`

### Step 3 — Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy (first time — follow prompts)
vercel

# Set environment variables
vercel env add NVIDIA_API_KEY
vercel env add ANTHROPIC_API_KEY
vercel env add DATABASE_URL
# ... (add all from .env.example)

# Deploy to production
vercel --prod
```

### Step 4 — Run Database Migrations
```bash
# From local machine, pointing at Neon
DATABASE_URL=your_neon_url alembic upgrade head
```

### Step 5 — Configure Webhooks
- **Calendly:** Set webhook URL to `https://your-project.vercel.app/api/webhooks/calendly`
- **Greenhouse:** Set webhook URL to `https://your-project.vercel.app/api/webhooks/greenhouse`

### Step 6 — Verify
```bash
curl https://your-project.vercel.app/api/v1/jobs
# Should return: {"jobs": []}
```

---

## 14. API Endpoints (FastAPI)

### Jobs
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/jobs` | Create a new job requisition |
| `GET` | `/api/v1/jobs` | List all jobs with status |
| `GET` | `/api/v1/jobs/{id}` | Job detail + pipeline status |
| `PATCH` | `/api/v1/jobs/{id}` | Update job details |

### Pipeline Control
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/pipeline/start` | Start full AI pipeline for a job |
| `GET` | `/api/v1/pipeline/{job_id}/status` | Real-time agent state (polled by frontend every 3s) |
| `POST` | `/api/v1/pipeline/{job_id}/approve` | Human-in-the-loop approval gate |
| `POST` | `/api/v1/agents/{agent_name}` | QStash-triggered agent endpoints (internal) |

### Candidates
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/candidates?job_id=` | List candidates + NIM scores |
| `GET` | `/api/v1/candidates/{id}` | Full detail: score, reasoning, bias flags |
| `PATCH` | `/api/v1/candidates/{id}/stage` | Manual stage override |

### Offers
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/offers` | Generate + send offer |
| `GET` | `/api/v1/offers/{id}` | Offer detail |
| `PATCH` | `/api/v1/offers/{id}/status` | Update offer status |

---

## 15. Human-in-the-Loop Gates

The pipeline pauses at two critical points requiring recruiter approval:

1. **After JD Agent** — Recruiter reviews/edits the generated JD before it goes live on LinkedIn/Greenhouse.
2. **After Search Agent** — Recruiter reviews Nemotron scores + reasoning before interviews are booked.

Implementation: pipeline state is set to `human_approved: false` before each gate. The Vue.js frontend shows an approval modal. On recruiter click → `POST /api/v1/pipeline/{id}/approve` → sets `human_approved: true` → dispatches next QStash job.

---

## 16. NVIDIA NIM Model Rationale Summary

| Model | Task | Key Advantage |
|---|---|---|
| `nvidia/llama-3.3-nemotron-super-49b-v1` | Resume scoring | Highest open-model reasoning accuracy; structured JSON output; understands nuanced career signals |
| `mistralai/mistral-nemotron` | Assessment generation | Built for enterprise agentic tasks; reliable function calling and instruction following |
| `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` | Bias/safety check on all AI output | Multilingual content safety; runs fast at 8B; mandatory filter before anything reaches a candidate |
| `nvidia/nvidia-nemotron-nano-9b-v2` | Quick JD validation | Lightweight + fast; configurable thinking budget; cost-efficient for high-frequency validation passes |

All NIM models use the **same OpenAI-compatible SDK** — just swap `base_url` to `https://integrate.api.nvidia.com/v1` and `api_key` to your `NVIDIA_API_KEY`. This means zero additional dependencies.

---

## 17. Codex Implementation Instructions

> **Instruction for OpenAI Codex:** Build this application exactly as specified. Follow these rules strictly:

1. **Vercel-first** — No Docker, no Celery, no self-hosted Redis. All background work goes through Upstash QStash. All database connections go through Neon Postgres with `?sslmode=require`.

2. **NVIDIA NIM via OpenAI SDK** — Use `openai.AsyncOpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=settings.NVIDIA_API_KEY)`. Do not create a custom HTTP client for NIM.

3. **Model assignments are fixed:**
   - Resume scoring → `nvidia/llama-3.3-nemotron-super-49b-v1`
   - Assessment generation → `mistralai/mistral-nemotron`
   - Safety/bias checks → `nvidia/llama-3.1-nemotron-safety-guard-8b-v3`
   - JD writing / offer letters → Claude 3.5 (`claude-sonnet-4-20250514`)
   - Interview questions → GPT-4o

4. **All LLM outputs must be JSON-validated with Pydantic** before being stored or acted on. If JSON parse fails → log error to `agent_runs` → set `state["errors"]` → stop that agent gracefully.

5. **QStash request verification** — Validate the `Upstash-Signature` header on every `/api/v1/agents/*` endpoint using the `QSTASH_CURRENT_SIGNING_KEY`. Reject unverified requests with 401.

6. **NIM Safety Guard on every agent** — Call `check_bias()` on all AI-generated text before it leaves the system. If `is_safe: false` → flag the candidate record → notify recruiter → do not send to candidate.

7. **Greenhouse v3 only** — Harvest v1/v2 deprecated August 2026. Use only v3 endpoints.

8. **Polling not WebSockets** — Frontend polls `/api/v1/pipeline/{job_id}/status` every 3 seconds. This is intentional for Vercel compatibility.

9. **Start with migrations** — Run `alembic upgrade head` against Neon before any other work. All 6 tables must exist.

10. **Test with mocks** — Use `pytest` + `respx` to mock all external HTTP calls (NIM, Claude, Greenhouse, Calendly, QStash). Never make real API calls in CI.

---

## 18. Key Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Vercel 300s function timeout | Each agent is a separate QStash job — no single function runs the full pipeline |
| NIM API rate limits | Exponential backoff in `nvidia_nim.py`; cache identical resume scores in Upstash Redis |
| Nemotron JSON parse failure | Pydantic validation with retry (up to 2 retries with adjusted prompt) |
| Greenhouse API deprecation (v1/v2) | Harvest v3 only throughout codebase |
| Calendly webhook failures | Idempotent handlers + QStash retry logic as fallback |
| Biased AI screening | NIM Safety Guard on every output; mandatory human review gate at shortlist |
| Neon cold starts (serverless DB) | Use Neon's connection pooling (built-in); keep queries simple |
| GDPR / candidate data | Deletion endpoint; store only necessary fields; audit log in `agent_runs` |

---

## 19. Cost Estimate (Monthly, at 50 hires/month)

| Service | Tier | Estimated Cost |
|---|---|---|
| Vercel | Pro | ~$20/month |
| Neon Postgres | Launch | ~$19/month |
| Upstash Redis + QStash | Pay-per-use | ~$5-10/month |
| NVIDIA NIM (Nemotron Super 49B) | Pay-per-token | ~$30-60/month |
| Anthropic Claude 3.5 | Pay-per-token | ~$20-40/month |
| OpenAI GPT-4o | Pay-per-token | ~$10-20/month |
| **Total** | | **~$104-169/month** |

---

*Generated: June 2026 | v2 — Vercel + NVIDIA NIM | Ready for Google Stitch → VS Code → Codex*
