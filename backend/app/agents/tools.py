import uuid

from langchain_core.tools import tool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Trade, TradeStrategyTag, UserProfile
from app.models.screener_schemas import RangeCriteria, ScreenerCriteria
from app.services.indicators import indicator_service
from app.services.market_data import market_data_service
from app.services.screener import screener_service

# --- Market Data Tools ---


@tool
def get_quote(ticker: str) -> str:
    """Get the current price quote for a stock ticker symbol."""
    try:
        quote = market_data_service.get_quote(ticker)
        return (
            f"{quote.ticker}: ${quote.price:.2f} ({quote.change_percent:+.2f}%) "
            f"| Volume: {quote.volume:,}"
        )
    except Exception:
        return f"No quote data available for {ticker}"


@tool
def get_ohlcv(ticker: str, period: str = "1mo", interval: str = "1d") -> str:
    """Get historical OHLCV price data for a stock."""
    try:
        data = market_data_service.get_ohlcv(ticker, period, interval)
        if not data.bars:
            return f"No price data available for {ticker}"
        latest = data.bars[-1]
        first = data.bars[0]
        high = max(b.high for b in data.bars)
        low = min(b.low for b in data.bars)
        avg_vol = int(sum(b.volume for b in data.bars) / len(data.bars))
        return (
            f"{ticker} ({period}): Open ${first.open:.2f} -> Close ${latest.close:.2f} | "
            f"High ${high:.2f} Low ${low:.2f} | Avg Volume: {avg_vol:,} | {len(data.bars)} bars"
        )
    except Exception:
        return f"No price data available for {ticker}"


@tool
def calculate_indicators(
    ticker: str,
    indicators: str = "sma_20,sma_50,rsi_14,macd",
) -> str:
    """Calculate technical indicators like RSI, SMA, MACD for a stock."""
    try:
        indicator_list = [i.strip() for i in indicators.split(",")]
        result = indicator_service.calculate(ticker, "3mo", "1d", indicator_list)
        if not result.bars:
            return f"No indicator data for {ticker}"
        latest = result.bars[-1]
        parts = [f"{ticker} latest indicators:"]
        for name, value in latest.indicators.items():
            if value is not None:
                parts.append(f"  {name}: {value:.2f}")
        return "\n".join(parts)
    except Exception:
        return f"No indicator data for {ticker}"


@tool
def run_screener(
    min_price: float | None = None,
    max_price: float | None = None,
    min_volume_ratio: float | None = None,
    min_rsi: float | None = None,
    max_rsi: float | None = None,
    universe: str = "sp500",
    limit: int = 10,
) -> str:
    """Screen stocks based on technical criteria like price range, volume, RSI."""
    criteria = ScreenerCriteria(
        price=RangeCriteria(min=min_price, max=max_price) if (min_price or max_price) else None,
        volume_ratio=RangeCriteria(min=min_volume_ratio) if min_volume_ratio else None,
        rsi_14=RangeCriteria(min=min_rsi, max=max_rsi) if (min_rsi or max_rsi) else None,
    )
    result = screener_service.screen(criteria, universe, None, limit)
    if not result.matches:
        return "No stocks matched the screening criteria."
    lines = [f"Screener results ({len(result.matches)} matches, {result.total_scanned} scanned):"]
    for m in result.matches:
        line = (
            f"  {m.ticker}: ${m.price:.2f} ({m.change_percent:+.2f}%) "
            f"Vol ratio: {m.volume_ratio:.1f}x"
        )
        if m.rsi_14 is not None:
            line += f" RSI: {m.rsi_14:.0f}"
        lines.append(line)
    return "\n".join(lines)


# --- Trade History Tools (need db session) ---


