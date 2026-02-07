# Meridian

AI-powered trading journal & research assistant.

## Services

| Service | Directory | Tech |
|---------|-----------|------|
| Frontend | `frontend/` | Next.js 15, React, TypeScript |
| Backend API | `backend/` | .NET 9, Semantic Kernel |
| Analytics | `python-service/` | Python 3.12, FastAPI |

## Getting Started

See individual service READMEs for setup instructions.

## Development

```bash
# Start all services
docker compose up -d

# Or run individually
cd frontend && npm run dev
cd backend/src/Meridian.Api && dotnet run
cd python-service && uvicorn app.main:app --reload
```

## Architecture

See `docs/plans/2026-02-03-meridian-design.md` for full architecture documentation.
