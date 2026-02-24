# Harness Engineering Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a four-layer development harness enabling end-to-end autonomous task execution with mechanical quality enforcement and proof of testing.

**Architecture:** Four layers built bottom-up: (1) Context & Documentation, (2) Quality Gates & Enforcement, (3) Testing Harness, (4) Orchestration Loop. Each layer is independently useful and compounds with the ones above it.

**Tech Stack:** Python 3.12/FastAPI, Next.js 15/React 19, Playwright, pytest, vitest, hookify, beads (bd), ralph loop

**Design Doc:** `docs/plans/2026-02-24-harness-engineering-design.md`

---

## Phase 1: Context & Documentation

### Task 1: Create `docs/architecture/overview.md`

**Files:**
- Create: `docs/architecture/overview.md`

**Step 1: Write the architecture overview**

```markdown
# Meridian Architecture Overview

## System Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend       │     │   Backend         │     │   PostgreSQL    │
│   Next.js 15     │────▶│   FastAPI         │────▶│   16-alpine     │
│   Port 3000      │     │   Port 8000       │     │   Port 5432     │
│   React 19       │     │   Python 3.12     │     │                 │
│   TailwindCSS 4  │     │   SQLAlchemy      │     │   8 tables      │
└─────────────────┘     │   LangGraph       │     │   JSONB columns │
                         └──────────────────┘     └─────────────────┘
                                │
                         ┌──────┴──────┐
                         │  External    │
                         │  Services    │
                         ├─────────────┤
                         │ Azure OpenAI │
                         │ Stripe       │
                         │ yfinance     │
                         └─────────────┘
```

## Service Boundaries

- **Frontend** (`frontend/`) — UI layer. Next.js App Router. All API calls go through `src/lib/api.ts`. No business logic.
- **Backend** (`backend/`) — API + business logic + AI agents. FastAPI with async SQLAlchemy. Service-layer pattern (no repository classes).
- **Database** — PostgreSQL via SQLAlchemy async + asyncpg. All money fields `Numeric(18,4)`.

## Data Flow

1. Frontend calls `api.ts` functions → HTTP to backend port 8000
2. Router validates request (Pydantic) → calls service function
3. Service runs business logic + DB queries → returns Pydantic response model
4. Response serialized as camelCase JSON via `CamelModel`

## AI Agent Architecture

Three LangGraph agents in `backend/app/agents/`:
- **ScreenerAgent** — Market scanning for trade setups
- **AnalystAgent** — Position monitoring, exit suggestions
- **CoachAgent** — Performance reviews, behavioral feedback

Agents use tools defined in `app/agents/tools.py` for market data, trade access, and user profile queries.

## Background Jobs

APScheduler jobs in `backend/app/jobs/`:
- `daily_summary` — Daily trading summary
- `profile_refresh` — User profile updates
- `screener_job` — Scheduled market scans
- `embedding_job` — Placeholder for future vector embeddings

## Infrastructure

- **Hosting:** Azure Container Apps (2 containers)
- **Database:** Azure PostgreSQL Flexible Server
- **IaC:** Bicep templates in `infrastructure/`
- **CI/CD:** GitHub Actions with path-filtered triggers
- **Auth:** Azure AD B2C (frontend), hardcoded dev user (backend)
```

**Step 2: Commit**

```bash
git add docs/architecture/overview.md
git commit -m "docs: add architecture overview"
```

---

### Task 2: Create `docs/architecture/backend-patterns.md`

**Files:**
- Create: `docs/architecture/backend-patterns.md`

**Step 1: Write backend patterns**

```markdown
# Backend Patterns

## Service Layer Pattern

All business logic lives in `app/services/`. Routers are thin — they validate input, call a service function, and return the result.

```python
# CORRECT — router calls service
@router.post("/api/trades", status_code=201)
async def create_trade(dto: CreateTradeRequest, db: AsyncSession = Depends(get_db)):
    return await trade_service.create_trade(db, user_id, dto)

# WRONG — router contains business logic / DB queries
@router.post("/api/trades", status_code=201)
async def create_trade(dto: CreateTradeRequest, db: AsyncSession = Depends(get_db)):
    trade = Trade(**dto.model_dump())
    db.add(trade)  # NO — this belongs in a service
    await db.commit()
```

Service functions take `db: AsyncSession` as first parameter and run direct SQLAlchemy queries (no repository classes).

## CamelModel for JSON Serialization

All API response and request models inherit from `CamelModel` (defined in `app/models/base.py`):

```python
from app.models.base import CamelModel

class TradeResponse(CamelModel):
    entry_price: Decimal  # serializes as "entryPrice" in JSON
    position_size: Decimal  # serializes as "positionSize" in JSON
```

Exception: Internal-only models (not exposed via API) can use plain `BaseModel`.

## Enum Conventions

Enums use PascalCase string values via Pydantic `Literal` types:

```python
direction: Literal["Long", "Short"]
status: Literal["Open", "Closed", "Cancelled"]
subscription_tier: Literal["Free", "Premium"]
```

No Python `Enum` classes — always `Literal`.

## Financial Precision

All money fields use `Numeric(18,4)` in SQLAlchemy and `Decimal` in Pydantic:

```python
# SQLAlchemy model
entry_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

# Pydantic schema
entry_price: Decimal
```

Never use `float` for financial data.

## Async Everything

All services and routes are fully async. Database sessions use `AsyncSession`:

```python
async def get_trades(db: AsyncSession, user_id: UUID, ...) -> list[TradeResponse]:
    result = await db.execute(query)
```

## Rate Limiting

Applied via slowapi decorators:
- Global: 100 requests/minute
- Agent chat: 20 requests/minute
- Screener: 5 requests/minute

## Error Handling

Global exception handler in `app/middleware/error_handler.py` maps Python exceptions to HTTP status codes. Services raise standard Python exceptions (ValueError, etc.), not HTTP exceptions.

## File Organization

```
app/
├── routers/     → Route handlers (thin, delegate to services)
├── services/    → Business logic + DB queries
├── models/      → Pydantic request/response schemas
├── db/          → SQLAlchemy ORM models + DB setup
├── agents/      → LangGraph AI agents
├── jobs/        → APScheduler background jobs
├── middleware/   → Error handling + rate limiting
├── auth.py      → Auth dependency
├── config.py    → Pydantic settings
└── main.py      → App entry point
```
```

**Step 2: Commit**

```bash
git add docs/architecture/backend-patterns.md
git commit -m "docs: add backend patterns reference"
```

---

### Task 3: Create `docs/architecture/frontend-patterns.md`

**Files:**
- Create: `docs/architecture/frontend-patterns.md`

**Step 1: Write frontend patterns**

```markdown
# Frontend Patterns

## App Router Structure

Next.js 15 App Router with file-based routing under `src/app/`:

```
src/app/
├── page.tsx                          → / (landing)
├── layout.tsx                        → Root layout
├── globals.css                       → Tailwind 4 theme + component classes
├── dashboard/
│   ├── layout.tsx                    → Dashboard sidebar layout (client component)
│   ├── page.tsx                      → /dashboard (overview)
│   ├── journal/
│   │   ├── page.tsx                  → /dashboard/journal
│   │   └── new/page.tsx              → /dashboard/journal/new
│   ├── analytics/page.tsx            → /dashboard/analytics
│   ├── agents/page.tsx               → /dashboard/agents
│   └── settings/page.tsx             → /dashboard/settings
```

## API Client

All backend calls go through `src/lib/api.ts`. Never use raw `fetch()` elsewhere:

```typescript
import { api } from '@/lib/api';

// CORRECT
const trades = await api.getTrades();

// WRONG
const res = await fetch('http://localhost:8000/api/trades');
```

The API client handles base URL, error checking, and JSON parsing.

## Component Architecture

Currently page-level components (no shared component library). Components that need interactivity use `'use client'` directive.

Server components by default. Only add `'use client'` when needed (state, effects, event handlers, browser APIs).

## Styling

Tailwind 4 with custom design tokens in `globals.css`:
- Custom colors: `meridian-navy-*`, `meridian-surface-*`, `meridian-crimson-*`, `meridian-steel-*`
- Component classes: `.meridian-card`, `.meridian-btn-primary`, `.meridian-input`, etc.
- Use custom component classes for consistency. Use Tailwind utilities for one-off adjustments.

## Utilities

