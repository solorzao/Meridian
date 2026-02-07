# Meridian Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build Meridian, an AI-powered trading journal and research assistant SaaS platform with personalized screening agents.

**Architecture:** Monorepo with three services: Next.js frontend, .NET API with Semantic Kernel agents, Python analytics service. Azure Container Apps hosting with Azure SQL + Cosmos DB persistence. Stripe billing, Azure AD B2C auth.

**Tech Stack:** Next.js 15, .NET 9, Semantic Kernel, Python 3.12, FastAPI, Azure SQL, Cosmos DB, Azure AD B2C, Azure Web PubSub, Hangfire, Stripe

**Reference Design:** See `docs/plans/2026-02-03-meridian-design.md` for full architecture details.

---

## Phase 1: Repository & Infrastructure Setup

### Task 1.1: Initialize Monorepo

**Files:**
- Create: `meridian/.gitignore`
- Create: `meridian/README.md`
- Create: `meridian/.github/dependabot.yml`

**Step 1: Create repository directory**

```bash
mkdir -p C:/Users/Oliver/source/repos/meridian
cd C:/Users/Oliver/source/repos/meridian
git init
```

**Step 2: Create .gitignore**

```gitignore
# .gitignore

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.*
!.env.example

# Frontend
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.turbo/

# Backend (.NET)
backend/**/bin/
backend/**/obj/
backend/**/*.user
backend/**/*.suo
backend/.vs/

# Python
python-service/__pycache__/
python-service/*.pyc
python-service/.venv/
python-service/venv/
python-service/.pytest_cache/
python-service/.ruff_cache/

# Infrastructure
infrastructure/.terraform/
infrastructure/*.tfstate*
infrastructure/.bicep/

# Logs
*.log
logs/

# Test coverage
coverage/
*.coverage
htmlcov/
```

**Step 3: Create README.md**

```markdown
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
```

**Step 4: Create dependabot.yml**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "nuget"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "pip"
    directory: "/python-service"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

**Step 5: Commit**

```bash
git add .
git commit -m "chore: initialize meridian monorepo"
```

---

### Task 1.2: Create Directory Structure

**Files:**
- Create: `meridian/frontend/.gitkeep`
- Create: `meridian/backend/.gitkeep`
- Create: `meridian/python-service/.gitkeep`
- Create: `meridian/infrastructure/.gitkeep`
- Create: `meridian/docs/plans/.gitkeep`

**Step 1: Create directory structure**

```bash
cd C:/Users/Oliver/source/repos/meridian
mkdir -p frontend backend python-service infrastructure docs/plans .github/workflows
touch frontend/.gitkeep backend/.gitkeep python-service/.gitkeep infrastructure/.gitkeep docs/plans/.gitkeep
```

**Step 2: Copy design document**

```bash
cp C:/Users/Oliver/source/repos/docs/plans/2026-02-03-meridian-design.md docs/plans/
```

**Step 3: Commit**

```bash
git add .
git commit -m "chore: add directory structure and design doc"
```

---

### Task 1.3: Azure Infrastructure - Bicep Modules

**Files:**
- Create: `infrastructure/main.bicep`
- Create: `infrastructure/modules/container-apps.bicep`
- Create: `infrastructure/modules/sql.bicep`
- Create: `infrastructure/modules/cosmos.bicep`
- Create: `infrastructure/modules/keyvault.bicep`
- Create: `infrastructure/parameters/dev.bicepparam`
- Create: `infrastructure/parameters/prod.bicepparam`

**Step 1: Create main.bicep**

```bicep
// infrastructure/main.bicep
targetScope = 'subscription'

@description('Environment name')
@allowed(['dev', 'prod'])
param environment string

@description('Azure region')
param location string = 'eastus2'

@description('SQL admin password')
@secure()
param sqlAdminPassword string

var resourceGroupName = 'meridian-${environment}'
var tags = {
  project: 'meridian'
  environment: environment
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  scope: rg
  params: {
    location: location
    environment: environment
    tags: tags
  }
}

module sql 'modules/sql.bicep' = {
  name: 'sql'
  scope: rg
  params: {
    location: location
    environment: environment
    adminPassword: sqlAdminPassword
    keyVaultName: keyVault.outputs.keyVaultName
    tags: tags
  }
}

module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmos'
  scope: rg
  params: {
    location: location
    environment: environment
    keyVaultName: keyVault.outputs.keyVaultName
    tags: tags
  }
}

module containerApps 'modules/container-apps.bicep' = {
  name: 'container-apps'
  scope: rg
  params: {
    location: location
    environment: environment
    tags: tags
  }
}

output resourceGroupName string = rg.name
output containerAppsEnvironmentId string = containerApps.outputs.environmentId
```

**Step 2: Create modules/keyvault.bicep**

```bicep
// infrastructure/modules/keyvault.bicep
param location string
param environment string
param tags object

var keyVaultName = 'kv-meridian-${environment}'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
```

**Step 3: Create modules/sql.bicep**

```bicep
// infrastructure/modules/sql.bicep
param location string
param environment string
param tags object
param keyVaultName string
@secure()
param adminPassword string

var serverName = 'sql-meridian-${environment}'
var databaseName = 'meridian'

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: serverName
  location: location
  tags: tags
  properties: {
    administratorLogin: 'meridianadmin'
    administratorLoginPassword: adminPassword
    version: '12.0'
    minimalTlsVersion: '1.2'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: databaseName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }
}

resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource sqlConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'SqlConnectionString'
  properties: {
    value: 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Initial Catalog=${databaseName};Persist Security Info=False;User ID=meridianadmin;Password=${adminPassword};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
  }
}

output serverName string = sqlServer.name
output databaseName string = sqlDatabase.name
output fullyQualifiedDomainName string = sqlServer.properties.fullyQualifiedDomainName
```

**Step 4: Create modules/cosmos.bicep**

```bicep
// infrastructure/modules/cosmos.bicep
param location string
param environment string
param tags object
param keyVaultName string

var accountName = 'cosmos-meridian-${environment}'

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-02-15-preview' = {
  name: accountName
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-02-15-preview' = {
  parent: cosmosAccount
  name: 'meridian'
  properties: {
    resource: {
      id: 'meridian'
    }
  }
}

resource conversationsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-02-15-preview' = {
  parent: database
  name: 'conversations'
  properties: {
    resource: {
      id: 'conversations'
      partitionKey: {
        paths: ['/userId']
        kind: 'Hash'
      }
    }
  }
}

resource agentConfigsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-02-15-preview' = {
  parent: database
  name: 'agent_configs'
  properties: {
    resource: {
      id: 'agent_configs'
      partitionKey: {
        paths: ['/userId']
        kind: 'Hash'
      }
    }
  }
}

resource userProfilesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-02-15-preview' = {
  parent: database
  name: 'user_profiles'
  properties: {
    resource: {
      id: 'user_profiles'
      partitionKey: {
        paths: ['/userId']
        kind: 'Hash'
      }
    }
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource cosmosConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'CosmosConnectionString'
  properties: {
    value: cosmosAccount.listConnectionStrings().connectionStrings[0].connectionString
  }
}

output accountName string = cosmosAccount.name
output endpoint string = cosmosAccount.properties.documentEndpoint
```

**Step 5: Create modules/container-apps.bicep**

