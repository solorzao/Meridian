# Harness Engineering Design — Meridian

**Date:** 2026-02-24
**Status:** Approved
**Goal:** Build a fully automated development harness so that a beads task can be carried out end-to-end by Claude — from implementation, through review and QA (with proof), to PR creation — with deployment remaining human-gated.

## Architecture Overview

Four layers, built bottom-up. Each layer is independently useful but compounds with the ones above it.

```
┌─────────────────────────────────────────────────┐
│  Layer 4: ORCHESTRATION LOOP                    │
│  beads task → ralph loop → PR with proof        │
│  Skills: task-runner, task-lifecycle             │
├─────────────────────────────────────────────────┤
│  Layer 3: TESTING HARNESS                       │
│  pytest (unit+integration+contract)             │
│  vitest (frontend unit)                         │
│  playwright (e2e + visual regression)           │
│  Script: test-evidence-collector                │
├─────────────────────────────────────────────────┤
│  Layer 2: QUALITY GATES                         │
│  Hookify rules, custom linters, structural      │
│  tests, self-review, architecture enforcement   │
├─────────────────────────────────────────────────┤
│  Layer 1: CONTEXT & DOCUMENTATION               │
│  CLAUDE.md as TOC → docs/ structured reference  │
│  Golden principles, architecture decision log   │
│  Contract definitions, testing standards        │
└─────────────────────────────────────────────────┘
```

**Core principle (from OpenAI):** When the agent produces bad output, the fix isn't better prompting — it's building the missing capability into the repo. Every failure becomes infrastructure.

**Autonomy model:** Autonomous through implementation and QA. Human-gated deployment. The agent opens a PR with a complete evidence packet. You review and merge. CI deploys.

## Layer 1: Context & Documentation

### Problem

Current CLAUDE.md is ~150 lines of mixed concerns. The agent pattern-matches locally rather than navigating intentionally. Conventions are implicit, not versioned.

### Solution

Restructure CLAUDE.md into an ~80-line navigation hub pointing to structured docs.

```
CLAUDE.md                          ← TOC: project overview, command cheatsheet, pointers
docs/
├── architecture/
│   ├── overview.md                ← System diagram, service boundaries, data flow
│   ├── backend-patterns.md        ← CamelModel, enum conventions, service layer patterns
│   ├── frontend-patterns.md       ← App Router conventions, component patterns, API client
│   └── database.md                ← Schema, migration conventions, Numeric(18,4) rules
├── golden-principles.md           ← Non-negotiable rules (max 15-20 items)
├── testing-standards.md           ← Required tests per change type, coverage bar
├── contracts/
│   ├── api-response-shapes.md     ← Expected response shapes per endpoint
│   └── enum-values.md             ← Canonical enum definitions shared between FE/BE
└── plans/
    ├── (existing design docs)
    └── (future task plans)
```

### Golden Principles (draft, to be refined)

1. All money fields use `Numeric(18,4)`, never floats
2. API responses are camelCase via `CamelModel`, enums are PascalCase
3. No direct DB queries in routers — always go through service layer
4. Every new endpoint gets a route test + contract test
5. Playwright tests required for any UI change
6. No secrets in committed files
7. Backend services are async, use `AsyncSession`
8. Frontend API calls go through `lib/api.ts`, never raw fetch
9. File size limit: 400 lines per file (split if larger)
10. Branch naming: `<type>/<short-description>`
11. Never push directly to master
12. All Pydantic response models inherit `CamelModel`
13. Rate limiting on all public endpoints
14. Financial decimal precision: `Numeric(18,4)` in SQLAlchemy, never JS `number` for money
15. Test coverage must not decrease on any PR

These are enforced mechanically (Layer 2), not by hoping the agent reads the doc. The doc exists so the agent knows *why* and *how to fix* violations.

## Layer 2: Quality Gates & Enforcement

Three categories matching OpenAI's framework: deterministic linters, structural tests, LLM-based review.

### Hookify Rules

Fire on every tool call, catching violations before they reach a commit:

| Rule | Trigger | Detection | Remediation Message |
|------|---------|-----------|-------------------|
| No floats for money | Edit/Write to `models/` or `db/` | `Float` or `float` in model fields | "Use `Numeric(18,4)` for financial precision. See docs/golden-principles.md #1" |
| No DB in routers | Edit/Write to `routers/` | `session.execute`, `select(`, `insert(` | "Move DB queries to service layer. See docs/architecture/backend-patterns.md" |
| No hardcoded secrets | Edit/Write any file | API key patterns, connection strings | "Use environment variables via app/config.py. Never commit secrets." |
| File size guard | Edit/Write any `.py`/`.ts`/`.tsx` | File exceeds 400 lines | "Split this file. See docs/golden-principles.md #9" |
| Test file required | Bash `git commit` | Source file changed without corresponding test file | "Every code change needs a test. See docs/testing-standards.md" |
| No raw fetch | Edit/Write to `frontend/src/` | `fetch(` outside `lib/api.ts` | "Use the API client in lib/api.ts. See docs/architecture/frontend-patterns.md" |

### Structural Tests

Actual test files that enforce architecture, run as part of the normal test suite:

**`backend/tests/test_architecture.py`**
- Import direction: routers → services → db, never reverse
- No circular dependencies between modules
- All router files import from services, not from db directly

**`backend/tests/test_conventions.py`**
- All Pydantic response models inherit `CamelModel`
- All enum classes use PascalCase string values
- All SQLAlchemy money columns use `Numeric(18,4)`

**`backend/tests/test_api_contracts.py`**
- Serializes every response model, asserts all keys are camelCase
- Validates enum values match canonical list in `docs/contracts/enum-values.md`
- Validates numeric fields maintain precision

**`frontend/src/__tests__/test_structure.ts`** (or vitest equivalent)
- Every route in app/ has a corresponding page component
- No orphan components (components not imported anywhere)

### LLM-Based: Self-Review Skill

After implementation, before pushing, the agent reviews its own diff against the golden principles. Produces a structured checklist included in the PR body:

```markdown
## Self-Review Checklist
- [x] No float types used for financial data
- [x] All new endpoints have route tests
- [x] API responses serialized through CamelModel
- [x] No secrets committed
- [x] No direct DB access in routers
- [x] Coverage did not decrease
- [ ] FINDING: Missing contract test for PUT /api/trades/{id} → fixing now
```

## Layer 3: Testing Harness

Four test tiers, all run locally before push. Every task must produce evidence.

### Tier 1: Backend Unit + Integration Tests (pytest)

- Unit tests for every new/changed service function, mocking external deps
- Integration tests that spin up docker postgres and run real queries
- Command: `pytest tests/ -v --tb=short --cov=app --cov-report=term-missing`
- Coverage delta tracked: if coverage drops, agent must add tests to compensate

### Tier 2: Backend Contract Tests (pytest)

New directory: `backend/tests/contracts/`

For every endpoint the task touches:
- Call the route handler with test data
- Serialize the response through the Pydantic model
- Assert all keys are camelCase
- Assert enum values match canonical list
- Assert numeric precision matches `Numeric(18,4)` expectations

### Tier 3: Frontend Tests (vitest)

- Unit tests for new/changed components and hooks
- Command: `npm run test`
- Build must succeed: `npm run build` (catches TypeScript errors)

### Tier 4: Playwright E2E + Visual Regression

- Run full existing e2e suite for regression: `npx playwright test`
- Write new e2e tests for any UI-touching change (happy path minimum)
- Visual regression:
  - Capture screenshots at key states via `page.screenshot()`
  - Store baselines in `e2e/screenshots/baselines/`
  - On subsequent runs, compare against baselines with pixel-diff threshold
  - New baselines committed with PR so reviewers see visual changes
- All Playwright traces and failure screenshots attached as PR evidence

### Test Evidence Report Format

Captured in the PR body:

```markdown
## Test Evidence

### Backend (pytest)
- **Result:** 47 passed, 0 failed, 0 skipped
- **Coverage:** 78% → 81% (+3%)

### Contract Tests
- **Result:** 12 contract tests passed
- **Endpoints covered:** GET /api/trades, POST /api/trades, PUT /api/trades/{id}

### Frontend (vitest)
- **Result:** 23 passed, 0 failed
- **Build:** success

### E2E (Playwright)
- **Result:** 6 specs passed (4 existing + 2 new)
- **Visual regression:** 3 screenshots compared, 0 diffs above threshold
- **New baselines:** [list of new screenshot files]
- **Traces:** [link to playwright-report/]

### Self-Review
- [checklist as above]
```

## Layer 4: Orchestration Loop

### Step 1: Task Creation (human, manual)

Create a beads task with description, acceptance criteria, and scope:

```bash
bd add "Add position sizing calculator to trade form" \
  --criteria "Calculator appears on new trade page, computes shares from risk %, saves to trade" \
  --scope fullstack
```

### Step 2: Task Pickup (agent, autonomous)

1. Claim the beads task
2. Create git worktree (`feat/<task-slug>`)
3. Read CLAUDE.md → follow pointers to relevant docs based on scope
4. Read golden principles
5. Read testing standards
6. Generate implementation plan → write to `docs/plans/`

### Step 3: Implementation (ralph loop, autonomous)

Ralph loop iterates with fresh context per cycle:

- **Cycle 1:** Implement backend changes, run tier 1+2 tests
- **Cycle 2:** Implement frontend changes, run tier 3 tests
- **Cycle 3:** Write e2e tests, run tier 4 (playwright + visual regression)
- **Cycle 4:** Self-review against golden principles, fix findings
- **Cycle N:** Continue until all gates green or circuit breaker trips

Each cycle receives the full test output from the previous cycle as context.

### Step 4: PR Creation (agent, autonomous)

When all gates pass:
1. Push the branch
2. Open PR with structured test evidence report
3. Attach playwright screenshots/traces
4. Include self-review checklist
5. Mark beads task as "review"

### Step 5: Review & Merge (human, manual)

Review the PR — evidence packet provides confidence without running anything locally. Merge. CI deploys to Azure via existing pipeline with production environment approval gate.

### Circuit Breakers

- Max 5 ralph iterations (configurable per task)
- If tests fail 3 consecutive cycles on the same issue, stop and surface the blocker
- If coverage drops after implementation cycle, force test-writing cycle before continuing
- If structural tests fail, stop — architectural violation needs human guidance

## Deliverables by Phase

### Phase 1: Context & Documentation

| Deliverable | Type |
|---|---|
| Restructured CLAUDE.md (~80 lines) | Doc refactor |
| `docs/architecture/overview.md` | New doc |
| `docs/architecture/backend-patterns.md` | New doc |
| `docs/architecture/frontend-patterns.md` | New doc |
| `docs/architecture/database.md` | New doc |
| `docs/golden-principles.md` | New doc |
| `docs/testing-standards.md` | New doc |
| `docs/contracts/api-response-shapes.md` | New doc |
| `docs/contracts/enum-values.md` | New doc |

### Phase 2: Quality Gates

| Deliverable | Type |
|---|---|
| 6 hookify rules | Hook config |
| `backend/tests/test_architecture.py` | Structural test |
| `backend/tests/test_conventions.py` | Structural test |
| `backend/tests/test_api_contracts.py` | Contract test |
| `frontend/src/__tests__/test_structure.ts` | Structural test |
| Self-review skill | New skill |

### Phase 3: Testing Harness

| Deliverable | Type |
|---|---|
| `backend/tests/contracts/` directory + fixtures | Test infrastructure |
| Visual regression setup (playwright config, baseline dir, diff util) | Config + utility |
| Test evidence collector script | Script |
| Frontend structural test | Test |

### Phase 4: Orchestration Loop

| Deliverable | Type |
|---|---|
| Beads initialization for meridian | Config |
| `task-runner` skill | New skill |
| `task-lifecycle` skill | New skill |
| Updated `ralph-loop` skill | Skill modification |
| Updated `worktree-task-start` skill | Skill modification |
| Updated `worktree-task-finish` skill | Skill modification |

## References

- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)
- [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
- [OpenAI: Unlocking the Codex Harness](https://openai.com/index/unlocking-the-codex-harness/)
