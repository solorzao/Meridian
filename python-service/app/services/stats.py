from collections import defaultdict

from app.models.stats_schemas import (
    TradeInput,
    PerformanceStats,
    StrategyStats,
    PerformanceResponse,
)


class StatsService:
    """Service for calculating trading performance statistics."""

    def calculate(self, trades: list[TradeInput]) -> PerformanceResponse:
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
        if not trades:
            return self._empty_stats()

        pnls = [t.pnl for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0

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
        by_ticker = defaultdict(list)
        for t in trades:
            by_ticker[t.ticker].append(t)

        return {
            ticker: self._calculate_stats(ticker_trades)
            for ticker, ticker_trades in by_ticker.items()
        }

    def _calculate_monthly(self, trades: list[TradeInput]) -> dict[str, float]:
        monthly = defaultdict(float)

        for t in trades:
            if t.exit_date:
                month_key = t.exit_date.strftime("%Y-%m")
                monthly[month_key] += t.pnl or 0

        return {k: round(v, 2) for k, v in sorted(monthly.items())}

    def _empty_response(self) -> PerformanceResponse:
        return PerformanceResponse(
            overall=self._empty_stats(),
            by_strategy=[],
            by_ticker={},
            monthly_pnl={},
        )

    def _empty_stats(self) -> PerformanceStats:
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


stats_service = StatsService()