`src/lib/utils.ts` provides:
- `cn()` — clsx + tailwind-merge for conditional classes
- `formatCurrency()` — USD formatting
- `formatPercent()` — Percentage with +/- prefix
- `formatNumber()` — Comma-separated numbers
- `formatDate()` — Short date format

## Testing

Vitest + React Testing Library. Tests in `__tests__/` directories co-located with source:

```
src/app/dashboard/__tests__/page.test.tsx    → tests dashboard/page.tsx
src/lib/__tests__/api.test.ts                → tests lib/api.ts
```

Mock `next/link` and `next/image` in component tests. Mock `fetch` in API tests.

## Dependencies

Minimal: React 19, Next.js 15, Tailwind 4, lucide-react (icons), class-variance-authority, clsx, tailwind-merge. No UI component library.
```

**Step 2: Commit**

```bash
git add docs/architecture/frontend-patterns.md
git commit -m "docs: add frontend patterns reference"
```

---

### Task 4: Create `docs/architecture/database.md`

**Files:**
- Create: `docs/architecture/database.md`

**Step 1: Write database reference**

```markdown
# Database Reference

## Connection

PostgreSQL 16 via SQLAlchemy async + asyncpg.

- Dev: `postgresql+asyncpg://meridian:meridian@localhost:5432/meridian`
- Prod: Azure PostgreSQL Flexible Server (via `DATABASE_URL` env var)

## Tables

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| azure_ad_b2c_id | String(128) | UNIQUE, NOT NULL |
| email | String(256) | UNIQUE, NOT NULL |
| display_name | String(256) | NOT NULL |
| subscription_tier | String(20) | NOT NULL, default="Free" |
| stripe_customer_id | String(256) | nullable |
| created_at | DateTime | NOT NULL |
| updated_at | DateTime | NOT NULL |

### trades
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK→users.id CASCADE |
| ticker | String(20) | NOT NULL |
| direction | String(10) | NOT NULL ("Long"/"Short") |
| entry_date | DateTime | NOT NULL |
| entry_price | Numeric(18,4) | NOT NULL |
| exit_date | DateTime | nullable |
| exit_price | Numeric(18,4) | nullable |
| position_size | Numeric(18,4) | NOT NULL |
| stop_loss | Numeric(18,4) | nullable |
| take_profit | Numeric(18,4) | nullable |
| pnl | Numeric(18,4) | nullable |
| pnl_percent | Numeric(18,4) | nullable |
| status | String(20) | NOT NULL, default="Open" |
| entry_thesis | String(2000) | nullable |
| exit_thesis | String(2000) | nullable |
| market_sentiment | Integer | nullable |
| emotional_state | String(100) | nullable |
| market_conditions | String(500) | nullable |
| notes | Text | nullable |
| created_at | DateTime | NOT NULL |
| updated_at | DateTime | NOT NULL |

Indexes: `(user_id, status)`, `(user_id, entry_date)`

### strategies
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK→users.id CASCADE |
| name | String(100) | NOT NULL, UNIQUE(user_id, name) |
| description | String(500) | nullable |
| source | String(10) | NOT NULL, default="user" |
| created_at | DateTime | NOT NULL |

### trade_strategy_tags (junction)
| Column | Type | Constraints |
|--------|------|-------------|
| trade_id | UUID | PK, FK→trades.id CASCADE |
| strategy_id | UUID | PK, FK→strategies.id RESTRICT |
| source | String(10) | NOT NULL, default="user" |

### trade_screenshots
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| trade_id | UUID | FK→trades.id CASCADE |
| blob_url | String(1024) | NOT NULL |
| caption | String(500) | nullable |
| uploaded_at | DateTime | NOT NULL |

### conversations
| Column | Type | Constraints |
|--------|------|-------------|
| id | String | PK |
| user_id | String | NOT NULL, indexed |
| agent_type | String(20) | NOT NULL |
| title | String(200) | NOT NULL |
| messages | JSONB | NOT NULL, default=[] |
| created_at | DateTime | NOT NULL |
| updated_at | DateTime | NOT NULL |

### agent_configs
| Column | Type | Constraints |
|--------|------|-------------|
| id | String | PK |
| user_id | String | NOT NULL, indexed |
| agent_type | String(20) | NOT NULL |
| custom_system_prompt | Text | nullable |
| settings | JSONB | nullable |
| is_enabled | Boolean | NOT NULL, default=True |
| created_at | DateTime | NOT NULL |
| updated_at | DateTime | NOT NULL |

### user_profiles
| Column | Type | Constraints |
|--------|------|-------------|
| id | String | PK |
| user_id | String | NOT NULL, UNIQUE |
| trading_style | String(50) | nullable |
| preferred_sectors | JSONB | nullable |
| watchlist_tickers | JSONB | nullable |
| strategy_performance | JSONB | nullable |
| risk_profile | String(50) | nullable |
| last_refreshed | DateTime | nullable |

## Migration Conventions

Alembic migrations in `backend/alembic/`:

```bash
# Create a new migration
cd backend && alembic revision --autogenerate -m "description of change"

# Run migrations
cd backend && alembic upgrade head

# Downgrade one step
cd backend && alembic downgrade -1
```

Always review autogenerated migrations before committing. Ensure `Numeric(18,4)` precision is preserved.

## Financial Precision Rules

1. All money columns: `Numeric(18,4)` — never `Float`, never `Integer`
2. P&L calculation in `trade_service.update_trade()`:
   - Long: `(exit_price - entry_price) * position_size`
   - Short: `(entry_price - exit_price) * position_size`
3. Frontend must not perform financial math with JS `number` — display only
```

**Step 2: Commit**

```bash
git add docs/architecture/database.md
git commit -m "docs: add database reference"
```

---

### Task 5: Create `docs/golden-principles.md`

**Files:**
- Create: `docs/golden-principles.md`

**Step 1: Write golden principles**

```markdown
# Golden Principles

Non-negotiable rules for all code changes. Enforced mechanically by hookify rules and structural tests.

## Data Integrity

1. **All money fields use `Numeric(18,4)`**, never floats. SQLAlchemy: `Numeric(18, 4)`. Pydantic: `Decimal`.
2. **Enums are PascalCase Literal strings**: `"Long"`, `"Short"`, `"Open"`, `"Closed"`, `"Cancelled"`, `"Free"`, `"Premium"`.
3. **API responses are camelCase** via `CamelModel` base class. All response models must inherit `CamelModel`.

## Architecture

4. **No DB queries in routers.** Routers call service functions. Services contain business logic and DB queries.
5. **Frontend API calls go through `lib/api.ts`.** No raw `fetch()` outside the API client.
6. **Services are async.** All service functions use `async def` and take `AsyncSession`.

## Quality

7. **Every new endpoint gets a route test + contract test.** Route test verifies HTTP behavior. Contract test verifies response shape.
8. **Playwright tests required for any UI change.** New or modified pages/components must have e2e coverage.
9. **Test coverage must not decrease.** If you add code, add tests. Coverage delta is tracked per PR.
10. **No secrets in committed files.** API keys, connection strings, tokens go in environment variables via `app/config.py`.

## Hygiene

11. **File size limit: 400 lines.** Split files that grow beyond this. Prefer focused modules.
12. **Branch naming: `<type>/<short-description>`** — e.g., `feat/position-sizing`, `fix/pnl-calculation`.
13. **Never push directly to master.** Always feature branch → PR → merge.

## Testing

14. **Backend tests use the existing conftest.py fixtures.** `mock_db`, `mock_result`, `sample_trade`, `sample_strategy`, `sample_user`, `sample_conversation`.
15. **Frontend tests mock `next/link`, `next/image`, and `fetch`.** Use React Testing Library patterns from existing tests.
```

**Step 2: Commit**

```bash
git add docs/golden-principles.md
git commit -m "docs: add golden principles"
```

---

### Task 6: Create `docs/testing-standards.md`

**Files:**
- Create: `docs/testing-standards.md`

**Step 1: Write testing standards**

```markdown
# Testing Standards

## Required Tests by Change Type

| Change Type | Unit Test | Integration/Route Test | Contract Test | Playwright E2E | Visual Regression |
|---|---|---|---|---|---|
| New backend endpoint | Yes | Yes | Yes | — | — |
| Modified backend endpoint | Yes (if logic changed) | Yes | Yes | — | — |
| New service function | Yes | — | — | — | — |
| Modified service function | Yes | — | — | — | — |
| New frontend page | Yes (render test) | — | — | Yes | Yes |
| Modified frontend page | Yes (if logic changed) | — | — | Yes | Yes |
| New frontend component | Yes (render test) | — | — | — | — |
| Bug fix | Yes (regression test) | As needed | As needed | As needed | — |
| Database migration | — | Yes (verify migration) | Yes (verify response shapes) | — | — |

