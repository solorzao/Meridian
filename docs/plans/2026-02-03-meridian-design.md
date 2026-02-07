# Meridian - Design Document

> **Tagline:** AI-powered trading journal & research assistant

**Date:** 2026-02-03
**Status:** Approved for implementation

---

## Overview

Meridian is a SaaS platform for retail traders that combines:
1. **Trading Journal** - Rich trade logging with strategy tags, thesis capture, and performance tracking
2. **Analytics Dashboards** - Performance metrics, strategy breakdowns, P&L visualization
3. **AI Agents** - Personalized screening, position analysis, and coaching powered by Semantic Kernel

---

## Architecture

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USERS                                          │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Azure Front Door (CDN)   │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Next.js App    │    │   .NET API      │    │  Web PubSub     │
│  (Frontend)     │    │   (Backend)     │    │  (Real-time)    │
│                 │    │                 │    │                 │
│  • Dashboard    │◄──►│  • Auth         │◄──►│  • Agent chat   │
│  • Journal UI   │    │  • Trade CRUD   │    │  • Notifications│
│  • Agent chat   │    │  • Semantic     │    │                 │
│                 │    │    Kernel       │    │                 │
└─────────────────┘    │  • Hangfire     │    └─────────────────┘
                       └────────┬────────┘
        Azure Container Apps    │
                       ┌────────┼────────┐
                       ▼        ▼        ▼
              ┌─────────┐ ┌──────────┐ ┌─────────────┐
              │Azure SQL│ │Cosmos DB │ │Python Svc   │
              │         │ │          │ │             │
              │• Users  │ │• Chat    │ │• Indicators │
              │• Trades │ │• Agent   │ │• Market data│
              │• Billing│ │  memory  │ │• Analytics  │
              └─────────┘ └──────────┘ └─────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js (React), TypeScript, Tailwind, shadcn/ui |
| Backend API | .NET 9, ASP.NET Core, Semantic Kernel |
| Analytics Service | Python, FastAPI, pandas, yfinance |
| Databases | Azure SQL (structured), Cosmos DB (flexible) |
| Cache | Azure Cache for Redis (optional, can start without) |
| Auth | Azure AD B2C |
| Real-time | Azure Web PubSub |
| AI | Azure AI Foundry (GPT-5-mini, text-embedding-3) |
| Background Jobs | Hangfire |
| Billing | Stripe |
| Hosting | Azure Container Apps |
| CI/CD | GitHub Actions |

---

## Data Model

### Azure SQL Tables

#### Users
```sql
CREATE TABLE Users (
    id UNIQUEIDENTIFIER PRIMARY KEY,
    azure_ad_b2c_id NVARCHAR(255) UNIQUE,
    email NVARCHAR(255),
    display_name NVARCHAR(255),
    subscription_tier NVARCHAR(20), -- 'free', 'premium'
    stripe_customer_id NVARCHAR(255) NULL,
    created_at DATETIME2,
    updated_at DATETIME2
);
```

#### Trades
```sql
CREATE TABLE Trades (
    id UNIQUEIDENTIFIER PRIMARY KEY,
    user_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Users(id),
    ticker NVARCHAR(20),
    direction NVARCHAR(10), -- 'long', 'short'
    entry_date DATETIME2,
    entry_price DECIMAL(18,4),
    exit_date DATETIME2 NULL,
    exit_price DECIMAL(18,4) NULL,
    position_size DECIMAL(18,4),
    stop_loss DECIMAL(18,4) NULL,
    take_profit DECIMAL(18,4) NULL,
    pnl DECIMAL(18,4) NULL,
    pnl_percent DECIMAL(18,4) NULL,
    status NVARCHAR(20), -- 'open', 'closed', 'cancelled'
    thesis NVARCHAR(MAX),
    emotional_state NVARCHAR(100),
    market_conditions NVARCHAR(255),
    notes NVARCHAR(MAX),
    created_at DATETIME2,
    updated_at DATETIME2
);
```