```bicep
// infrastructure/modules/container-apps.bicep
param location string
param environment string
param tags object

var environmentName = 'cae-meridian-${environment}'
var logAnalyticsName = 'log-meridian-${environment}'
var registryName = 'acrmeridian${environment}'

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

output environmentId string = containerAppsEnvironment.id
output environmentName string = containerAppsEnvironment.name
output registryName string = containerRegistry.name
output registryLoginServer string = containerRegistry.properties.loginServer
```

**Step 6: Create parameters/dev.bicepparam**

```bicep
// infrastructure/parameters/dev.bicepparam
using '../main.bicep'

param environment = 'dev'
param location = 'eastus2'
param sqlAdminPassword = '' // Set via CLI or pipeline
```

**Step 7: Create parameters/prod.bicepparam**

```bicep
// infrastructure/parameters/prod.bicepparam
using '../main.bicep'

param environment = 'prod'
param location = 'eastus2'
param sqlAdminPassword = '' // Set via CLI or pipeline
```

**Step 8: Commit**

```bash
git add infrastructure/
git commit -m "infra: add Azure Bicep modules for core resources"
```

---

## Phase 2: Python Analytics Service

### Task 2.1: Initialize Python Project

**Files:**
- Create: `python-service/pyproject.toml`
- Create: `python-service/app/__init__.py`
- Create: `python-service/app/main.py`
- Create: `python-service/app/config.py`
- Create: `python-service/tests/__init__.py`

**Step 1: Create pyproject.toml**

```toml
# python-service/pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "meridian-analytics"
version = "0.1.0"
description = "Meridian analytics and market data service"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "pandas>=2.2.0",
    "numpy>=2.0.0",
    "yfinance>=0.2.48",
    "pandas-ta>=0.3.14b0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
]
premium = [
    "polygon-api-client>=1.14.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
```

**Step 2: Create app/config.py**

```python
# python-service/app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    app_name: str = "Meridian Analytics"
    debug: bool = False

    # Market data
    polygon_api_key: str | None = None

    # Cache settings (for future Redis integration)
    cache_ttl_quotes: int = 60  # 1 minute for premium
    cache_ttl_quotes_free: int = 900  # 15 minutes for free tier

    class Config:
        env_file = ".env"


settings = Settings()
```

**Step 3: Create app/main.py**

```python
# python-service/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "meridian-analytics"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Meridian Analytics Service", "version": "0.1.0"}
```

**Step 4: Create __init__.py files**

```python
# python-service/app/__init__.py
```

```python
# python-service/tests/__init__.py
```

**Step 5: Create test for health check**

```python
# python-service/tests/test_main.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Meridian" in response.json()["message"]
```

**Step 6: Run tests to verify**

```bash
cd C:/Users/Oliver/source/repos/meridian/python-service
uv venv
uv pip install -e ".[dev]"
uv run pytest tests/ -v
```

Expected: PASS

**Step 7: Commit**

```bash
git add python-service/
git commit -m "feat(python): initialize FastAPI analytics service"
```

---

### Task 2.2: Market Data Service

**Files:**
- Create: `python-service/app/services/__init__.py`
- Create: `python-service/app/services/market_data.py`
- Create: `python-service/app/models/__init__.py`
- Create: `python-service/app/models/schemas.py`
- Create: `python-service/tests/test_market_data.py`

**Step 1: Create models/schemas.py**

```python
# python-service/app/models/schemas.py
from datetime import datetime
from pydantic import BaseModel


class OHLCVBar(BaseModel):
    """Single OHLCV bar."""

    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class OHLCVResponse(BaseModel):
    """OHLCV data response."""

    ticker: str
    bars: list[OHLCVBar]
    period: str
    interval: str


class QuoteResponse(BaseModel):
    """Current quote response."""

    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime


class MarketDataError(BaseModel):
    """Error response for market data."""

    error: str
    ticker: str
```

**Step 2: Create services/market_data.py**

```python
# python-service/app/services/market_data.py
import yfinance as yf
import pandas as pd
from datetime import datetime

from app.models.schemas import OHLCVBar, OHLCVResponse, QuoteResponse


class MarketDataService:
    """Service for fetching market data."""

    def get_ohlcv(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> OHLCVResponse:
        """
        Fetch OHLCV data for a ticker.

        Args:
            ticker: Stock symbol (e.g., "AAPL")
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            OHLCVResponse with bars
        """
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        bars = []
        for idx, row in df.iterrows():
            bars.append(
                OHLCVBar(
                    date=idx.to_pydatetime(),
                    open=round(row["Open"], 4),
                    high=round(row["High"], 4),
                    low=round(row["Low"], 4),
                    close=round(row["Close"], 4),
                    volume=int(row["Volume"]),
                )
            )

        return OHLCVResponse(
            ticker=ticker.upper(),
            bars=bars,
            period=period,
            interval=interval,
        )

    def get_quote(self, ticker: str) -> QuoteResponse:
        """
        Get current quote for a ticker.

        Args:
            ticker: Stock symbol

        Returns:
            QuoteResponse with current price and change
        """
        stock = yf.Ticker(ticker)
        info = stock.fast_info

        price = info.last_price
        prev_close = info.previous_close
        change = price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close else 0

        return QuoteResponse(
            ticker=ticker.upper(),
            price=round(price, 4),
            change=round(change, 4),
            change_percent=round(change_percent, 2),
            volume=int(info.last_volume or 0),
            timestamp=datetime.now(),
        )


# Singleton instance
market_data_service = MarketDataService()
```

**Step 3: Create services/__init__.py**

```python
# python-service/app/services/__init__.py
from app.services.market_data import market_data_service

__all__ = ["market_data_service"]
```

**Step 4: Create models/__init__.py**

```python
# python-service/app/models/__init__.py
from app.models.schemas import (
    OHLCVBar,
    OHLCVResponse,
    QuoteResponse,
    MarketDataError,
)

__all__ = ["OHLCVBar", "OHLCVResponse", "QuoteResponse", "MarketDataError"]
```

**Step 5: Create tests/test_market_data.py**

```python
# python-service/tests/test_market_data.py
import pytest
from app.services.market_data import MarketDataService


@pytest.fixture
def service():
    return MarketDataService()


def test_get_ohlcv_returns_data(service):
    """Test that OHLCV data is returned for valid ticker."""
    result = service.get_ohlcv("AAPL", period="5d", interval="1d")

    assert result.ticker == "AAPL"
    assert len(result.bars) > 0
    assert result.bars[0].close > 0


def test_get_ohlcv_invalid_ticker(service):
    """Test that invalid ticker raises error."""
    with pytest.raises(ValueError, match="No data"):
        service.get_ohlcv("INVALIDTICKER123")


def test_get_quote_returns_price(service):
    """Test that quote returns current price."""
    result = service.get_quote("MSFT")

    assert result.ticker == "MSFT"
    assert result.price > 0
    assert result.timestamp is not None


def test_ohlcv_bar_has_required_fields(service):
    """Test that OHLCV bars have all required fields."""
    result = service.get_ohlcv("GOOGL", period="5d")

    bar = result.bars[0]
    assert bar.open > 0
    assert bar.high >= bar.low
    assert bar.close > 0
    assert bar.volume >= 0
```

**Step 6: Run tests**

```bash
cd C:/Users/Oliver/source/repos/meridian/python-service
uv run pytest tests/test_market_data.py -v
```

Expected: PASS (may be slow due to API calls)

**Step 7: Commit**

```bash
git add python-service/
git commit -m "feat(python): add market data service with yfinance"
```

---

### Task 2.3: Technical Indicators Service