## Commands

### Backend
```bash
# All tests with coverage
cd backend && uv run pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

# Specific test file
cd backend && uv run pytest tests/test_trade_service.py -v

# Specific test
cd backend && uv run pytest tests/test_trade_service.py::test_create_trade_sets_status_open -v

# Lint + format check
cd backend && ruff check . && ruff format --check .
```

### Frontend
```bash
# All tests
cd frontend && npm run test

# Specific test file
cd frontend && npx vitest run src/lib/__tests__/api.test.ts

# Lint
cd frontend && npm run lint

# Build (catches TypeScript errors)
cd frontend && npm run build
```

### E2E
```bash
# All e2e tests (requires docker compose up)
cd e2e && npx playwright test --reporter=list

# Specific spec
cd e2e && npx playwright test tests/trade-crud.spec.ts

# With UI (local debugging)
cd e2e && npx playwright test --ui

# Update visual regression baselines
cd e2e && npx playwright test --update-snapshots
```

## Coverage Bar

- Backend: Coverage must not decrease on any PR. Target: 80%+.
- Frontend: All new pages and components must have render tests.
- E2E: All user-facing flows must have at least a happy-path spec.

## Contract Test Pattern

Contract tests verify that API response shapes match frontend expectations:

```python
# backend/tests/contracts/test_trade_contracts.py

async def test_trade_response_keys_are_camel_case():
    """Every key in the serialized TradeResponse must be camelCase."""
    response = TradeResponse(**sample_data)
    json_dict = response.model_dump(mode="json", by_alias=True)
    for key in json_dict:
        assert key[0].islower(), f"Key '{key}' is not camelCase"
        assert "_" not in key, f"Key '{key}' contains underscore"

async def test_trade_response_enum_values():
    """Direction and status must be PascalCase."""
    response = TradeResponse(**sample_data)
    json_dict = response.model_dump(mode="json", by_alias=True)
    assert json_dict["direction"] in ["Long", "Short"]
    assert json_dict["status"] in ["Open", "Closed", "Cancelled"]
```

## Visual Regression Pattern

```typescript
// e2e/tests/example.spec.ts
test('page matches visual baseline', async ({ page }) => {
  await page.goto('/dashboard/journal');
  await expect(page).toHaveScreenshot('journal-page.png', {
    maxDiffPixelRatio: 0.01,
  });
});
```

Baselines stored in `e2e/tests/*.spec.ts-snapshots/`. New baselines committed with the PR.

## Test Evidence Report

Every PR must include a test evidence section:

```markdown
## Test Evidence

### Backend (pytest)
- **Result:** X passed, 0 failed, 0 skipped
- **Coverage:** X% → Y% (+Z%)

### Contract Tests
- **Result:** X contract tests passed

### Frontend (vitest)
- **Result:** X passed, 0 failed
- **Build:** success

### E2E (Playwright)
- **Result:** X specs passed (Y existing + Z new)
- **Visual regression:** X screenshots compared, 0 diffs above threshold

### Self-Review
- [x] Golden principles checklist completed
```
```

**Step 2: Commit**

```bash
git add docs/testing-standards.md
git commit -m "docs: add testing standards"
```

---

### Task 7: Create `docs/contracts/enum-values.md`

**Files:**
- Create: `docs/contracts/enum-values.md`

**Step 1: Write canonical enum values**

```markdown
# Canonical Enum Values

Single source of truth for all enum-like values shared between frontend and backend.

## Trade Direction
- `"Long"` — Buying to profit from price increase
- `"Short"` — Selling to profit from price decrease

**Backend:** `Literal["Long", "Short"]` in `app/models/trade_schemas.py`
**Frontend:** `direction` field in `TradeResponse` type in `src/lib/api.ts`

## Trade Status
- `"Open"` — Trade is active
- `"Closed"` — Trade has been exited
- `"Cancelled"` — Trade was cancelled before exit

**Backend:** `Literal["Open", "Closed", "Cancelled"]` in `app/models/trade_schemas.py`
**Frontend:** `status` field in `TradeResponse` type in `src/lib/api.ts`

## Subscription Tier
- `"Free"` — Free tier (default)
- `"Premium"` — Paid tier

**Backend:** Default value `"Free"` in `app/db/models.py` User.subscription_tier

## Agent Type
- `"screener"` — Market scanning agent
- `"analyst"` — Position analysis agent
- `"coach"` — Performance coaching agent

**Backend:** `VALID_AGENT_TYPES` set in `app/routers/agents.py`

## Screener Universe
- `"sp500"` — S&P 500 sample
- `"nasdaq100"` — NASDAQ-100 sample
- `"custom"` — User-provided ticker list

**Backend:** `Literal["sp500", "nasdaq100", "custom"]` in `app/models/screener_schemas.py`

## Strategy Source
- `"user"` — User-created strategy
- (future: `"ai"` — AI-suggested strategy)

**Backend:** Default `"user"` in `app/db/models.py` Strategy.source
```

**Step 2: Commit**

```bash
git add docs/contracts/enum-values.md
git commit -m "docs: add canonical enum values"
```

---

### Task 8: Create `docs/contracts/api-response-shapes.md`

**Files:**
- Create: `docs/contracts/api-response-shapes.md`

**Step 1: Write API response shape reference**

```markdown
# API Response Shapes

Reference for frontend-backend contract. All response bodies use camelCase keys.

## Trades

### GET /api/trades → `TradeResponse[]`
### GET /api/trades/{id} → `TradeResponse`
### POST /api/trades → `TradeResponse` (201)
### PUT /api/trades/{id} → `TradeResponse`

```json
{
  "id": "uuid",
  "ticker": "AAPL",
  "direction": "Long",
  "entryDate": "2026-01-15T00:00:00",
  "entryPrice": "150.0000",
  "exitDate": null,
  "exitPrice": null,
  "positionSize": "100.0000",
  "stopLoss": "145.0000",
  "takeProfit": "165.0000",
  "pnl": null,
  "pnlPercent": null,
  "status": "Open",
  "entryThesis": "Breakout above resistance",
  "exitThesis": null,
  "marketSentiment": 7,
  "emotionalState": "Confident",
  "marketConditions": "Bullish trend",
  "notes": "Testing",
  "strategyTags": [
    { "id": "uuid", "name": "Momentum", "description": "...", "source": "user", "createdAt": "...", "tradeCount": 0 }
  ],
  "createdAt": "2026-01-15T10:00:00",
  "updatedAt": "2026-01-15T10:00:00"
}
```

### DELETE /api/trades/{id} → 204 (no body)

## Strategies

### GET /api/strategies → `StrategyResponse[]`
### POST /api/strategies → `StrategyResponse` (201)

```json
{
  "id": "uuid",
  "name": "Momentum Breakout",
  "description": "Buy on breakout above resistance",
  "source": "user",
  "createdAt": "2026-01-15T10:00:00",
  "tradeCount": 5
}
```

### DELETE /api/strategies/{id} → 204 (no body)

## Agents

### POST /api/agents/{type}/chat → `ChatResponse`

```json
{
  "message": "Agent response text..."
}
```

### GET /api/agents/conversations → `ConversationSummary[]`

```json
{
  "id": "string",
  "agentType": "screener",
  "title": "Conversation title",
  "messageCount": 5,
  "createdAt": "2026-01-15T10:00:00",
  "updatedAt": "2026-01-15T10:30:00"
}
```

## Analytics

### GET /api/analytics/quote/{ticker} → `QuoteResponse`

```json
{
  "ticker": "AAPL",
  "price": 185.50,
  "change": 2.30,
  "changePercent": 1.25,
  "volume": 45000000,
  "timestamp": "2026-01-15T16:00:00"
}
```

### GET /api/analytics/ohlcv/{ticker} → `OHLCVResponse`

```json
{
  "ticker": "AAPL",
  "bars": [
    { "date": "2026-01-15", "open": 183.0, "high": 186.0, "low": 182.5, "close": 185.5, "volume": 45000000 }
  ],
  "period": "1y",
  "interval": "1d"
}
```

## Billing