#### Strategies
```sql
CREATE TABLE Strategies (
    id UNIQUEIDENTIFIER PRIMARY KEY,
    user_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Users(id),
    name NVARCHAR(100),
    description NVARCHAR(MAX),
    source NVARCHAR(20), -- 'user', 'ai'
    created_at DATETIME2
);
```

#### TradeStrategyTags
```sql
CREATE TABLE TradeStrategyTags (
    trade_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Trades(id),
    strategy_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Strategies(id),
    source NVARCHAR(20), -- 'user', 'ai'
    PRIMARY KEY (trade_id, strategy_id)
);
```

#### TradeScreenshots
```sql
CREATE TABLE TradeScreenshots (
    id UNIQUEIDENTIFIER PRIMARY KEY,
    trade_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Trades(id),
    blob_url NVARCHAR(500),
    caption NVARCHAR(255),
    uploaded_at DATETIME2
);
```

#### TradeEmbeddings
```sql
CREATE TABLE TradeEmbeddings (
    trade_id UNIQUEIDENTIFIER PRIMARY KEY FOREIGN KEY REFERENCES Trades(id),
    embedding VARBINARY(MAX), -- or use Azure SQL vector preview
    content_hash NVARCHAR(64),
    model_version NVARCHAR(50)
);
```

### Cosmos DB Containers

#### conversations (partitioned by userId)
```json
{
  "id": "conv_abc123",
  "userId": "user_xyz",
  "agentType": "screener",
  "title": "Tech momentum plays",
  "createdAt": "2026-02-03T10:00:00Z",
  "updatedAt": "2026-02-03T10:15:00Z",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Find me stocks breaking out with volume",
      "timestamp": "2026-02-03T10:00:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "Based on your preferences, I found 3 candidates...",
      "timestamp": "2026-02-03T10:00:05Z",
      "metadata": {
        "tokensUsed": 1250,
        "model": "gpt-5-mini",
        "toolsUsed": ["market_scanner", "trade_history_lookup"]
      }
    }
  ]
}
```

#### agent_configs (partitioned by userId)
```json
{
  "id": "screener_abc123",
  "userId": "user_xyz",
  "agentType": "screener",
  "name": "Gap Scanner",
  "icon": "trending_up",
  "configType": "manual",
  "criteria": {
    "gapPercent": { "min": 3 },
    "volumeRatio": { "min": 2.0 },
    "sectors": ["technology"],
    "marketCapMin": 1000000000
  },
  "schedule": {
    "enabled": true,
    "frequency": "daily",
    "time": "07:00",
    "timezone": "America/New_York"
  },
  "createdAt": "2026-02-01T00:00:00Z"
}
```

#### user_profiles (partitioned by userId)
```json
{
  "id": "profile_user_xyz",
  "userId": "user_xyz",
  "tradingProfile": {
    "summary": "Momentum trader focusing on tech stocks. Average hold 3-5 days. Tends to exit winners early.",
    "preferredStrategies": ["momentum_breakout", "gap_and_go"],
    "avgHoldDays": 4.2,
    "winRate": 0.58,
    "profitFactor": 1.85,
    "weaknesses": ["exits_winners_early", "revenge_trading_after_loss"],
    "generatedAt": "2026-02-01T00:00:00Z"
  }
}
```

---

## AI Agent Architecture

### Agent Types

| Agent | Purpose | Availability |
|-------|---------|--------------|
| **Analyst** | Monitors open positions, provides exit suggestions, risk alerts | All users |
| **Coach** | Weekly performance reviews, pattern detection, behavioral feedback | All users |
| **Screener** (custom) | Scans market for setups matching user criteria | Free: 1, Premium: 3 |

### Screener Configuration Types

| Type | Description |
|------|-------------|
| **Manual** | User defines specific criteria (sectors, indicators, price ranges) |
| **Strategy-Based** | User picks one of their strategies; agent finds matching setups |
| **Auto-Learned** | Agent analyzes user's most profitable trades and creates criteria automatically |

### Semantic Kernel Plugins

