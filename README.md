# Meridian

AI-powered trading journal & research assistant. Log trades, track performance, and get AI-driven insights from three specialized agents: a market screener, a position analyst, and a performance coach.

## Services

| Service | Directory | Tech |
|---------|-----------|------|
| Frontend | `frontend/` | Next.js 15, React 19, TypeScript, TailwindCSS |
| Backend | `backend/` | Python 3.12, FastAPI, SQLAlchemy, LangGraph, PostgreSQL |

## Quick Start

```bash
# Start everything with Docker
docker compose up -d

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Postgres: localhost:5432
```

### Run services individually

```bash
# Backend
cd backend && uv venv && uv pip install -e ".[dev]"
cd backend && alembic upgrade head
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm install
cd frontend && npm run dev

# Seed sample data
python scripts/seed.py
```

## Tests

```bash
# Backend (pytest)
cd backend && uv run pytest tests/ -v

# Frontend (vitest)
cd frontend && npm run test -- --run
```

## Architecture

```
Meridian/
├── frontend/          Next.js app (App Router)
│   └── src/app/       Pages: overview, journal, analytics, agents, settings
├── backend/           FastAPI service
│   ├── app/
│   │   ├── agents/    LangGraph AI agents (screener, analyst, coach)
│   │   ├── db/        SQLAlchemy models + async database setup
│   │   ├── routers/   API route handlers
│   │   ├── services/  Business logic layer
│   │   ├── jobs/      APScheduler background jobs
│   │   └── middleware/ Error handling + rate limiting
│   ├── alembic/       Database migrations
│   └── tests/
├── infrastructure/    Azure Bicep IaC templates
└── scripts/           Seed data + utilities
```

### AI Agents

Three LangGraph agents with tool access to market data and trade history:

- **Screener** — Scans markets for trade setups matching your criteria
- **Analyst** — Monitors open positions, suggests exits based on technicals
- **Coach** — Reviews your trading performance and behavioral patterns

### Key API Routes

```
/api/trades            Trade CRUD
/api/strategies        Strategy management
/api/analytics/*       Market data, indicators, screener
/api/agents/*/chat     AI agent conversations
/api/billing/*         Stripe subscription management
```

## Infrastructure

- **Hosting:** Azure Container Apps
- **Database:** Azure PostgreSQL Flexible Server
- **IaC:** Bicep templates in `infrastructure/`
- **CI/CD:** GitHub Actions with path-filtered triggers