**Files:**
- Create: `python-service/app/services/indicators.py`
- Create: `python-service/app/models/indicator_schemas.py`
- Create: `python-service/tests/test_indicators.py`

**Step 1: Create models/indicator_schemas.py**

```python
# python-service/app/models/indicator_schemas.py
from pydantic import BaseModel


class IndicatorRequest(BaseModel):
    """Request to calculate indicators."""

    ticker: str
    period: str = "1y"
    interval: str = "1d"
    indicators: list[str] = ["sma_20", "sma_50", "rsi_14", "macd"]


class IndicatorBar(BaseModel):
    """OHLCV bar with indicator values."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    indicators: dict[str, float | None]


class IndicatorResponse(BaseModel):
    """Response with OHLCV and indicator data."""

    ticker: str
    bars: list[IndicatorBar]
    indicators_calculated: list[str]
```

**Step 2: Create services/indicators.py**

```python
# python-service/app/services/indicators.py
import pandas as pd
import pandas_ta as ta

from app.services.market_data import market_data_service
from app.models.indicator_schemas import IndicatorBar, IndicatorResponse


class IndicatorService:
    """Service for calculating technical indicators."""

    # Map of indicator names to pandas_ta functions
    INDICATOR_MAP = {
        "sma_20": lambda df: ta.sma(df["close"], length=20),
        "sma_50": lambda df: ta.sma(df["close"], length=50),
        "sma_200": lambda df: ta.sma(df["close"], length=200),
        "ema_12": lambda df: ta.ema(df["close"], length=12),
        "ema_26": lambda df: ta.ema(df["close"], length=26),
        "rsi_14": lambda df: ta.rsi(df["close"], length=14),
        "macd": lambda df: ta.macd(df["close"])["MACD_12_26_9"],
        "macd_signal": lambda df: ta.macd(df["close"])["MACDs_12_26_9"],
        "macd_hist": lambda df: ta.macd(df["close"])["MACDh_12_26_9"],
        "bbands_upper": lambda df: ta.bbands(df["close"])["BBU_5_2.0"],
        "bbands_lower": lambda df: ta.bbands(df["close"])["BBL_5_2.0"],
        "bbands_mid": lambda df: ta.bbands(df["close"])["BBM_5_2.0"],
        "atr_14": lambda df: ta.atr(df["high"], df["low"], df["close"], length=14),
        "volume_sma_20": lambda df: ta.sma(df["volume"], length=20),
    }

    def calculate(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        indicators: list[str] | None = None,
    ) -> IndicatorResponse:
        """
        Calculate technical indicators for a ticker.

        Args:
            ticker: Stock symbol
            period: Data period
            interval: Data interval
            indicators: List of indicator names to calculate

        Returns:
            IndicatorResponse with OHLCV and indicator values
        """
        if indicators is None:
            indicators = ["sma_20", "sma_50", "rsi_14", "macd"]

        # Fetch OHLCV data
        ohlcv = market_data_service.get_ohlcv(ticker, period, interval)

        # Convert to DataFrame for pandas_ta
        df = pd.DataFrame([bar.model_dump() for bar in ohlcv.bars])
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        # Calculate requested indicators
        calculated = []
        for ind_name in indicators:
            if ind_name in self.INDICATOR_MAP:
                try:
                    df[ind_name] = self.INDICATOR_MAP[ind_name](df)
                    calculated.append(ind_name)
                except Exception:
                    df[ind_name] = None
            else:
                df[ind_name] = None

        # Build response
        bars = []
        for idx, row in df.iterrows():
            ind_values = {}
            for ind_name in indicators:
                val = row.get(ind_name)
                ind_values[ind_name] = round(val, 4) if pd.notna(val) else None

            bars.append(
                IndicatorBar(
                    date=idx.strftime("%Y-%m-%d"),
                    open=round(row["open"], 4),
                    high=round(row["high"], 4),
                    low=round(row["low"], 4),
                    close=round(row["close"], 4),
                    volume=int(row["volume"]),
                    indicators=ind_values,
                )
            )

        return IndicatorResponse(
            ticker=ticker.upper(),
            bars=bars,
            indicators_calculated=calculated,
        )


# Singleton instance
indicator_service = IndicatorService()
```

**Step 3: Update services/__init__.py**

```python
# python-service/app/services/__init__.py
from app.services.market_data import market_data_service
from app.services.indicators import indicator_service

__all__ = ["market_data_service", "indicator_service"]
```

**Step 4: Create tests/test_indicators.py**

```python
# python-service/tests/test_indicators.py
import pytest
from app.services.indicators import IndicatorService


@pytest.fixture
def service():
    return IndicatorService()


def test_calculate_default_indicators(service):
    """Test calculating default indicators."""
    result = service.calculate("AAPL", period="3mo")

    assert result.ticker == "AAPL"
    assert len(result.bars) > 0
    assert "sma_20" in result.indicators_calculated
    assert "rsi_14" in result.indicators_calculated


def test_calculate_specific_indicators(service):
    """Test calculating specific indicators."""
    result = service.calculate(
        "MSFT",
        period="3mo",
        indicators=["sma_50", "ema_12", "atr_14"],
    )

    assert "sma_50" in result.indicators_calculated
    assert "ema_12" in result.indicators_calculated
    assert "atr_14" in result.indicators_calculated


def test_indicator_values_present_after_warmup(service):
    """Test that indicator values are present after warmup period."""
    result = service.calculate("GOOGL", period="3mo", indicators=["sma_20"])

    # After 20+ bars, SMA should have values
    bars_with_sma = [b for b in result.bars if b.indicators.get("sma_20") is not None]
    assert len(bars_with_sma) > 0


def test_rsi_in_valid_range(service):
    """Test that RSI values are between 0 and 100."""
    result = service.calculate("NVDA", period="3mo", indicators=["rsi_14"])

    for bar in result.bars:
        rsi = bar.indicators.get("rsi_14")
        if rsi is not None:
            assert 0 <= rsi <= 100
```

**Step 5: Run tests**

```bash
cd C:/Users/Oliver/source/repos/meridian/python-service
uv run pytest tests/test_indicators.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add python-service/
git commit -m "feat(python): add technical indicators service"
```

---

### Task 2.4: Screening Service

**Files:**
- Create: `python-service/app/services/screener.py`
- Create: `python-service/app/models/screener_schemas.py`
- Create: `python-service/tests/test_screener.py`

**Step 1: Create models/screener_schemas.py**

```python
# python-service/app/models/screener_schemas.py
from pydantic import BaseModel
from typing import Literal


class RangeCriteria(BaseModel):
    """Numeric range criteria."""

    min: float | None = None
    max: float | None = None


class ScreenerCriteria(BaseModel):
    """Criteria for screening stocks."""

    # Price criteria
    price: RangeCriteria | None = None
    gap_percent: RangeCriteria | None = None

    # Volume criteria
    volume_ratio: RangeCriteria | None = None  # vs 20-day avg
    min_volume: int | None = None

    # Technical criteria
    rsi_14: RangeCriteria | None = None
    above_sma_20: bool | None = None
    above_sma_50: bool | None = None
    above_sma_200: bool | None = None

    # Filters
    sectors: list[str] | None = None
    market_cap_min: int | None = None
    market_cap_max: int | None = None


class ScreenerRequest(BaseModel):
    """Request to run screener."""

    criteria: ScreenerCriteria
    universe: Literal["sp500", "nasdaq100", "custom"] = "sp500"
    custom_tickers: list[str] | None = None
    limit: int = 20


class ScreenerMatch(BaseModel):
    """A stock matching screener criteria."""

    ticker: str
    name: str | None = None
    price: float
    change_percent: float
    volume: int
    volume_ratio: float | None = None
    rsi_14: float | None = None
    gap_percent: float | None = None
    sector: str | None = None
    market_cap: int | None = None


class ScreenerResponse(BaseModel):
    """Screener results."""

    matches: list[ScreenerMatch]
    total_scanned: int
    criteria_summary: str
```

