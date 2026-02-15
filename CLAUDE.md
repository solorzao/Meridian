# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Meridian is an AI-powered trading journal & research assistant. Monorepo with two services:

- **Frontend** (`frontend/`) — Next.js 15, React 19, TypeScript, TailwindCSS
- **Backend** (`backend/`) — Python 3.12, FastAPI, SQLAlchemy, LangGraph, PostgreSQL

## Common Commands

### Full Stack (Docker)
```bash
docker compose up -d          # Start all services (frontend + backend + postgres)
docker compose down            # Stop all services
```

### Backend (Python/FastAPI)
```bash
cd backend && uv venv && uv pip install -e ".[dev]"  # Setup
cd backend && uvicorn app.main:app --reload           # Dev server (port 8000)
cd backend && pytest                                  # Run tests
cd backend && ruff check .                            # Lint
cd backend && ruff format .                           # Format
cd backend && alembic upgrade head                    # Run DB migrations
cd backend && alembic revision --autogenerate -m "description"  # Create migration
```

### Frontend (Next.js)
```bash
cd frontend && npm install     # Install dependencies
cd frontend && npm run dev     # Dev server (port 3000)
cd frontend && npm run build   # Production build
cd frontend && npm run lint    # ESLint
```

### Seed Data
```bash
python scripts/seed.py         # Create test user + sample trades
```

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── agents/          → LangGraph AI agents (tools, prompts, orchestrator)
│   ├── db/              → SQLAlchemy models + database setup
│   ├── jobs/            → APScheduler background jobs
│   ├── middleware/       → Error handling + rate limiting
│   ├── models/          → Pydantic schemas (request/response models)
│   ├── routers/         → FastAPI route handlers
│   ├── services/        → Business logic layer
│   ├── auth.py          → Auth dependency (hardcoded user ID for dev)
│   ├── config.py        → Pydantic settings
│   └── main.py          → FastAPI app entry point
├── alembic/             → Database migrations
└── tests/
```

### Database — PostgreSQL
- All data in PostgreSQL via SQLAlchemy async + asyncpg
- 8 tables: users, trades, strategies, trade_strategy_tags, trade_screenshots, conversations, agent_configs, user_profiles
- JSONB columns for flexible data (conversations.messages, user_profiles.watchlist_tickers, etc.)
- Financial precision: Numeric(18,4) for all money fields
- Migrations via Alembic

### AI Agents (LangGraph)
Three agents in `app/agents/`, using LangGraph's `create_react_agent`:
- **ScreenerAgent** — Market scanning for trade setups
- **AnalystAgent** — Position monitoring, exit suggestions
- **CoachAgent** — Performance reviews, behavioral feedback

Agent tools defined in `app/agents/tools.py`:
- Market tools: get_quote, get_ohlcv, calculate_indicators, run_screener
- Trade tools: get_open_trades, get_recent_closed_trades, get_trades_for_ticker, get_trade_count
- Profile tools: get_user_profile, get_watchlist

### API Routes
```
/api/trades          → Trade CRUD (GET, POST, PUT, DELETE)
/api/strategies      → Strategy CRUD (GET, POST, DELETE)
/api/analytics/*     → Market data, indicators, screener (frontend-facing)
/api/agents/*/chat   → AI agent chat
/api/agents/conversations → Conversation management
/api/billing/*       → Stripe checkout, portal, webhooks
/market-data/*       → Legacy market data routes (kept for compatibility)
/screen              → Legacy screener route
/indicators          → Legacy indicator route
/stats/*             → Legacy stats route
```

### Backend Patterns
- Service-layer functions in `app/services/` (no repository classes, direct SQLAlchemy queries)
- CamelCase JSON via `CamelModel` base class with Pydantic `alias_generator=to_camel`
- Enum values are PascalCase strings: "Long", "Short", "Open", "Closed", "Cancelled", "Free", "Premium"
- Rate limiting: global 100/min, AgentChat 20/min, Screener 5/min (via slowapi)
- Global exception handler maps Python exceptions to HTTP status codes
- Hardcoded dev user ID: `00000000-0000-0000-0000-000000000001` (in `app/auth.py`)

### Frontend Structure
- Next.js App Router with file-based routing under `frontend/src/app/`
- Dashboard pages: overview, journal, journal/new, analytics, agents, settings
- API client in `frontend/src/lib/api.ts` (points to port 8000)
- Auth: Azure AD B2C via `@azure/msal-browser` and `@azure/msal-react`
- Charting: recharts

### Background Jobs (APScheduler)
In `app/jobs/`: daily_summary, profile_refresh, screener_job, embedding_job (placeholder)

## Infrastructure
- **Hosting:** Azure Container Apps (2 containers: frontend + backend)
- **Database:** Azure PostgreSQL Flexible Server
- **IaC:** Bicep templates in `infrastructure/` (main.bicep + modules)
- **CI/CD:** GitHub Actions in `.github/workflows/` — path-filtered triggers
- **Container builds:** Dockerfiles for both services

## Key Configuration
- Backend config via environment variables (see `app/config.py`)
- `DATABASE_URL` — PostgreSQL connection string
- `AZURE_OPENAI_*` — Azure OpenAI for AI agents
- `STRIPE_*` — Stripe for billing
- Frontend API URL: `NEXT_PUBLIC_API_URL` environment variable (default: http://localhost:8000)
- Financial decimal precision: Numeric(18,4) in SQLAlchemy models