### POST /api/billing/checkout → `{ "url": "https://checkout.stripe.com/..." }`
### POST /api/billing/portal → `{ "url": "https://billing.stripe.com/..." }`

## Error Responses

All errors return:

```json
{
  "detail": "Human-readable error message"
}
```

Status codes: 400 (bad request), 404 (not found), 422 (validation), 429 (rate limited), 500 (server error).
```

**Step 2: Commit**

```bash
git add docs/contracts/api-response-shapes.md
git commit -m "docs: add API response shapes contract"
```

---

### Task 9: Restructure CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Read current CLAUDE.md**

Run: Read `CLAUDE.md` to understand current content.

**Step 2: Rewrite as navigation hub**

Replace the full content of `CLAUDE.md` with a slimmed-down version (~80 lines) that serves as a table of contents. Keep the command cheatsheet (agents need this constantly) but move all detailed patterns, architecture, and conventions into the `docs/` files we just created. Reference them with relative paths.

Key sections to keep inline:
- Project overview (2-3 sentences)
- Command cheatsheet (docker, backend, frontend, seed)
- Pointers to `docs/architecture/`, `docs/golden-principles.md`, `docs/testing-standards.md`, `docs/contracts/`

Key sections to remove (now in docs/):
- Architecture details → `docs/architecture/overview.md`
- Backend patterns → `docs/architecture/backend-patterns.md`
- Frontend structure → `docs/architecture/frontend-patterns.md`
- Database details → `docs/architecture/database.md`
- API routes listing → `docs/contracts/api-response-shapes.md`

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: restructure CLAUDE.md as navigation hub"
```

---

### Task 10: Phase 1 verification

**Step 1: Verify all docs exist and are non-empty**

```bash
ls -la docs/architecture/
ls -la docs/contracts/
ls -la docs/golden-principles.md
ls -la docs/testing-standards.md
```

Expected: 4 files in `architecture/`, 2 files in `contracts/`, plus golden-principles and testing-standards.

**Step 2: Verify CLAUDE.md is under 100 lines**

```bash
wc -l CLAUDE.md
```

Expected: Under 100 lines.

**Step 3: Commit phase marker**

```bash
git add -A
git commit -m "docs: complete Phase 1 — context and documentation layer"
```

---

## Phase 2: Quality Gates & Enforcement

### Task 11: Create hookify rule — no floats for money

**Files:**
- Create: `.claude/hookify.no-floats-for-money.local.md`

**Step 1: Write the hookify rule**

```yaml
---
name: no-floats-for-money
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: backend/app/(db|models)/
  - field: new_text
    operator: regex_match
    pattern: \bFloat\b|:\s*float\b
---

**Financial precision violation detected.**

You are using `Float` or `float` in a model/schema file. All monetary fields must use `Numeric(18,4)` in SQLAlchemy or `Decimal` in Pydantic.

See `docs/golden-principles.md` rule #1 and `docs/architecture/database.md`.

Fix: Replace `Float` with `Numeric(18, 4)` or `float` with `Decimal`.
```

**Step 2: Commit**

```bash
git add .claude/hookify.no-floats-for-money.local.md
git commit -m "harness: add hookify rule — no floats for money"
```

---

### Task 12: Create hookify rule — no DB in routers

**Files:**
- Create: `.claude/hookify.no-db-in-routers.local.md`

**Step 1: Write the hookify rule**

```yaml
---
name: no-db-in-routers
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: backend/app/routers/
  - field: new_text
    operator: regex_match
    pattern: session\.execute|\.query\(|db\.add\(|db\.delete\(|\bselect\(|\binsert\(|\bupdate\(|\bdelete\(
---

**Architecture violation: DB query in router file.**

Routers must be thin — delegate to service functions in `app/services/`. Do not run SQLAlchemy queries directly in router handlers.

See `docs/golden-principles.md` rule #4 and `docs/architecture/backend-patterns.md`.

Fix: Move the DB query into the appropriate service file and call it from the router.
```

**Step 2: Commit**

```bash
git add .claude/hookify.no-db-in-routers.local.md
git commit -m "harness: add hookify rule — no DB in routers"
```

---

### Task 13: Create hookify rule — no hardcoded secrets

**Files:**
- Create: `.claude/hookify.no-hardcoded-secrets.local.md`

**Step 1: Write the hookify rule**

```yaml
---
name: no-hardcoded-secrets
enabled: true
event: file
action: block
conditions:
  - field: new_text
    operator: regex_match
    pattern: (sk-[a-zA-Z0-9]{20,}|AKIA[A-Z0-9]{16}|ghp_[a-zA-Z0-9]{36}|postgresql\+asyncpg://[^\s"']+@[^\s"']+|sk_live_|pk_live_|-----BEGIN (RSA |EC )?PRIVATE KEY-----)
---

**Hardcoded secret detected!**

Never commit API keys, connection strings, or private keys. Use environment variables via `app/config.py` (backend) or `NEXT_PUBLIC_*` env vars (frontend).

See `docs/golden-principles.md` rule #10.

Fix: Move the secret to an environment variable and reference it through the settings/config module.
```

**Step 2: Commit**

```bash
git add .claude/hookify.no-hardcoded-secrets.local.md
git commit -m "harness: add hookify rule — no hardcoded secrets"
```

---

### Task 14: Create hookify rule — file size guard

**Files:**
- Create: `.claude/hookify.file-size-guard.local.md`

**Step 1: Write the hookify rule**

```yaml
---
name: file-size-guard
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.(py|ts|tsx)$
  - field: line_count
    operator: greater_than
    pattern: "400"
---

**File exceeds 400 lines.**

Consider splitting this file into smaller, focused modules. Large files are harder for agents to work with and increase the risk of merge conflicts.

See `docs/golden-principles.md` rule #11.
```

**Step 2: Commit**

```bash
git add .claude/hookify.file-size-guard.local.md
git commit -m "harness: add hookify rule — file size guard"
```

---

### Task 15: Create hookify rule — no raw fetch in frontend

**Files:**
- Create: `.claude/hookify.no-raw-fetch.local.md`

**Step 1: Write the hookify rule**

```yaml
---
name: no-raw-fetch
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: frontend/src/(?!lib/api\.ts).*\.(ts|tsx)$
  - field: new_text
    operator: regex_match
    pattern: \bfetch\s*\(
---

**Raw fetch() detected outside API client.**

All backend API calls must go through `src/lib/api.ts`. Do not use `fetch()` directly in pages or components.

See `docs/golden-principles.md` rule #5 and `docs/architecture/frontend-patterns.md`.

Fix: Add a new method to the `api` object in `src/lib/api.ts` and call it from your component.
```

**Step 2: Commit**

```bash
git add .claude/hookify.no-raw-fetch.local.md
git commit -m "harness: add hookify rule — no raw fetch in frontend"
```

---

### Task 16: Create hookify rule — require tests before completion

**Files:**
- Create: `.claude/hookify.require-tests.local.md`

**Step 1: Write the hookify rule**

```yaml
---
name: require-tests
enabled: true
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: pytest|npm run test|vitest|playwright test
---

**Tests not detected in session!**

Before completing work, you must run the relevant test suite and include results as evidence.

See `docs/testing-standards.md` for required tests by change type.

Required commands:
- Backend changes: `cd backend && uv run pytest tests/ -v --tb=short --cov=app --cov-report=term-missing`
- Frontend changes: `cd frontend && npm run test`
- UI changes: `cd e2e && npx playwright test --reporter=list`
```

**Step 2: Commit**

```bash
git add .claude/hookify.require-tests.local.md
git commit -m "harness: add hookify rule — require tests before completion"
```

---

### Task 17: Create structural test — architecture enforcement

**Files:**
- Create: `backend/tests/test_architecture.py`

**Step 1: Write the failing test**