**Step 2: Create services/screener.py**

```python
# python-service/app/services/screener.py
import yfinance as yf
import pandas as pd

from app.models.screener_schemas import (
    ScreenerCriteria,
    ScreenerMatch,
    ScreenerResponse,
)
from app.services.indicators import indicator_service


class ScreenerService:
    """Service for screening stocks against criteria."""

    # Sample universes (in production, fetch dynamically or from DB)
    SP500_SAMPLE = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
        "UNH", "JNJ", "JPM", "V", "PG", "XOM", "HD", "CVX", "MA", "ABBV",
        "MRK", "PFE", "KO", "PEP", "COST", "TMO", "AVGO", "MCD", "WMT",
        "CSCO", "ACN", "ABT", "DHR", "LLY", "NEE", "VZ", "ADBE", "CRM",
    ]

    NASDAQ100_SAMPLE = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO",
        "ADBE", "COST", "CSCO", "PEP", "AMD", "NFLX", "INTC", "CMCSA",
        "INTU", "QCOM", "TXN", "AMGN", "AMAT", "BKNG", "ISRG", "MDLZ",
    ]

    def screen(
        self,
        criteria: ScreenerCriteria,
        universe: str = "sp500",
        custom_tickers: list[str] | None = None,
        limit: int = 20,
    ) -> ScreenerResponse:
        """
        Screen stocks against criteria.

        Args:
            criteria: Screening criteria
            universe: Stock universe to scan
            custom_tickers: Custom list of tickers (if universe="custom")
            limit: Max results to return

        Returns:
            ScreenerResponse with matching stocks
        """
        # Get universe
        if universe == "custom" and custom_tickers:
            tickers = custom_tickers
        elif universe == "nasdaq100":
            tickers = self.NASDAQ100_SAMPLE
        else:
            tickers = self.SP500_SAMPLE

        matches = []
        for ticker in tickers:
            try:
                match = self._evaluate_ticker(ticker, criteria)
                if match:
                    matches.append(match)
            except Exception:
                continue  # Skip tickers that error

            if len(matches) >= limit:
                break

        # Sort by volume ratio descending (most active first)
        matches.sort(key=lambda x: x.volume_ratio or 0, reverse=True)

        return ScreenerResponse(
            matches=matches[:limit],
            total_scanned=len(tickers),
            criteria_summary=self._summarize_criteria(criteria),
        )

    def _evaluate_ticker(
        self, ticker: str, criteria: ScreenerCriteria
    ) -> ScreenerMatch | None:
        """Evaluate a single ticker against criteria."""
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        hist = stock.history(period="5d")

        if hist.empty:
            return None

        price = info.last_price
        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else price
        change_pct = ((price - prev_close) / prev_close) * 100

        # Calculate volume ratio
        vol_avg = hist["Volume"].mean()
        vol_ratio = info.last_volume / vol_avg if vol_avg > 0 else 1.0

        # Calculate gap percent (open vs prev close)
        today_open = hist["Open"].iloc[-1]
        gap_pct = ((today_open - prev_close) / prev_close) * 100

        # Get RSI if needed
        rsi = None
        if criteria.rsi_14:
            try:
                ind_result = indicator_service.calculate(
                    ticker, period="1mo", indicators=["rsi_14"]
                )
                last_bar = ind_result.bars[-1] if ind_result.bars else None
                rsi = last_bar.indicators.get("rsi_14") if last_bar else None
            except Exception:
                pass

        # Apply criteria filters
        if criteria.price:
            if criteria.price.min and price < criteria.price.min:
                return None
            if criteria.price.max and price > criteria.price.max:
                return None

        if criteria.gap_percent:
            if criteria.gap_percent.min and gap_pct < criteria.gap_percent.min:
                return None
            if criteria.gap_percent.max and gap_pct > criteria.gap_percent.max:
                return None

        if criteria.volume_ratio:
            if criteria.volume_ratio.min and vol_ratio < criteria.volume_ratio.min:
                return None
            if criteria.volume_ratio.max and vol_ratio > criteria.volume_ratio.max:
                return None

        if criteria.min_volume and info.last_volume < criteria.min_volume:
            return None

        if criteria.rsi_14 and rsi:
            if criteria.rsi_14.min and rsi < criteria.rsi_14.min:
                return None
            if criteria.rsi_14.max and rsi > criteria.rsi_14.max:
                return None

        return ScreenerMatch(
            ticker=ticker,
            name=None,  # Would need full info call
            price=round(price, 2),
            change_percent=round(change_pct, 2),
            volume=int(info.last_volume or 0),
            volume_ratio=round(vol_ratio, 2),
            rsi_14=round(rsi, 2) if rsi else None,
            gap_percent=round(gap_pct, 2),
            sector=None,
            market_cap=None,
        )

    def _summarize_criteria(self, criteria: ScreenerCriteria) -> str:
        """Generate human-readable summary of criteria."""
        parts = []

        if criteria.price:
            if criteria.price.min and criteria.price.max:
                parts.append(f"price ${criteria.price.min}-${criteria.price.max}")
            elif criteria.price.min:
                parts.append(f"price > ${criteria.price.min}")
            elif criteria.price.max:
                parts.append(f"price < ${criteria.price.max}")

        if criteria.gap_percent and criteria.gap_percent.min:
            parts.append(f"gap > {criteria.gap_percent.min}%")

        if criteria.volume_ratio and criteria.volume_ratio.min:
            parts.append(f"volume > {criteria.volume_ratio.min}x avg")

        if criteria.rsi_14:
            if criteria.rsi_14.min and criteria.rsi_14.max:
                parts.append(f"RSI {criteria.rsi_14.min}-{criteria.rsi_14.max}")
            elif criteria.rsi_14.max:
                parts.append(f"RSI < {criteria.rsi_14.max} (oversold)")
            elif criteria.rsi_14.min:
                parts.append(f"RSI > {criteria.rsi_14.min}")

        return ", ".join(parts) if parts else "No specific criteria"


# Singleton instance
screener_service = ScreenerService()
```

**Step 3: Update services/__init__.py**

```python
# python-service/app/services/__init__.py
from app.services.market_data import market_data_service
from app.services.indicators import indicator_service
from app.services.screener import screener_service

__all__ = ["market_data_service", "indicator_service", "screener_service"]
```

**Step 4: Create tests/test_screener.py**

