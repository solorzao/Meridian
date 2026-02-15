from datetime import datetime

import yfinance as yf

from app.models.schemas import OHLCVBar, OHLCVResponse, QuoteResponse


class MarketDataService:
    """Service for fetching market data."""

    def get_ohlcv(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> OHLCVResponse:
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


market_data_service = MarketDataService()
