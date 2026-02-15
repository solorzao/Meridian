import logging

import yfinance as yf

from app.models.screener_schemas import (
    ScreenerCriteria,
    ScreenerMatch,
    ScreenerResponse,
)
from app.services.indicators import indicator_service

logger = logging.getLogger(__name__)


class ScreenerService:
    """Service for screening stocks against criteria."""

    SP500_SAMPLE = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "META",
        "TSLA",
        "BRK-B",
        "UNH",
        "JNJ",
        "JPM",
        "V",
        "PG",
        "XOM",
        "HD",
        "CVX",
        "MA",
        "ABBV",
        "MRK",
        "PFE",
        "KO",
        "PEP",
        "COST",
        "TMO",
        "AVGO",
        "MCD",
        "WMT",
        "CSCO",
        "ACN",
        "ABT",
        "DHR",
        "LLY",
        "NEE",
        "VZ",
        "ADBE",
        "CRM",
    ]

    NASDAQ100_SAMPLE = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "META",
        "TSLA",
        "AVGO",
        "ADBE",
        "COST",
        "CSCO",
        "PEP",
        "AMD",
        "NFLX",
        "INTC",
        "CMCSA",
        "INTU",
        "QCOM",
        "TXN",
        "AMGN",
        "AMAT",
        "BKNG",
        "ISRG",
        "MDLZ",
    ]

    def screen(
        self,
        criteria: ScreenerCriteria,
        universe: str = "sp500",
        custom_tickers: list[str] | None = None,
        limit: int = 20,
    ) -> ScreenerResponse:
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
            except Exception as e:
                logger.warning("Failed to evaluate ticker %s: %s", ticker, e)
                continue

            if len(matches) >= limit:
                break

        matches.sort(key=lambda x: x.volume_ratio or 0, reverse=True)

        return ScreenerResponse(
            matches=matches[:limit],
            total_scanned=len(tickers),
            criteria_summary=self._summarize_criteria(criteria),
        )

    def _evaluate_ticker(self, ticker: str, criteria: ScreenerCriteria) -> ScreenerMatch | None:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        hist = stock.history(period="5d")

        if hist.empty:
            return None

        price = info.last_price
        prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else price
        change_pct = ((price - prev_close) / prev_close) * 100

        vol_avg = hist["Volume"].mean()
        vol_ratio = info.last_volume / vol_avg if vol_avg > 0 else 1.0

        today_open = hist["Open"].iloc[-1]
        gap_pct = ((today_open - prev_close) / prev_close) * 100

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
            name=None,
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


screener_service = ScreenerService()