```python
# python-service/tests/test_screener.py
import pytest
from app.services.screener import ScreenerService
from app.models.screener_schemas import ScreenerCriteria, RangeCriteria


@pytest.fixture
def service():
    return ScreenerService()


def test_screen_returns_results(service):
    """Test that screening returns results."""
    criteria = ScreenerCriteria()  # No filters
    result = service.screen(criteria, limit=5)

    assert len(result.matches) > 0
    assert result.total_scanned > 0


def test_screen_with_volume_filter(service):
    """Test screening with volume ratio filter."""
    criteria = ScreenerCriteria(
        volume_ratio=RangeCriteria(min=1.0)  # Above average volume
    )
    result = service.screen(criteria, limit=10)

    for match in result.matches:
        if match.volume_ratio:
            assert match.volume_ratio >= 1.0


def test_screen_with_price_filter(service):
    """Test screening with price filter."""
    criteria = ScreenerCriteria(
        price=RangeCriteria(min=50, max=500)
    )
    result = service.screen(criteria, limit=10)

    for match in result.matches:
        assert 50 <= match.price <= 500


def test_screen_custom_universe(service):
    """Test screening with custom ticker list."""
    criteria = ScreenerCriteria()
    result = service.screen(
        criteria,
        universe="custom",
        custom_tickers=["AAPL", "MSFT", "GOOGL"],
        limit=3,
    )

    assert result.total_scanned == 3
    tickers = [m.ticker for m in result.matches]
    assert all(t in ["AAPL", "MSFT", "GOOGL"] for t in tickers)


def test_criteria_summary(service):
    """Test that criteria summary is generated."""
    criteria = ScreenerCriteria(
        gap_percent=RangeCriteria(min=2),
        volume_ratio=RangeCriteria(min=1.5),
    )
    result = service.screen(criteria, limit=5)

    assert "gap" in result.criteria_summary.lower()
    assert "volume" in result.criteria_summary.lower()
```

**Step 5: Run tests**

```bash
cd C:/Users/Oliver/source/repos/meridian/python-service
uv run pytest tests/test_screener.py -v
```

Expected: PASS (may be slow due to API calls)

**Step 6: Commit**

```bash
git add python-service/
git commit -m "feat(python): add stock screener service"
```

---

### Task 2.5: Performance Statistics Service

**Files:**
- Create: `python-service/app/services/stats.py`
- Create: `python-service/app/models/stats_schemas.py`
- Create: `python-service/tests/test_stats.py`

**Step 1: Create models/stats_schemas.py**

```python
# python-service/app/models/stats_schemas.py
from pydantic import BaseModel
from datetime import datetime


class TradeInput(BaseModel):
    """Trade data for statistics calculation."""

    id: str
    ticker: str
    direction: str  # "long" or "short"
    entry_date: datetime
    entry_price: float
    exit_date: datetime | None = None
    exit_price: float | None = None
    position_size: float
    pnl: float | None = None
    strategy_tags: list[str] = []


class PerformanceStats(BaseModel):
    """Overall performance statistics."""

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_hold_days: float
    expectancy: float


class StrategyStats(BaseModel):
    """Performance statistics for a single strategy."""

    strategy_name: str
    total_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    avg_pnl: float


class PerformanceResponse(BaseModel):
    """Full performance analysis response."""

    overall: PerformanceStats
    by_strategy: list[StrategyStats]
    by_ticker: dict[str, PerformanceStats]
    monthly_pnl: dict[str, float]  # "2026-01": 1234.56
```

**Step 2: Create services/stats.py**

```python
# python-service/app/services/stats.py
from collections import defaultdict
from datetime import datetime

from app.models.stats_schemas import (
    TradeInput,
    PerformanceStats,
    StrategyStats,
    PerformanceResponse,
)


class StatsService:
    """Service for calculating trading performance statistics."""

    def calculate(self, trades: list[TradeInput]) -> PerformanceResponse:
        """
        Calculate comprehensive performance statistics.

        Args:
            trades: List of closed trades

        Returns:
            PerformanceResponse with overall, by-strategy, and by-ticker stats
        """
        # Filter to closed trades with P&L
        closed = [t for t in trades if t.pnl is not None and t.exit_date is not None]

        if not closed:
            return self._empty_response()

        overall = self._calculate_stats(closed)
        by_strategy = self._calculate_by_strategy(closed)
        by_ticker = self._calculate_by_ticker(closed)
        monthly = self._calculate_monthly(closed)

        return PerformanceResponse(
            overall=overall,
            by_strategy=by_strategy,
            by_ticker=by_ticker,
            monthly_pnl=monthly,
        )

    def _calculate_stats(self, trades: list[TradeInput]) -> PerformanceStats:
        """Calculate stats for a list of trades."""
        if not trades:
            return self._empty_stats()

        pnls = [t.pnl for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0

        # Calculate hold days
        hold_days = []
        for t in trades:
            if t.exit_date and t.entry_date:
                days = (t.exit_date - t.entry_date).days
                hold_days.append(max(days, 1))

        avg_hold = sum(hold_days) / len(hold_days) if hold_days else 0

        win_rate = len(wins) / len(trades) if trades else 0
        avg_win = total_wins / len(wins) if wins else 0
        avg_loss = total_losses / len(losses) if losses else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

        return PerformanceStats(
            total_trades=len(trades),
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=round(win_rate, 4),
            profit_factor=round(profit_factor, 2),
            total_pnl=round(sum(pnls), 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            largest_win=round(max(wins), 2) if wins else 0,
            largest_loss=round(min(losses), 2) if losses else 0,
            avg_hold_days=round(avg_hold, 1),
            expectancy=round(expectancy, 2),
        )

    def _calculate_by_strategy(self, trades: list[TradeInput]) -> list[StrategyStats]:
        """Calculate stats grouped by strategy tag."""
        by_strategy = defaultdict(list)

        for t in trades:
            for tag in t.strategy_tags:
                by_strategy[tag].append(t)

        results = []
        for strategy_name, strategy_trades in by_strategy.items():
            pnls = [t.pnl for t in strategy_trades]
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p <= 0]

            total_wins = sum(wins) if wins else 0
            total_losses = abs(sum(losses)) if losses else 0

            results.append(
                StrategyStats(
                    strategy_name=strategy_name,
                    total_trades=len(strategy_trades),
                    win_rate=round(len(wins) / len(strategy_trades), 4),
                    profit_factor=round(
                        total_wins / total_losses if total_losses > 0 else 0, 2
                    ),
                    total_pnl=round(sum(pnls), 2),
                    avg_pnl=round(sum(pnls) / len(strategy_trades), 2),
                )
            )

        return sorted(results, key=lambda x: x.win_rate, reverse=True)

    def _calculate_by_ticker(
        self, trades: list[TradeInput]
    ) -> dict[str, PerformanceStats]:
        """Calculate stats grouped by ticker."""
        by_ticker = defaultdict(list)
        for t in trades:
            by_ticker[t.ticker].append(t)

        return {
            ticker: self._calculate_stats(ticker_trades)
            for ticker, ticker_trades in by_ticker.items()
        }

    def _calculate_monthly(self, trades: list[TradeInput]) -> dict[str, float]:
        """Calculate monthly P&L."""
        monthly = defaultdict(float)

        for t in trades:
            if t.exit_date:
                month_key = t.exit_date.strftime("%Y-%m")
                monthly[month_key] += t.pnl or 0

        return {k: round(v, 2) for k, v in sorted(monthly.items())}

    def _empty_response(self) -> PerformanceResponse:
        """Return empty response when no trades."""
        return PerformanceResponse(
            overall=self._empty_stats(),
            by_strategy=[],
            by_ticker={},
            monthly_pnl={},
        )

    def _empty_stats(self) -> PerformanceStats:
        """Return empty stats."""
        return PerformanceStats(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            profit_factor=0,
            total_pnl=0,
            avg_win=0,
            avg_loss=0,
            largest_win=0,
            largest_loss=0,
            avg_hold_days=0,
            expectancy=0,
        )


# Singleton instance
stats_service = StatsService()
```