```python
"""Structural tests enforcing architectural invariants.

These tests verify that the codebase follows the architectural rules
defined in docs/golden-principles.md and docs/architecture/backend-patterns.md.
"""

import ast
import importlib
import pkgutil
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).parent.parent
APP_DIR = BACKEND_ROOT / "app"


class TestImportDirection:
    """Routers must not import from db directly — they go through services."""

    def _get_imports(self, filepath: Path) -> list[str]:
        """Extract all import module names from a Python file."""
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def test_routers_do_not_import_db_models(self):
        """Router files must not import from app.db directly."""
        router_dir = APP_DIR / "routers"
        violations = []
        for py_file in router_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            imports = self._get_imports(py_file)
            for imp in imports:
                if imp.startswith("app.db") and "models" in imp:
                    violations.append(f"{py_file.name} imports {imp}")
        assert violations == [], (
            f"Routers must not import DB models directly. "
            f"Use service functions instead.\n"
            f"Violations:\n" + "\n".join(f"  - {v}" for v in violations)
        )

    def test_routers_do_not_use_sqlalchemy_select(self):
        """Router files must not use SQLAlchemy select/insert/update/delete."""
        router_dir = APP_DIR / "routers"
        violations = []
        for py_file in router_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            imports = self._get_imports(py_file)
            for imp in imports:
                if imp == "sqlalchemy" or imp.startswith("sqlalchemy."):
                    violations.append(f"{py_file.name} imports {imp}")
        assert violations == [], (
            f"Routers must not import SQLAlchemy directly. "
            f"DB queries belong in service functions.\n"
            f"Violations:\n" + "\n".join(f"  - {v}" for v in violations)
        )


class TestNoCircularImports:
    """Verify no circular import chains exist within the app."""

    def test_all_modules_importable(self):
        """Every module in app/ should be importable without circular import errors."""
        failures = []
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=[str(APP_DIR)], prefix="app."
        ):
            try:
                importlib.import_module(modname)
            except ImportError as e:
                if "circular" in str(e).lower():
                    failures.append(f"{modname}: {e}")
            except Exception:
                pass  # Other import errors are not circular dependency issues
        assert failures == [], (
            f"Circular imports detected:\n" + "\n".join(f"  - {f}" for f in failures)
        )
```

**Step 2: Run the test**

```bash
cd backend && uv run pytest tests/test_architecture.py -v
```

Expected: All tests PASS (existing code should already follow these patterns).

**Step 3: Commit**

```bash
git add backend/tests/test_architecture.py
git commit -m "harness: add structural architecture tests"
```

---

### Task 18: Create structural test — convention enforcement

**Files:**
- Create: `backend/tests/test_conventions.py`

**Step 1: Write the test**

```python
"""Tests enforcing coding conventions from docs/golden-principles.md."""

import ast
import importlib
import inspect
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import BaseModel

from app.models.base import CamelModel

BACKEND_ROOT = Path(__file__).parent.parent
APP_DIR = BACKEND_ROOT / "app"


class TestCamelModelInheritance:
    """All API response/request models must inherit CamelModel."""

    RESPONSE_MODULES = [
        "app.models.trade_schemas",
        "app.models.strategy_schemas",
        "app.models.agent_schemas",
        "app.models.billing_schemas",
    ]

    def test_api_models_inherit_camel_model(self):
        """Response/request models in API-facing schema modules must inherit CamelModel."""
        violations = []
        for module_name in self.RESPONSE_MODULES:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if not obj.__module__ == module_name:
                    continue
                if issubclass(obj, BaseModel) and not issubclass(obj, CamelModel):
                    violations.append(f"{module_name}.{name}")
        assert violations == [], (
            f"These API models do not inherit CamelModel:\n"
            + "\n".join(f"  - {v}" for v in violations)
            + "\nAll API-facing models must use CamelModel for camelCase JSON. "
            "See docs/golden-principles.md #3."
        )


class TestEnumValues:
    """Enum-like Literal values must be PascalCase."""

    def test_trade_direction_values(self):
        from app.models.trade_schemas import CreateTradeRequest

        hints = CreateTradeRequest.__annotations__
        # Direction should accept "Long" and "Short" (PascalCase)
        schema = CreateTradeRequest.model_json_schema()
        direction_enum = None
        for prop in schema.get("properties", {}).values():
            if "enum" in prop and "Long" in prop["enum"]:
                direction_enum = prop["enum"]
                break
        if direction_enum:
            for val in direction_enum:
                assert val[0].isupper(), (
                    f"Enum value '{val}' is not PascalCase. "
                    "See docs/golden-principles.md #2."
                )

    def test_trade_status_values(self):
        from app.models.trade_schemas import UpdateTradeRequest

        schema = UpdateTradeRequest.model_json_schema()
        status_enum = None
        for prop_name, prop in schema.get("properties", {}).items():
            if "enum" in prop and "Open" in prop["enum"]:
                status_enum = prop["enum"]
                break
        if status_enum:
            for val in status_enum:
                assert val[0].isupper(), (
                    f"Enum value '{val}' is not PascalCase. "
                    "See docs/golden-principles.md #2."
                )


class TestNumericPrecision:
    """All money columns in DB models must use Numeric(18,4)."""

    def test_trade_money_columns_are_numeric(self):
        from app.db.models import Trade

        money_columns = [
            "entry_price", "exit_price", "position_size",
            "stop_loss", "take_profit", "pnl", "pnl_percent",
        ]
        for col_name in money_columns:
            col = Trade.__table__.columns[col_name]
            col_type = str(col.type)
            assert "NUMERIC" in col_type.upper(), (
                f"Trade.{col_name} is {col_type}, expected Numeric. "
                "See docs/golden-principles.md #1."
            )
            # Check precision
            if hasattr(col.type, "precision") and col.type.precision is not None:
                assert col.type.precision == 18, (
                    f"Trade.{col_name} precision is {col.type.precision}, expected 18."
                )
            if hasattr(col.type, "scale") and col.type.scale is not None:
                assert col.type.scale == 4, (
                    f"Trade.{col_name} scale is {col.type.scale}, expected 4."
                )
```

**Step 2: Run the test**

```bash
cd backend && uv run pytest tests/test_conventions.py -v
```

Expected: All tests PASS. If CamelModel inheritance test fails for any model, that's a real finding — the `schemas.py` and `indicator_schemas.py` models use plain `BaseModel` since they're internal/analytics models, not API-facing trade/strategy models. The test is scoped to API-facing modules only.

**Step 3: Commit**

```bash
git add backend/tests/test_conventions.py
git commit -m "harness: add convention enforcement tests"
```

---

### Task 19: Create contract tests for trade endpoint

**Files:**
- Create: `backend/tests/contracts/__init__.py`
- Create: `backend/tests/contracts/test_trade_contracts.py`

**Step 1: Create the contract test directory**

```bash
mkdir -p backend/tests/contracts
```

**Step 2: Write contract tests**

`backend/tests/contracts/__init__.py` — empty file.

`backend/tests/contracts/test_trade_contracts.py`:

