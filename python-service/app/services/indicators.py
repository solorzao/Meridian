import pandas as pd
import pandas_ta as ta

from app.services.market_data import market_data_service
from app.models.indicator_schemas import IndicatorBar, IndicatorResponse


class IndicatorService:
    """Service for calculating technical indicators."""

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
        if indicators is None:
            indicators = ["sma_20", "sma_50", "rsi_14", "macd"]

        ohlcv = market_data_service.get_ohlcv(ticker, period, interval)

        df = pd.DataFrame([bar.model_dump() for bar in ohlcv.bars])
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

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


indicator_service = IndicatorService()
