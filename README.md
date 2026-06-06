# Autonomous HR Recruiting Pipeline

Production-ready Vercel-first recruiting automation with FastAPI serverless functions, Vue 3, Neon Postgres, Upstash QStash, and NVIDIA NIM.

## Architecture

- Frontend: Vue 3, Vite, Pinia, polling every 3000ms.
- Backend: FastAPI at `api/index.py` with the exported app variable named exactly `app`.
- Database: Neon Postgres through async SQLAlchemy.
- Background jobs: Upstash QStash dispatches one serverless agent per stage.
- LLMs: Claude Sonnet 4 for JD and offers, NVIDIA NIM for resume scoring, assessments, validation, and Safety Guard, GPT-4o for interview questions.
- Human gates: after JD generation and after Search Agent screening.

## Deployment Guide

1. Clone the repo.
2. Create a Neon Postgres project and copy `DATABASE_URL`.
3. Create Upstash Redis and copy the REST URL and token.
4. Create Upstash QStash and copy the token plus current and next signing keys.
5. Get an NVIDIA NIM API key from `build.nvidia.com`.
6. Get an Anthropic API key.
7. Get an OpenAI API key.
8. Configure Greenhouse, LinkedIn, and Calendly credentials.
9. Install and log into Vercel:

```bash
npm i -g vercel
vercel login
vercel
```

10. Add every variable from `.env.example` in the Vercel dashboard.
11. Run migrations against Neon:

```bash
DATABASE_URL=your_neon_url alembic upgrade head
```

12. Set the Calendly webhook to:

```text
https://your-project.vercel.app/api/webhooks/calendly
```

13. Deploy production:

```bash
vercel --prod
```

## Local Development

Install backend dependencies from `api/requirements.txt`, then run:

```bash
uvicorn api.index:app --reload
```

Install frontend dependencies:

```bash
cd frontend
npm install
npm run dev
```

## Required Checks

- `api/index.py` exports `app`.
- `vercel.json` points to `api/index.py`.
- `api/requirements.txt` contains no Celery and no TCP Redis client.
- `/api/v1/agents/{agent_name}` verifies the QStash signature before running an agent.
- NIM calls use `https://integrate.api.nvidia.com/v1`.
- The migration creates `jobs`, `candidates`, `interviews`, `offers`, `pipeline_states`, and `agent_runs`.