```python
"""Contract tests verifying trade API response shapes match frontend expectations.

These tests ensure the backend-frontend contract is maintained:
- All response keys are camelCase
- Enum values are PascalCase
- Numeric precision is preserved
- Required fields are present

Reference: docs/contracts/api-response-shapes.md
"""

import re
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.trade_schemas import CreateTradeRequest, TradeResponse, UpdateTradeRequest
from app.models.strategy_schemas import StrategyResponse


def _sample_trade_data() -> dict:
    """Minimal valid data for constructing a TradeResponse."""
    return {
        "id": uuid4(),
        "ticker": "AAPL",
        "direction": "Long",
        "entry_date": datetime(2026, 1, 15),
        "entry_price": Decimal("150.0000"),
        "exit_date": None,
        "exit_price": None,
        "position_size": Decimal("100.0000"),
        "stop_loss": Decimal("145.0000"),
        "take_profit": Decimal("165.0000"),
        "pnl": None,
        "pnl_percent": None,
        "status": "Open",
        "entry_thesis": "Breakout above resistance",
        "exit_thesis": None,
        "market_sentiment": 7,
        "emotional_state": "Confident",
        "market_conditions": "Bullish trend",
        "notes": "Test trade",
        "strategy_tags": [],
        "created_at": datetime(2026, 1, 15, 10, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0),
    }


CAMEL_CASE_PATTERN = re.compile(r"^[a-z][a-zA-Z0-9]*$")


class TestTradeResponseContract:
    """Verify TradeResponse serialization matches the documented contract."""

    def test_all_keys_are_camel_case(self):
        """Every key in serialized TradeResponse must be camelCase."""
        response = TradeResponse(**_sample_trade_data())
        json_dict = response.model_dump(mode="json", by_alias=True)
        non_camel_keys = [
            key for key in json_dict
            if not CAMEL_CASE_PATTERN.match(key)
        ]
        assert non_camel_keys == [], (
            f"Keys not in camelCase: {non_camel_keys}. "
            "All API response keys must be camelCase via CamelModel. "
            "See docs/golden-principles.md #3."
        )

    def test_direction_is_pascal_case(self):
        """Direction enum values must be PascalCase."""
        for direction in ["Long", "Short"]:
            data = _sample_trade_data()
            data["direction"] = direction
            response = TradeResponse(**data)
            json_dict = response.model_dump(mode="json", by_alias=True)
            assert json_dict["direction"] == direction

    def test_status_is_pascal_case(self):
        """Status enum values must be PascalCase."""
        for status in ["Open", "Closed", "Cancelled"]:
            data = _sample_trade_data()
            data["status"] = status
            response = TradeResponse(**data)
            json_dict = response.model_dump(mode="json", by_alias=True)
            assert json_dict["status"] == status

    def test_required_fields_present(self):
        """All required fields from the contract must be in the response."""
        required_fields = [
            "id", "ticker", "direction", "entryDate", "entryPrice",
            "positionSize", "status", "createdAt", "updatedAt",
        ]
        response = TradeResponse(**_sample_trade_data())
        json_dict = response.model_dump(mode="json", by_alias=True)
        missing = [f for f in required_fields if f not in json_dict]
        assert missing == [], (
            f"Missing required fields: {missing}. "
            "See docs/contracts/api-response-shapes.md."
        )

    def test_numeric_fields_are_strings_or_numbers(self):
        """Numeric fields should serialize without losing precision."""
        response = TradeResponse(**_sample_trade_data())
        json_dict = response.model_dump(mode="json", by_alias=True)
        numeric_fields = ["entryPrice", "positionSize", "stopLoss", "takeProfit"]
        for field in numeric_fields:
            value = json_dict.get(field)
            if value is not None:
                # Value should be serializable without precision loss
                assert isinstance(value, (str, int, float, Decimal)), (
                    f"{field} has unexpected type {type(value)}"
                )


class TestStrategyResponseContract:
    """Verify StrategyResponse serialization."""

    def test_all_keys_are_camel_case(self):
        data = {
            "id": uuid4(),
            "name": "Momentum Breakout",
            "description": "Buy on breakout",
            "source": "user",
            "created_at": datetime(2026, 1, 15),
            "trade_count": 5,
        }
        response = StrategyResponse(**data)
        json_dict = response.model_dump(mode="json", by_alias=True)
        non_camel_keys = [
            key for key in json_dict
            if not CAMEL_CASE_PATTERN.match(key)
        ]
        assert non_camel_keys == [], (
            f"Keys not in camelCase: {non_camel_keys}"
        )
```

**Step 3: Run the tests**

```bash
cd backend && uv run pytest tests/contracts/ -v
```

Expected: All PASS.

**Step 4: Commit**

```bash
git add backend/tests/contracts/
git commit -m "harness: add contract tests for trade and strategy endpoints"
```

---

### Task 20: Create self-review skill

**Files:**
- Create: `~/.claude/skills/self-review/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: self-review
description: Review own changes against golden principles before pushing. Use after implementing changes and before creating a PR.
---

# Self-Review

Review your own changes against the project's golden principles and produce a structured checklist for the PR body.

## Process

1. **Get the diff:**
   ```bash
   git diff --stat HEAD~1
   git diff HEAD~1
   ```

2. **Read the golden principles:**
   Read `docs/golden-principles.md` to load the current rules.

3. **Check each principle against the diff:**

   For each file changed, verify:
   - [ ] No `float`/`Float` for financial data (use `Numeric(18,4)` / `Decimal`)
   - [ ] Enum values are PascalCase Literals
   - [ ] API response models inherit `CamelModel`
   - [ ] No DB queries in router files
   - [ ] No raw `fetch()` outside `lib/api.ts`
   - [ ] All new service functions are `async`
   - [ ] New endpoints have route tests + contract tests
   - [ ] UI changes have Playwright tests
   - [ ] Test coverage did not decrease
   - [ ] No secrets in committed files
   - [ ] No file exceeds 400 lines
   - [ ] Branch name follows `<type>/<description>` convention

4. **Output the checklist** in this format (include in PR body):

   ```markdown
   ## Self-Review Checklist
   - [x] No float types for financial data
   - [x] Enum values are PascalCase
   - [x] API models inherit CamelModel
   - [x] No DB queries in routers
   - [x] No raw fetch outside api.ts
   - [x] New services are async
   - [x] Route tests added for new endpoints
   - [x] Contract tests added for new endpoints
   - [x] Playwright tests for UI changes
   - [x] Coverage maintained or improved
   - [x] No secrets committed
   - [x] All files under 400 lines
   - [x] Branch naming convention followed
   ```

   If any check FAILS, mark it with `[ ]` and add a note:
   ```markdown
   - [ ] FINDING: Missing contract test for PUT /api/trades/{id} → added in next commit
   ```

5. **Fix any findings** before proceeding to PR creation.

## When to Use

- After completing implementation and all tests pass
- Before running the PR creation step
- Can be triggered manually with `/self-review`
```

**Step 2: Commit**

```bash
git add ~/.claude/skills/self-review/SKILL.md
git commit -m "harness: add self-review skill"
```

Note: This file is outside the repo (in user home). Commit it separately if you version your skills, or just create it in place.

---

### Task 21: Phase 2 verification

**Step 1: Verify hookify rules exist**

```bash
ls -la .claude/hookify.*.local.md
```

Expected: 6 rule files.

**Step 2: Run all structural + convention + contract tests**

```bash
cd backend && uv run pytest tests/test_architecture.py tests/test_conventions.py tests/contracts/ -v
```

Expected: All PASS.

**Step 3: Run full backend test suite to check for regressions**

```bash
cd backend && uv run pytest tests/ -v --tb=short
```

Expected: All existing tests still pass.

**Step 4: Commit phase marker**

```bash
git add -A
git commit -m "harness: complete Phase 2 — quality gates and enforcement"
```

---

## Phase 3: Testing Harness

### Task 22: Set up Playwright visual regression

**Files:**
- Modify: `e2e/playwright.config.ts`
- Create: `e2e/tests/visual-regression.spec.ts`

**Step 1: Update playwright config for snapshots**

Add snapshot configuration to the existing `e2e/playwright.config.ts`. In the `use` block, add:

```typescript
snapshotPathTemplate: '{testDir}/{testFileDir}/{testFileName}-snapshots/{arg}{ext}',
```

And update the `expect` block:

```typescript
expect: {
  timeout: 10000,
  toHaveScreenshot: {
    maxDiffPixelRatio: 0.01,
  },
},
```

**Step 2: Create baseline visual regression spec**

`e2e/tests/visual-regression.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('landing page', async ({ page }) => {
    await page.goto('/');
    // Wait for animations to settle
    await page.waitForTimeout(1000);
    await expect(page).toHaveScreenshot('landing-page.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });

  test('dashboard overview', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('dashboard-overview.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });

  test('trade journal', async ({ page }) => {
    await page.goto('/dashboard/journal');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('trade-journal.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });

  test('new trade form', async ({ page }) => {
    await page.goto('/dashboard/journal/new');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('new-trade-form.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });

  test('agents page', async ({ page }) => {
    await page.goto('/dashboard/agents');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('agents-page.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });

  test('analytics page', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('analytics-page.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });

  test('settings page', async ({ page }) => {
    await page.goto('/dashboard/settings');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('settings-page.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });
});
```

**Step 3: Generate initial baselines**

```bash
cd e2e && npx playwright test tests/visual-regression.spec.ts --update-snapshots
```

This creates the baseline screenshots. They will be committed with the PR.

**Step 4: Run visual regression to verify baselines work**

```bash
cd e2e && npx playwright test tests/visual-regression.spec.ts
```

Expected: All PASS (comparing against just-created baselines).

**Step 5: Commit**

```bash
git add e2e/playwright.config.ts e2e/tests/visual-regression.spec.ts e2e/tests/visual-regression.spec.ts-snapshots/
git commit -m "harness: add visual regression testing with baselines"
```

---

### Task 23: Create test evidence collector script

**Files:**
- Create: `scripts/collect-test-evidence.sh`

**Step 1: Write the script**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Test Evidence Collector
# Runs all test tiers and outputs a formatted report for PR bodies.
# Usage: bash scripts/collect-test-evidence.sh [--skip-e2e]

SKIP_E2E=false
if [[ "${1:-}" == "--skip-e2e" ]]; then
  SKIP_E2E=true
fi

REPORT=""
EXIT_CODE=0

echo "=== Running Test Evidence Collection ==="
echo ""