| Plugin | Functions |
|--------|-----------|
| **MarketDataPlugin** | `get_quote`, `get_ohlcv`, `scan_universe` |
| **TradeHistoryPlugin** | `search_similar_trades`, `get_strategy_performance`, `get_open_positions` |
| **TechnicalAnalysisPlugin** | `calculate_indicators`, `detect_patterns` |
| **UserProfilePlugin** | `get_trading_profile`, `get_weaknesses` |

### Agent Personalization

Two-pronged approach:
1. **RAG** - Embed all trades/theses, retrieve relevant context for specific lookups
2. **System Prompt** - Periodically summarize user's patterns into personalized system prompt

---

## Python Analytics Service

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/indicators` | POST | Calculate technical indicators for a ticker |
| `/screen` | POST | Screen universe against criteria |
| `/analyze-trade` | POST | Analyze a trade setup |
| `/performance-stats` | POST | Calculate performance metrics |
| `/derive-criteria` | POST | Generate screening criteria from winning trades |
| `/market-data/{ticker}` | GET | Fetch OHLCV data |
| `/quote/{ticker}` | GET | Get current quote |

### Key Libraries

- FastAPI
- pandas, numpy
- yfinance (free), polygon-api-client (premium)
- pandas-ta (technical indicators)
- quantstats (performance metrics)

---

## Subscription Tiers

| Feature | Free | Premium |
|---------|------|---------|
| Trading Journal | Unlimited trades | Unlimited trades |
| Performance Dashboard | Basic metrics | Advanced analytics |
| AI Feedback | 5 analyses/month | Unlimited |
| Screener Agents | 1 (manual only) | 3 (any type) |
| Market Data | 15-min delayed | Real-time |
| Strategy Tags | User-defined | User + AI-suggested |
| Auto-Learned Screeners | No | Yes |

---

## Infrastructure

### Azure Resources

| Resource | Tier | Est. Cost (idle) |
|----------|------|------------------|
| Container Apps | Consumption | ~$0-5/mo |
| Azure SQL | Basic | $5/mo |
| Cosmos DB | Serverless | ~$1-2/mo |
| Web PubSub | Free | $0 |
| Blob Storage | Hot | <$1/mo |
| Azure AD B2C | Free (50k MAU) | $0 |
| Azure OpenAI | Pay-per-use | $0 idle |
| **Total Baseline** | | **~$10-15/mo** |

### Environments

- **Dev** - Development and testing
- **Prod** - Production

---

## Repository Structure

```
meridian/
├── .github/
│   └── workflows/
│       ├── frontend.yml
│       ├── backend.yml
│       ├── python-service.yml
│       └── infrastructure.yml
│
├── frontend/                    # Next.js app
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── Dockerfile
│
├── backend/                     # .NET solution
│   ├── src/
│   │   ├── Meridian.Api/
│   │   ├── Meridian.Core/
│   │   ├── Meridian.Infrastructure/
│   │   ├── Meridian.Agents/
│   │   └── Meridian.Jobs/
│   ├── tests/
│   ├── Meridian.sln
│   └── Dockerfile
│
├── python-service/              # FastAPI analytics
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── infrastructure/              # Azure IaC
│   ├── main.bicep
│   ├── modules/
│   └── parameters/
│       ├── dev.json
│       └── prod.json
│
├── docs/
│   └── plans/
│
├── .gitignore
└── README.md
```

---

## CI/CD

GitHub Actions with path-based triggers:
- `frontend/**` changes → Build & deploy Next.js
- `backend/**` changes → Test & deploy .NET API
- `python-service/**` changes → Test & deploy Python service
- `infrastructure/**` changes → Manual trigger for Bicep

Branch strategy: `feature/*` → PR → `main` → auto-deploy to prod

---

## Next Steps

1. Initialize repository with monorepo structure
2. Set up Azure infrastructure (Bicep)
3. Scaffold .NET backend with Semantic Kernel
4. Scaffold Python analytics service
5. Scaffold Next.js frontend
6. Implement auth flow (Azure AD B2C)
7. Build trading journal CRUD
8. Build analytics dashboard
9. Implement AI agents
10. Add Stripe billing
11. Polish and launch

---

*Document generated during brainstorming session on 2026-02-03*