def create_trade_tools(db: AsyncSession, user_id: uuid.UUID) -> list:
    """Create trade-related tools bound to a specific db session and user."""

    @tool
    async def get_open_trades() -> str:
        """Get all currently open trades for the user."""
        query = (
            select(Trade)
            .options(selectinload(Trade.strategy_tags).selectinload(TradeStrategyTag.strategy))
            .where(Trade.user_id == user_id, Trade.status == "Open")
            .order_by(Trade.entry_date.desc())
            .limit(100)
        )
        result = await db.execute(query)
        trades = result.scalars().all()
        if not trades:
            return "No open trades."
        lines = [f"Open trades ({len(trades)}):"]
        for t in trades:
            strategy_names = [tag.strategy.name for tag in (t.strategy_tags or []) if tag.strategy]
            lines.append(
                f"  {t.ticker} {t.direction} @ ${t.entry_price:.2f} ({t.entry_date:%b %d}) | "
                f"Size: {t.position_size} | "
                f"SL: {f'${t.stop_loss:.2f}' if t.stop_loss else 'none'} | "
                f"TP: {f'${t.take_profit:.2f}' if t.take_profit else 'none'} | "
                f"Tags: [{', '.join(strategy_names)}]"
            )
        return "\n".join(lines)

    @tool
    async def get_recent_closed_trades(count: int = 20) -> str:
        """Get recently closed trades with P&L."""
        query = (
            select(Trade)
            .where(Trade.user_id == user_id, Trade.status == "Closed")
            .order_by(Trade.entry_date.desc())
            .limit(count)
        )
        result = await db.execute(query)
        trades = list(result.scalars().all())
        if not trades:
            return "No closed trades found."
        total_pnl = sum(t.pnl for t in trades if t.pnl is not None)
        win_count = sum(1 for t in trades if t.pnl and t.pnl > 0)
        win_rate = win_count / len(trades) if trades else 0
        lines = [
            f"Recent closed trades ({len(trades)}): "
            f"Total P&L: ${total_pnl:.2f} | Win rate: {win_rate:.0%}"
        ]
        for t in trades[:10]:
            lines.append(
                f"  {t.ticker} {t.direction}: ${t.entry_price:.2f} -> ${t.exit_price:.2f} | "
                f"P&L: ${t.pnl:.2f} ({t.pnl_percent:+.1f}%) | "
                f"{t.entry_date:%b %d}-{t.exit_date:%b %d}"
            )
        return "\n".join(lines)

    @tool
    async def get_trades_for_ticker(ticker: str) -> str:
        """Get trade history for a specific stock ticker."""
        query = (
            select(Trade)
            .where(Trade.user_id == user_id)
            .order_by(Trade.entry_date.desc())
            .limit(200)
        )
        result = await db.execute(query)
        all_trades = result.scalars().all()
        ticker_trades = [t for t in all_trades if t.ticker.upper() == ticker.upper()]
        if not ticker_trades:
            return f"No trade history for {ticker}."
        closed = [t for t in ticker_trades if t.status == "Closed" and t.pnl is not None]
        total_pnl = sum(t.pnl for t in closed)
        win_rate = sum(1 for t in closed if t.pnl > 0) / len(closed) if closed else 0
        lines = [
            f"{ticker} history: {len(ticker_trades)} trades ({len(closed)} closed) | "
            f"Total P&L: ${total_pnl:.2f} | Win rate: {win_rate:.0%}"
        ]
        for t in ticker_trades[:5]:
            status = "OPEN" if t.status == "Open" else f"${t.pnl:.2f}"
            lines.append(
                f"  {t.direction} @ ${t.entry_price:.2f} ({t.entry_date:%b %d}) -> {status}"
            )
        return "\n".join(lines)

    @tool
    async def get_trade_count() -> str:
        """Get the total number of trades for the user."""
        from sqlalchemy import func

        open_q = (
            select(func.count())
            .select_from(Trade)
            .where(Trade.user_id == user_id, Trade.status == "Open")
        )
        closed_q = (
            select(func.count())
            .select_from(Trade)
            .where(Trade.user_id == user_id, Trade.status == "Closed")
        )
        open_result = await db.execute(open_q)
        closed_result = await db.execute(closed_q)
        open_count = open_result.scalar_one()
        closed_count = closed_result.scalar_one()
        total = open_count + closed_count
        return f"Trade counts: {open_count} open, {closed_count} closed, {total} total"

    return [get_open_trades, get_recent_closed_trades, get_trades_for_ticker, get_trade_count]


def create_profile_tools(db: AsyncSession, user_id_str: str) -> list:
    """Create profile-related tools bound to a specific db session and user."""

    @tool
    async def get_user_profile() -> str:
        """Get the user's trading profile including style, preferred sectors, and watchlist."""
        query = select(UserProfile).where(UserProfile.user_id == user_id_str)
        result = await db.execute(query)
        profile = result.scalar_one_or_none()
        if not profile:
            return "No user profile found. This appears to be a new user."
        sectors = ", ".join(profile.preferred_sectors) if profile.preferred_sectors else "None set"
        watchlist = ", ".join(profile.watchlist_tickers) if profile.watchlist_tickers else "Empty"
        refreshed = f"{profile.last_refreshed:%b %d, %Y}" if profile.last_refreshed else "Never"
        lines = [
            "User Trading Profile:",
            f"  Trading Style: {profile.trading_style or 'Not set'}",
            f"  Risk Profile: {profile.risk_profile or 'Not set'}",
            f"  Preferred Sectors: {sectors}",
            f"  Watchlist: {watchlist}",
            f"  Last Refreshed: {refreshed}",
        ]
        if profile.strategy_performance:
            lines.append("  Strategy Performance:")
            for strategy, win_rate in profile.strategy_performance.items():
                lines.append(f"    {strategy}: {win_rate:.0%} win rate")
        return "\n".join(lines)

    @tool
    async def get_watchlist() -> str:
        """Get the user's stock watchlist."""
        query = select(UserProfile).where(UserProfile.user_id == user_id_str)
        result = await db.execute(query)
        profile = result.scalar_one_or_none()
        if not profile or not profile.watchlist_tickers:
            return "Watchlist is empty."
        return f"Watchlist: {', '.join(profile.watchlist_tickers)}"

    return [get_user_profile, get_watchlist]


# Static tools (no db needed)
MARKET_TOOLS = [get_quote, get_ohlcv, calculate_indicators, run_screener]
