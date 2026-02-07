# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Meridian is an AI-powered trading journal & research assistant. Monorepo with three services:

- **Frontend** (`frontend/`) — Next.js 15, React 19, TypeScript, TailwindCSS
- **Backend API** (`backend/`) — .NET 10, Clean Architecture, Semantic Kernel, EF Core
- **Analytics** (`python-service/`) — Python 3.12, FastAPI, pandas, yfinance

## Common Commands

### Full Stack (Docker)
```bash
docker compose up -d          # Start all services
docker compose down            # Stop all services
```

### Backend (.NET)
```bash
cd backend/src/Meridian.Api && dotnet run                    # Run API (port 5000)
dotnet build backend/Meridian.sln                            # Build solution
dotnet test backend/Meridian.sln                             # Run all tests
dotnet test backend/tests/Meridian.Core.Tests                # Run core tests only
dotnet test backend/tests/Meridian.Api.Tests                 # Run API tests only
dotnet test --filter "FullyQualifiedName~TestMethodName"     # Run single test
dotnet ef migrations add MigrationName --project backend/src/Meridian.Infrastructure --startup-project backend/src/Meridian.Api
```

### Frontend (Next.js)
```bash
cd frontend && npm install     # Install dependencies
cd frontend && npm run dev     # Dev server (port 3000)
cd frontend && npm run build   # Production build
cd frontend && npm run lint    # ESLint
```

### Python Service
```bash
cd python-service && uv venv && uv pip install -e ".[dev]"  # Setup
cd python-service && uvicorn app.main:app --reload           # Dev server (port 8000)
cd python-service && pytest                                  # Run tests
cd python-service && ruff check .                            # Lint
cd python-service && ruff format .                           # Format
```

## Architecture

### Backend Clean Architecture Layers
```
Meridian.Api          → Controllers, Middleware, DI setup (Program.cs)
Meridian.Core         → Entities, Interfaces, DTOs, Enums (zero dependencies)
Meridian.Infrastructure → EF DbContext, Repositories, Cosmos services, HTTP clients
Meridian.Agents       → Semantic Kernel AI agents + plugins
Meridian.Jobs         → Hangfire background jobs
```

**Dependency rule:** Core has no project references. Infrastructure/Agents/Jobs depend on Core. Api depends on everything.

### Dual Database Strategy
- **Azure SQL** (via EF Core `MeridianDbContext`) — Structured data: users, trades, strategies, screenshots
- **Azure Cosmos DB** — Flexible data: conversation history, agent configs, user trading profiles. Services registered conditionally (only if `CosmosConnection` is configured).

### AI Agents (Semantic Kernel)
Three agents in `Meridian.Agents/Agents/`, all extending `BaseAgent`:
- **AnalystAgent** — Position monitoring, exit suggestions
- **CoachAgent** — Performance reviews, behavioral feedback
- **ScreenerAgent** — Market scanning for trade setups

Agents use **Plugins** (`Meridian.Agents/Plugins/`): MarketDataPlugin, TradeHistoryPlugin, UserProfilePlugin.

### Backend Patterns
- Repository pattern: interfaces in `Core/Interfaces/`, implementations in `Infrastructure/`
- Service layer: `ITradeService` → `TradeService` for business logic
- DI via extension methods: `AddInfrastructure()`, `AddAgents()`, `AddHangfireJobs()`, `AddRateLimiting()`
- Rate limiting: global 100/min, AgentChat 20/min, Screener 5/min
- `ErrorHandlingMiddleware` for standardized error responses

### Frontend Structure
- Next.js App Router with file-based routing under `frontend/src/app/`
- Dashboard pages: overview, journal, journal/new, analytics, agents, settings
- API client in `frontend/src/lib/api.ts`
- Auth: Azure AD B2C via `@azure/msal-browser` and `@azure/msal-react`
- Charting: recharts

### Python Service Structure
- FastAPI routers: `market_data`, `indicators`, `screener`, `stats`
- Services layer mirrors routers in `app/services/`
- Config via pydantic-settings in `app/config.py`
- Premium market data via Polygon API (optional)

### Background Jobs (Hangfire)
In `Meridian.Jobs/`: DailySummaryJob, EmbeddingJob, ProfileRefreshJob, ScreenerJob

## Infrastructure
- **Hosting:** Azure Container Apps
- **IaC:** Bicep templates in `infrastructure/` (main.bicep + modules)
- **CI/CD:** GitHub Actions in `.github/workflows/` — path-filtered triggers for each service
- **Container builds:** Multi-stage Dockerfiles for all three services

## Key Configuration
- Backend config: `backend/src/Meridian.Api/appsettings.json` (SQL, Cosmos, AzureOpenAI, Stripe)
- Python service talks to backend via `Services:PythonAnalytics` config
- Frontend API URL: `NEXT_PUBLIC_API_URL` environment variable
- Financial decimal precision: (18,4) in EF Core entity configs