**Step 3: Update services/__init__.py**

```python
# python-service/app/services/__init__.py
from app.services.market_data import market_data_service
from app.services.indicators import indicator_service
from app.services.screener import screener_service
from app.services.stats import stats_service

__all__ = [
    "market_data_service",
    "indicator_service",
    "screener_service",
    "stats_service",
]
```

**Step 4: Create tests/test_stats.py**

```python
# python-service/tests/test_stats.py
import pytest
from datetime import datetime, timedelta
from app.services.stats import StatsService
from app.models.stats_schemas import TradeInput


@pytest.fixture
def service():
    return StatsService()


@pytest.fixture
def sample_trades():
    """Create sample trade data."""
    base_date = datetime(2026, 1, 1)
    return [
        TradeInput(
            id="1",
            ticker="AAPL",
            direction="long",
            entry_date=base_date,
            entry_price=150,
            exit_date=base_date + timedelta(days=5),
            exit_price=160,
            position_size=100,
            pnl=1000,
            strategy_tags=["momentum"],
        ),
        TradeInput(
            id="2",
            ticker="MSFT",
            direction="long",
            entry_date=base_date + timedelta(days=7),
            entry_price=300,
            exit_date=base_date + timedelta(days=10),
            exit_price=290,
            position_size=50,
            pnl=-500,
            strategy_tags=["momentum"],
        ),
        TradeInput(
            id="3",
            ticker="GOOGL",
            direction="long",
            entry_date=base_date + timedelta(days=15),
            entry_price=140,
            exit_date=base_date + timedelta(days=20),
            exit_price=155,
            position_size=100,
            pnl=1500,
            strategy_tags=["breakout"],
        ),
        TradeInput(
            id="4",
            ticker="AAPL",
            direction="long",
            entry_date=base_date + timedelta(days=25),
            entry_price=165,
            exit_date=base_date + timedelta(days=28),
            exit_price=170,
            position_size=100,
            pnl=500,
            strategy_tags=["momentum", "breakout"],
        ),
    ]


def test_calculate_overall_stats(service, sample_trades):
    """Test overall statistics calculation."""
    result = service.calculate(sample_trades)

    assert result.overall.total_trades == 4
    assert result.overall.winning_trades == 3
    assert result.overall.losing_trades == 1
    assert result.overall.win_rate == 0.75
    assert result.overall.total_pnl == 2500


def test_calculate_by_strategy(service, sample_trades):
    """Test per-strategy statistics."""
    result = service.calculate(sample_trades)

    strategy_names = [s.strategy_name for s in result.by_strategy]
    assert "momentum" in strategy_names
    assert "breakout" in strategy_names

    momentum = next(s for s in result.by_strategy if s.strategy_name == "momentum")
    assert momentum.total_trades == 3  # trades 1, 2, 4


def test_calculate_by_ticker(service, sample_trades):
    """Test per-ticker statistics."""
    result = service.calculate(sample_trades)

    assert "AAPL" in result.by_ticker
    assert result.by_ticker["AAPL"].total_trades == 2


def test_calculate_monthly_pnl(service, sample_trades):
    """Test monthly P&L aggregation."""
    result = service.calculate(sample_trades)

    assert "2026-01" in result.monthly_pnl
    assert result.monthly_pnl["2026-01"] == 2500


def test_empty_trades(service):
    """Test handling of empty trade list."""
    result = service.calculate([])

    assert result.overall.total_trades == 0
    assert result.overall.win_rate == 0


def test_profit_factor(service, sample_trades):
    """Test profit factor calculation."""
    result = service.calculate(sample_trades)

    # Total wins: 3000, Total losses: 500
    # Profit factor = 3000 / 500 = 6.0
    assert result.overall.profit_factor == 6.0
```

**Step 5: Run tests**

```bash
cd C:/Users/Oliver/source/repos/meridian/python-service
uv run pytest tests/test_stats.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add python-service/
git commit -m "feat(python): add performance statistics service"
```

---

### Task 2.6: API Routers

**Files:**
- Create: `python-service/app/routers/__init__.py`
- Create: `python-service/app/routers/market_data.py`
- Create: `python-service/app/routers/indicators.py`
- Create: `python-service/app/routers/screener.py`
- Create: `python-service/app/routers/stats.py`
- Modify: `python-service/app/main.py`

**Step 1: Create routers/market_data.py**

```python
# python-service/app/routers/market_data.py
from fastapi import APIRouter, HTTPException

from app.services import market_data_service
from app.models.schemas import OHLCVResponse, QuoteResponse

router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.get("/{ticker}", response_model=OHLCVResponse)
async def get_ohlcv(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
):
    """Get OHLCV data for a ticker."""
    try:
        return market_data_service.get_ohlcv(ticker, period, interval)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/quote/{ticker}", response_model=QuoteResponse)
async def get_quote(ticker: str):
    """Get current quote for a ticker."""
    try:
        return market_data_service.get_quote(ticker)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Step 2: Create routers/indicators.py**

```python
# python-service/app/routers/indicators.py
from fastapi import APIRouter, HTTPException