# --- Tier 1 & 2: Backend Tests ---
echo ">>> Backend tests (pytest)..."
BACKEND_OUTPUT=$(cd backend && uv run pytest tests/ -v --tb=short --cov=app --cov-report=term-missing 2>&1) || true
BACKEND_EXIT=$?

# Extract summary line
BACKEND_SUMMARY=$(echo "$BACKEND_OUTPUT" | grep -E "^(FAILED|PASSED|ERROR|=)" | tail -1)
# Extract coverage percentage
BACKEND_COVERAGE=$(echo "$BACKEND_OUTPUT" | grep "^TOTAL" | awk '{print $NF}')

REPORT+="### Backend (pytest)\n"
REPORT+="- **Result:** ${BACKEND_SUMMARY}\n"
REPORT+="- **Coverage:** ${BACKEND_COVERAGE:-unknown}\n\n"

if [[ $BACKEND_EXIT -ne 0 ]]; then
  EXIT_CODE=1
fi

# --- Contract Tests ---
echo ">>> Contract tests..."
CONTRACT_OUTPUT=$(cd backend && uv run pytest tests/contracts/ -v --tb=short 2>&1) || true
CONTRACT_EXIT=$?
CONTRACT_SUMMARY=$(echo "$CONTRACT_OUTPUT" | grep -E "^(FAILED|PASSED|ERROR|=)" | tail -1)

REPORT+="### Contract Tests\n"
REPORT+="- **Result:** ${CONTRACT_SUMMARY}\n\n"

if [[ $CONTRACT_EXIT -ne 0 ]]; then
  EXIT_CODE=1
fi

# --- Tier 3: Frontend Tests ---
echo ">>> Frontend tests (vitest)..."
FRONTEND_OUTPUT=$(cd frontend && npm run test 2>&1) || true
FRONTEND_EXIT=$?
FRONTEND_SUMMARY=$(echo "$FRONTEND_OUTPUT" | grep -E "Tests\s+" | tail -1)

echo ">>> Frontend build..."
BUILD_OUTPUT=$(cd frontend && npm run build 2>&1) || true
BUILD_EXIT=$?

REPORT+="### Frontend (vitest)\n"
REPORT+="- **Result:** ${FRONTEND_SUMMARY:-see output}\n"
if [[ $BUILD_EXIT -eq 0 ]]; then
  REPORT+="- **Build:** success\n\n"
else
  REPORT+="- **Build:** FAILED\n\n"
  EXIT_CODE=1
fi

if [[ $FRONTEND_EXIT -ne 0 ]]; then
  EXIT_CODE=1
fi

# --- Tier 4: E2E Tests ---
if [[ "$SKIP_E2E" == "false" ]]; then
  echo ">>> E2E tests (playwright)..."
  E2E_OUTPUT=$(cd e2e && npx playwright test --reporter=list 2>&1) || true
  E2E_EXIT=$?
  E2E_SUMMARY=$(echo "$E2E_OUTPUT" | grep -E "^\s+\d+ passed" | tail -1)
  VR_SUMMARY=$(echo "$E2E_OUTPUT" | grep -c "visual-regression" || echo "0")

  REPORT+="### E2E (Playwright)\n"
  REPORT+="- **Result:** ${E2E_SUMMARY:-see output}\n"
  REPORT+="- **Visual regression specs run:** ${VR_SUMMARY}\n\n"

  if [[ $E2E_EXIT -ne 0 ]]; then
    EXIT_CODE=1
  fi
else
  REPORT+="### E2E (Playwright)\n"
  REPORT+="- **Result:** skipped (--skip-e2e)\n\n"
fi

# --- Output Report ---
echo ""
echo "========================================="
echo "        TEST EVIDENCE REPORT"
echo "========================================="
echo ""
echo -e "$REPORT"

# Write to file for PR body consumption
echo -e "## Test Evidence\n\n${REPORT}" > /tmp/test-evidence-report.md
echo "Report written to /tmp/test-evidence-report.md"

exit $EXIT_CODE
```

**Step 2: Make executable and test**

```bash
chmod +x scripts/collect-test-evidence.sh
bash scripts/collect-test-evidence.sh --skip-e2e
```

Expected: Backend and frontend tests run, report printed.

**Step 3: Commit**

```bash
git add scripts/collect-test-evidence.sh
git commit -m "harness: add test evidence collector script"
```

---

### Task 24: Phase 3 verification

**Step 1: Run full test suite including structural and contract tests**

```bash
cd backend && uv run pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
```

Expected: All pass, no regressions.

**Step 2: Run frontend tests**

```bash
cd frontend && npm run test && npm run build
```

Expected: All pass, build succeeds.

**Step 3: Verify test evidence collector works**

```bash
bash scripts/collect-test-evidence.sh --skip-e2e
```

Expected: Formatted report output.

**Step 4: Commit phase marker**

```bash
git add -A
git commit -m "harness: complete Phase 3 — testing harness"
```

---

## Phase 4: Orchestration Loop

### Task 25: Initialize beads for meridian

**Step 1: Initialize beads in the repo**

```bash
"C:/Users/Oliver/beads/bd.exe" init
```

**Step 2: Verify initialization**

```bash
"C:/Users/Oliver/beads/bd.exe" info
```

Expected: Shows database location and status.

**Step 3: Create a test task to verify the workflow**

```bash
"C:/Users/Oliver/beads/bd.exe" create "Harness smoke test — verify beads integration" -p 1
```

**Step 4: Commit beads initialization**

```bash
git add .beads/
git commit -m "harness: initialize beads task management"
```

---

### Task 26: Create task-runner skill

**Files:**
- Create: `~/.claude/skills/task-runner/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: task-runner
description: End-to-end task execution. Takes a beads task ID, creates a worktree, runs the ralph loop with testing harness, and opens a PR with evidence. Use when executing a beads task autonomously.
---

# Task Runner

Executes a beads task end-to-end: worktree → implement → test → review → PR.

## Prerequisites

- Beads initialized in repo (`bd info` succeeds)
- Docker running (for integration/e2e tests)
- All npm/pip dependencies installed

## Process

### 1. Load the Task

```bash
"C:/Users/Oliver/beads/bd.exe" show <task-id>
```

Read the task description and acceptance criteria. If criteria are missing or vague, PAUSE and ask the user.

### 2. Update Task Status

```bash
"C:/Users/Oliver/beads/bd.exe" update <task-id> --status in_progress
```

### 3. Determine Scope

From the task description, identify:
- **backend** — Python/FastAPI changes only
- **frontend** — Next.js/React changes only
- **fullstack** — Both backend and frontend
- **infra** — CI/CD, Docker, config changes

### 4. Load Context

Read these docs based on scope:

| Scope | Required Reading |
|-------|-----------------|
| All | `CLAUDE.md`, `docs/golden-principles.md`, `docs/testing-standards.md` |
| backend | `docs/architecture/backend-patterns.md`, `docs/architecture/database.md` |
| frontend | `docs/architecture/frontend-patterns.md` |
| fullstack | All of the above + `docs/contracts/api-response-shapes.md`, `docs/contracts/enum-values.md` |

### 5. Create Worktree

```bash
git worktree add -b feat/<task-slug> ../meridian-<task-slug> master
cd ../meridian-<task-slug>
```

Install dependencies:
```bash
cd backend && uv pip install -e ".[dev]"
cd ../frontend && npm install
cd ../e2e && npm install
```

### 6. Write Implementation Plan

Create a brief plan in the worktree before coding. Save to `docs/plans/` if non-trivial.

### 7. Launch Ralph Loop

Write the PRD from the beads task criteria, then launch:

```bash
powershell -File "$HOME/.claude/skills/ralph-loop/scripts/ralph.ps1" -Name "<task-slug>"
```

The PRD must include:
- Task description from beads
- Success criteria from beads
- Testing requirements from `docs/testing-standards.md`
- Verification commands

### 8. Ralph Loop Iterations

Each iteration should follow this sequence:

**Implementation iterations:**
1. Write code changes
2. Run relevant tests
3. Fix failures
4. Repeat until tests pass

**Testing iteration:**
1. Run full test evidence collection: `bash scripts/collect-test-evidence.sh`
2. If any tier fails, fix and re-run
3. Capture the final report output

**Review iteration:**
1. Run self-review (invoke `/self-review` skill)
2. Fix any findings
3. Re-run tests if fixes were needed

### 9. Create PR

When all tests pass and self-review is clean:

```bash
git push -u origin feat/<task-slug>

gh pr create --title "<concise title>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points from task description>

## Beads Task
<task-id>

## Test Evidence
<paste from /tmp/test-evidence-report.md>

## Self-Review Checklist
<paste from self-review output>

## Visual Regression
<list any new/changed screenshots>

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### 10. Update Beads

```bash
"C:/Users/Oliver/beads/bd.exe" update <task-id> --status review
"C:/Users/Oliver/beads/bd.exe" sync
```

### Circuit Breakers

- **Max ralph iterations:** 5 (default) — override with `--max-iterations` for complex tasks
- **Repeated test failure:** If the same test fails 3 consecutive iterations, PAUSE and surface the issue
- **Coverage drop:** If coverage decreases after implementation, force a test-writing iteration
- **Structural test failure:** STOP immediately — architectural violation needs human guidance
```

**Step 2: Create the skill file**

Write this to `~/.claude/skills/task-runner/SKILL.md`.

---

### Task 27: Create task-lifecycle skill

**Files:**
- Create: `~/.claude/skills/task-lifecycle/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: task-lifecycle
description: Manages beads task state transitions and post-completion cleanup. Use after PR is merged or when managing task status.
---

# Task Lifecycle

Manages task state transitions through the development pipeline.

## States

```
pending → in_progress → review → done
                ↓
              blocked (if circuit breaker trips)
```

## Commands by State

### Start Work (pending → in_progress)
```bash
"C:/Users/Oliver/beads/bd.exe" update <task-id> --status in_progress
```

### Submit for Review (in_progress → review)
```bash
"C:/Users/Oliver/beads/bd.exe" update <task-id> --status review
"C:/Users/Oliver/beads/bd.exe" sync
```

### Complete (review → done)
After PR is merged:
```bash
"C:/Users/Oliver/beads/bd.exe" close <task-id> --reason "PR #<number> merged"
"C:/Users/Oliver/beads/bd.exe" sync
```

### Block (in_progress → blocked)
If circuit breaker trips:
```bash
"C:/Users/Oliver/beads/bd.exe" update <task-id> --status blocked
"C:/Users/Oliver/beads/bd.exe" comments <task-id> add "Blocked: <reason>"
"C:/Users/Oliver/beads/bd.exe" sync
```

## Post-Merge Cleanup

After a PR is merged, clean up the worktree:

```bash
# From main repo
cd C:/Users/Oliver/source/repos/meridian

# Pull merged changes
git checkout master && git pull origin master

# Remove worktree
git worktree remove ../meridian-<task-slug>

# Delete local branch
git branch -d feat/<task-slug>

# Close beads task
"C:/Users/Oliver/beads/bd.exe" close <task-id> --reason "PR #<number> merged"
"C:/Users/Oliver/beads/bd.exe" sync
```

## Listing Tasks

```bash
# All open tasks
"C:/Users/Oliver/beads/bd.exe" list

# Ready to work (no blockers)
"C:/Users/Oliver/beads/bd.exe" ready

# Task details
"C:/Users/Oliver/beads/bd.exe" show <task-id>
```
```

**Step 2: Create the skill file**

Write this to `~/.claude/skills/task-lifecycle/SKILL.md`.

---

### Task 28: Update ralph-loop PRD template

**Files:**
- Modify: `~/.claude/skills/ralph-loop/SKILL.md`

**Step 1: Read current ralph-loop skill**

Read `~/.claude/skills/ralph-loop/SKILL.md`.

**Step 2: Add harness-aware PRD template**

In the PRD template section (Step 6), add the testing and evidence requirements. Update the template to:

```markdown
# [Feature Name]

**Beads Task**: [task-id]

## Project Overview
[1-2 sentence description]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Testing Requirements
Per docs/testing-standards.md:
- [ ] Backend: unit tests for new/changed service functions
- [ ] Backend: route tests for new/changed endpoints
- [ ] Backend: contract tests for API response shapes
- [ ] Frontend: render tests for new/changed components
- [ ] Frontend: build succeeds
- [ ] E2E: Playwright tests for UI changes
- [ ] E2E: visual regression screenshots captured
- [ ] Coverage: did not decrease

## Verification Commands
```bash
# Backend
cd backend && uv run pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

# Frontend
cd frontend && npm run test && npm run build

# E2E
cd e2e && npx playwright test --reporter=list

# Full evidence collection
bash scripts/collect-test-evidence.sh
```

## Evidence Collection
Before creating PR, run: `bash scripts/collect-test-evidence.sh`
Include output in PR body under "## Test Evidence"

## Self-Review
Before creating PR, run self-review skill against docs/golden-principles.md
Include checklist in PR body under "## Self-Review Checklist"

## Notes for Ralph
- Read docs/golden-principles.md before coding
- Follow patterns in docs/architecture/backend-patterns.md and docs/architecture/frontend-patterns.md
- All money fields: Numeric(18,4), never float
- All API responses: camelCase via CamelModel
- All enums: PascalCase Literal strings
```

**Step 3: Commit (if ralph-loop skill is in repo)**

Note: The ralph-loop skill lives in `~/.claude/skills/` which is outside the repo. Update it in place.

---

### Task 29: Update worktree skills for harness integration

**Files:**
- Modify: `~/.claude/skills/worktree-task-start/SKILL.md`
- Modify: `~/.claude/skills/worktree-task-finish/SKILL.md`

**Step 1: Update worktree-task-start**

Add to the "Begin Implementation" section:

```markdown
**5. Load Harness Context**
Before writing any code, read the harness documentation:
```bash
# Always read these
cat docs/golden-principles.md
cat docs/testing-standards.md

# Read based on task scope
cat docs/architecture/backend-patterns.md    # if backend
cat docs/architecture/frontend-patterns.md   # if frontend
cat docs/contracts/api-response-shapes.md    # if fullstack
cat docs/contracts/enum-values.md            # if fullstack
```
```

**Step 2: Update worktree-task-finish**

Add test evidence collection before PR creation:

```markdown
**0. Collect Test Evidence (before push)**
```bash
bash scripts/collect-test-evidence.sh
```
Save the report output — it goes in the PR body.

**0.5. Self-Review**
Run the self-review skill against your changes.
Include the checklist in the PR body.
```

Update the PR body template to include test evidence and self-review sections:

```bash
gh pr create --title "<PR title>" --body "$(cat <<'EOF'
## Summary
- <what this PR does>

## Beads Task
Closes <task-id>

## Test Evidence
<paste from /tmp/test-evidence-report.md>

## Self-Review Checklist
<paste from self-review output>

## Test Plan
- [ ] <how to verify>

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

### Task 30: End-to-end smoke test

**Step 1: Create a test beads task**

```bash
"C:/Users/Oliver/beads/bd.exe" create "Smoke test: add health check timestamp to /health endpoint" -p 1
```

**Step 2: Run the task through the harness manually**

Walk through each step of the task-runner skill:
1. Show the task
2. Create a worktree
3. Make a trivial change (add `"timestamp": datetime.now().isoformat()` to the health endpoint response)
4. Write a test for it
5. Run the test evidence collector
6. Run self-review
7. Create the PR

**Step 3: Verify the PR has the correct format**

Check that the PR body contains:
- Summary
- Beads task reference
- Test evidence report
- Self-review checklist

**Step 4: Close the test task**

```bash
"C:/Users/Oliver/beads/bd.exe" close <task-id> --reason "Smoke test complete"
```

**Step 5: Clean up worktree**

```bash
git worktree remove ../meridian-health-timestamp
git branch -d feat/health-timestamp
```

**Step 6: Final commit**

```bash
git add -A
git commit -m "harness: complete Phase 4 — orchestration loop with smoke test"
```

---

## Summary

| Phase | Tasks | Key Deliverables |
|-------|-------|-----------------|
| **1: Context** | Tasks 1-10 | 9 doc files, restructured CLAUDE.md |
| **2: Quality Gates** | Tasks 11-21 | 6 hookify rules, 3 structural test files, self-review skill |
| **3: Testing Harness** | Tasks 22-24 | Visual regression setup, test evidence collector |
| **4: Orchestration** | Tasks 25-30 | Beads init, task-runner skill, task-lifecycle skill, updated ralph/worktree skills, smoke test |

Total: 30 tasks across 4 phases.

After Phase 4, the harness is operational. You can create a beads task, hand it to Claude, and get back a PR with full test evidence.