from app.services import indicator_service
from app.models.indicator_schemas import IndicatorRequest, IndicatorResponse

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.post("", response_model=IndicatorResponse)
async def calculate_indicators(request: IndicatorRequest):
    """Calculate technical indicators for a ticker."""
    try:
        return indicator_service.calculate(
            ticker=request.ticker,
            period=request.period,
            interval=request.interval,
            indicators=request.indicators,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Step 3: Create routers/screener.py**

```python
# python-service/app/routers/screener.py
from fastapi import APIRouter

from app.services import screener_service
from app.models.screener_schemas import ScreenerRequest, ScreenerResponse

router = APIRouter(prefix="/screen", tags=["Screener"])


@router.post("", response_model=ScreenerResponse)
async def run_screener(request: ScreenerRequest):
    """Run stock screener with given criteria."""
    return screener_service.screen(
        criteria=request.criteria,
        universe=request.universe,
        custom_tickers=request.custom_tickers,
        limit=request.limit,
    )
```

**Step 4: Create routers/stats.py**

```python
# python-service/app/routers/stats.py
from fastapi import APIRouter

from app.services import stats_service
from app.models.stats_schemas import TradeInput, PerformanceResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.post("/performance", response_model=PerformanceResponse)
async def calculate_performance(trades: list[TradeInput]):
    """Calculate performance statistics from trade data."""
    return stats_service.calculate(trades)
```

**Step 5: Create routers/__init__.py**

```python
# python-service/app/routers/__init__.py
from app.routers.market_data import router as market_data_router
from app.routers.indicators import router as indicators_router
from app.routers.screener import router as screener_router
from app.routers.stats import router as stats_router

__all__ = [
    "market_data_router",
    "indicators_router",
    "screener_router",
    "stats_router",
]
```

**Step 6: Update main.py to include routers**

```python
# python-service/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    market_data_router,
    indicators_router,
    screener_router,
    stats_router,
)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(market_data_router)
app.include_router(indicators_router)
app.include_router(screener_router)
app.include_router(stats_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "meridian-analytics"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Meridian Analytics Service", "version": "0.1.0"}
```

**Step 7: Run all tests**

```bash
cd C:/Users/Oliver/source/repos/meridian/python-service
uv run pytest tests/ -v
```

Expected: All PASS

**Step 8: Commit**

```bash
git add python-service/
git commit -m "feat(python): add API routers for all services"
```

---

### Task 2.7: Python Dockerfile

**Files:**
- Create: `python-service/Dockerfile`
- Create: `python-service/.env.example`

**Step 1: Create Dockerfile**

```dockerfile
# python-service/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system -e .

# Copy application code
COPY app/ app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Create .env.example**

```bash
# python-service/.env.example
DEBUG=true
POLYGON_API_KEY=your_polygon_api_key_here
```

**Step 3: Test Docker build locally (optional)**

```bash
cd C:/Users/Oliver/source/repos/meridian/python-service
docker build -t meridian-python:dev .
docker run -p 8000:8000 -e DEBUG=true meridian-python:dev
```

**Step 4: Commit**

```bash
git add python-service/
git commit -m "feat(python): add Dockerfile and env example"
```

---

## Phase 3: .NET Backend API

### Task 3.1: Initialize .NET Solution

**Files:**
- Create: `backend/Meridian.sln`
- Create: `backend/src/Meridian.Api/Meridian.Api.csproj`
- Create: `backend/src/Meridian.Api/Program.cs`
- Create: `backend/src/Meridian.Core/Meridian.Core.csproj`
- Create: `backend/src/Meridian.Infrastructure/Meridian.Infrastructure.csproj`
- Create: `backend/src/Meridian.Agents/Meridian.Agents.csproj`
- Create: `backend/src/Meridian.Jobs/Meridian.Jobs.csproj`

**Step 1: Create solution and projects**

```bash
cd C:/Users/Oliver/source/repos/meridian/backend

# Create solution
dotnet new sln -n Meridian

# Create projects
dotnet new webapi -n Meridian.Api -o src/Meridian.Api
dotnet new classlib -n Meridian.Core -o src/Meridian.Core
dotnet new classlib -n Meridian.Infrastructure -o src/Meridian.Infrastructure
dotnet new classlib -n Meridian.Agents -o src/Meridian.Agents
dotnet new classlib -n Meridian.Jobs -o src/Meridian.Jobs

# Create test projects
dotnet new xunit -n Meridian.Core.Tests -o tests/Meridian.Core.Tests
dotnet new xunit -n Meridian.Api.Tests -o tests/Meridian.Api.Tests

# Add projects to solution
dotnet sln add src/Meridian.Api/Meridian.Api.csproj
dotnet sln add src/Meridian.Core/Meridian.Core.csproj
dotnet sln add src/Meridian.Infrastructure/Meridian.Infrastructure.csproj
dotnet sln add src/Meridian.Agents/Meridian.Agents.csproj
dotnet sln add src/Meridian.Jobs/Meridian.Jobs.csproj
dotnet sln add tests/Meridian.Core.Tests/Meridian.Core.Tests.csproj
dotnet sln add tests/Meridian.Api.Tests/Meridian.Api.Tests.csproj

# Add project references
dotnet add src/Meridian.Api/Meridian.Api.csproj reference src/Meridian.Core/Meridian.Core.csproj
dotnet add src/Meridian.Api/Meridian.Api.csproj reference src/Meridian.Infrastructure/Meridian.Infrastructure.csproj
dotnet add src/Meridian.Api/Meridian.Api.csproj reference src/Meridian.Agents/Meridian.Agents.csproj
dotnet add src/Meridian.Api/Meridian.Api.csproj reference src/Meridian.Jobs/Meridian.Jobs.csproj
dotnet add src/Meridian.Infrastructure/Meridian.Infrastructure.csproj reference src/Meridian.Core/Meridian.Core.csproj
dotnet add src/Meridian.Agents/Meridian.Agents.csproj reference src/Meridian.Core/Meridian.Core.csproj
dotnet add src/Meridian.Agents/Meridian.Agents.csproj reference src/Meridian.Infrastructure/Meridian.Infrastructure.csproj
dotnet add src/Meridian.Jobs/Meridian.Jobs.csproj reference src/Meridian.Core/Meridian.Core.csproj
dotnet add src/Meridian.Jobs/Meridian.Jobs.csproj reference src/Meridian.Agents/Meridian.Agents.csproj
dotnet add tests/Meridian.Core.Tests/Meridian.Core.Tests.csproj reference src/Meridian.Core/Meridian.Core.csproj
dotnet add tests/Meridian.Api.Tests/Meridian.Api.Tests.csproj reference src/Meridian.Api/Meridian.Api.csproj
```

**Step 2: Add NuGet packages to Meridian.Api**

```bash
cd C:/Users/Oliver/source/repos/meridian/backend/src/Meridian.Api
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
dotnet add package Microsoft.Identity.Web
dotnet add package Swashbuckle.AspNetCore
```

**Step 3: Add NuGet packages to Meridian.Infrastructure**

```bash
cd C:/Users/Oliver/source/repos/meridian/backend/src/Meridian.Infrastructure
dotnet add package Microsoft.EntityFrameworkCore.SqlServer
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Microsoft.Azure.Cosmos
dotnet add package Azure.Storage.Blobs
dotnet add package Stripe.net
```

**Step 4: Add NuGet packages to Meridian.Agents**

```bash
cd C:/Users/Oliver/source/repos/meridian/backend/src/Meridian.Agents
dotnet add package Microsoft.SemanticKernel
dotnet add package Microsoft.SemanticKernel.Connectors.AzureOpenAI
dotnet add package Azure.AI.OpenAI
```

**Step 5: Add NuGet packages to Meridian.Jobs**

```bash
cd C:/Users/Oliver/source/repos/meridian/backend/src/Meridian.Jobs
dotnet add package Hangfire.Core
dotnet add package Hangfire.SqlServer
dotnet add package Hangfire.AspNetCore
```

**Step 6: Verify build**

```bash
cd C:/Users/Oliver/source/repos/meridian/backend
dotnet build
```

Expected: Build succeeded

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat(backend): initialize .NET solution with project structure"
```

---

### Task 3.2: Core Domain Entities

**Files:**
- Create: `backend/src/Meridian.Core/Entities/User.cs`
- Create: `backend/src/Meridian.Core/Entities/Trade.cs`
- Create: `backend/src/Meridian.Core/Entities/Strategy.cs`
- Create: `backend/src/Meridian.Core/Enums/TradeDirection.cs`
- Create: `backend/src/Meridian.Core/Enums/TradeStatus.cs`
- Create: `backend/src/Meridian.Core/Enums/SubscriptionTier.cs`

**Step 1: Create Enums**

```csharp
// backend/src/Meridian.Core/Enums/TradeDirection.cs
namespace Meridian.Core.Enums;

public enum TradeDirection
{
    Long,
    Short
}
```

```csharp
// backend/src/Meridian.Core/Enums/TradeStatus.cs
namespace Meridian.Core.Enums;

public enum TradeStatus
{
    Open,
    Closed,
    Cancelled
}
```

```csharp
// backend/src/Meridian.Core/Enums/SubscriptionTier.cs
namespace Meridian.Core.Enums;

public enum SubscriptionTier
{
    Free,
    Premium
}
```

**Step 2: Create User entity**

```csharp
// backend/src/Meridian.Core/Entities/User.cs
using Meridian.Core.Enums;

namespace Meridian.Core.Entities;

public class User
{
    public Guid Id { get; set; }
    public required string AzureAdB2CId { get; set; }
    public required string Email { get; set; }
    public string? DisplayName { get; set; }
    public SubscriptionTier SubscriptionTier { get; set; } = SubscriptionTier.Free;
    public string? StripeCustomerId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<Trade> Trades { get; set; } = new List<Trade>();
    public ICollection<Strategy> Strategies { get; set; } = new List<Strategy>();
}
```

**Step 3: Create Strategy entity**

```csharp
// backend/src/Meridian.Core/Entities/Strategy.cs
namespace Meridian.Core.Entities;

public class Strategy
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public required string Source { get; set; } // "user" or "ai"
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public User? User { get; set; }
    public ICollection<TradeStrategyTag> TradeStrategyTags { get; set; } = new List<TradeStrategyTag>();
}
```

**Step 4: Create Trade entity**

```csharp
// backend/src/Meridian.Core/Entities/Trade.cs
using Meridian.Core.Enums;

namespace Meridian.Core.Entities;

public class Trade
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public required string Ticker { get; set; }
    public TradeDirection Direction { get; set; }
    public DateTime EntryDate { get; set; }
    public decimal EntryPrice { get; set; }
    public DateTime? ExitDate { get; set; }
    public decimal? ExitPrice { get; set; }
    public decimal PositionSize { get; set; }
    public decimal? StopLoss { get; set; }
    public decimal? TakeProfit { get; set; }
    public decimal? Pnl { get; set; }
    public decimal? PnlPercent { get; set; }
    public TradeStatus Status { get; set; } = TradeStatus.Open;
    public string? Thesis { get; set; }
    public string? EmotionalState { get; set; }
    public string? MarketConditions { get; set; }
    public string? Notes { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public User? User { get; set; }
    public ICollection<TradeStrategyTag> StrategyTags { get; set; } = new List<TradeStrategyTag>();
    public ICollection<TradeScreenshot> Screenshots { get; set; } = new List<TradeScreenshot>();
}
```

**Step 5: Create TradeStrategyTag entity**

```csharp
// backend/src/Meridian.Core/Entities/TradeStrategyTag.cs
namespace Meridian.Core.Entities;

public class TradeStrategyTag
{
    public Guid TradeId { get; set; }
    public Guid StrategyId { get; set; }
    public required string Source { get; set; } // "user" or "ai"

    // Navigation properties
    public Trade? Trade { get; set; }
    public Strategy? Strategy { get; set; }
}
```

**Step 6: Create TradeScreenshot entity**

```csharp
// backend/src/Meridian.Core/Entities/TradeScreenshot.cs
namespace Meridian.Core.Entities;

public class TradeScreenshot
{
    public Guid Id { get; set; }
    public Guid TradeId { get; set; }
    public required string BlobUrl { get; set; }
    public string? Caption { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public Trade? Trade { get; set; }
}
```

**Step 7: Verify build**

```bash
cd C:/Users/Oliver/source/repos/meridian/backend
dotnet build src/Meridian.Core/Meridian.Core.csproj
```

Expected: Build succeeded

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat(backend): add core domain entities"
```

---

## Phase 3 Continued & Remaining Phases

Due to the comprehensive nature of this implementation plan, the remaining tasks are outlined below. Each follows the same TDD structure demonstrated above.

### Phase 3 (Continued): .NET Backend
- **Task 3.3**: Repository interfaces (ITradeRepository, IUserRepository, IStrategyRepository)
- **Task 3.4**: Entity Framework DbContext and migrations
- **Task 3.5**: Repository implementations
- **Task 3.6**: Cosmos DB service for conversations and agent configs
- **Task 3.7**: Python analytics HTTP client
- **Task 3.8**: Trade service with business logic
- **Task 3.9**: API Controllers (TradesController, StrategiesController, AnalyticsController)
- **Task 3.10**: Azure AD B2C authentication configuration
- **Task 3.11**: Stripe billing service and webhooks
- **Task 3.12**: Dockerfile for .NET API

### Phase 4: Semantic Kernel Agents
- **Task 4.1**: Semantic Kernel configuration with Azure OpenAI
- **Task 4.2**: MarketDataPlugin (calls Python service)
- **Task 4.3**: TradeHistoryPlugin (queries SQL + embeddings)
- **Task 4.4**: UserProfilePlugin (reads from Cosmos)
- **Task 4.5**: ScreenerAgent implementation
- **Task 4.6**: AnalystAgent implementation
- **Task 4.7**: CoachAgent implementation
- **Task 4.8**: AgentOrchestrator service
- **Task 4.9**: AgentsController with chat endpoint
- **Task 4.10**: Web PubSub integration for real-time chat

### Phase 5: Hangfire Background Jobs
- **Task 5.1**: Hangfire configuration with SQL storage
- **Task 5.2**: ScreenerJob (runs user's scheduled screeners)
- **Task 5.3**: DailySummaryJob (morning briefings)
- **Task 5.4**: ProfileRefreshJob (regenerate trading profiles)
- **Task 5.5**: EmbeddingJob (embed new trades async)
- **Task 5.6**: Email notification service (Azure Communication Services)

### Phase 6: Next.js Frontend
- **Task 6.1**: Initialize Next.js project with TypeScript
- **Task 6.2**: Configure Tailwind CSS and shadcn/ui
- **Task 6.3**: Azure AD B2C authentication (MSAL)
- **Task 6.4**: API client with typed fetch wrapper
- **Task 6.5**: Dashboard layout (sidebar, header, mobile nav)
- **Task 6.6**: Dashboard home page (overview, quick stats)
- **Task 6.7**: Journal pages (list, create, detail)
- **Task 6.8**: Trade form component with strategy tags
- **Task 6.9**: Analytics page with charts (Recharts/Lightweight Charts)
- **Task 6.10**: Strategy breakdown page
- **Task 6.11**: Agent overview page
- **Task 6.12**: Chat interface component (Web PubSub)
- **Task 6.13**: Screener configuration page
- **Task 6.14**: Settings pages (account, billing, notifications)
- **Task 6.15**: Stripe checkout integration
- **Task 6.16**: Dockerfile for Next.js

### Phase 7: CI/CD & Deployment
- **Task 7.1**: GitHub Actions workflow for frontend
- **Task 7.2**: GitHub Actions workflow for backend
- **Task 7.3**: GitHub Actions workflow for Python service
- **Task 7.4**: GitHub Actions workflow for infrastructure
- **Task 7.5**: Azure Container App definitions (Bicep)
- **Task 7.6**: Azure Front Door configuration
- **Task 7.7**: Production deployment and smoke tests

### Phase 8: Polish & Launch Prep
- **Task 8.1**: Error handling and logging (Application Insights)
- **Task 8.2**: Rate limiting and API throttling
- **Task 8.3**: Landing page and marketing site
- **Task 8.4**: Documentation (API docs, user guide)
- **Task 8.5**: End-to-end testing
- **Task 8.6**: Security review and hardening
- **Task 8.7**: Performance testing and optimization

---

## Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| 1 | 1.1-1.3 | Repository setup, Azure infrastructure |
| 2 | 2.1-2.7 | Python analytics service (complete) |
| 3 | 3.1-3.12 | .NET backend API |
| 4 | 4.1-4.10 | Semantic Kernel agents |
| 5 | 5.1-5.6 | Background jobs |
| 6 | 6.1-6.16 | Next.js frontend |
| 7 | 7.1-7.7 | CI/CD and deployment |
| 8 | 8.1-8.7 | Polish and launch |

**Total estimated tasks:** ~55 tasks

---

**Plan complete and saved to `docs/plans/2026-02-03-meridian-implementation.md`.**

**Two execution options:**

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
