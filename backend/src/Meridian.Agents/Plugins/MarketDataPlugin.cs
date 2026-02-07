using System.ComponentModel;
using Meridian.Infrastructure.Http;
using Microsoft.SemanticKernel;

namespace Meridian.Agents.Plugins;

public class MarketDataPlugin
{
    private readonly PythonAnalyticsClient _client;

    public MarketDataPlugin(PythonAnalyticsClient client)
    {
        _client = client;
    }

    [KernelFunction("get_quote")]
    [Description("Get the current price quote for a stock ticker symbol")]
    public async Task<string> GetQuoteAsync(
        [Description("Stock ticker symbol (e.g., AAPL, MSFT)")] string ticker)
    {
        var quote = await _client.GetQuoteAsync(ticker);
        if (quote == null) return $"No quote data available for {ticker}";

        return $"{quote.Ticker}: ${quote.Price:F2} ({quote.ChangePercent:+0.00;-0.00}%) | Volume: {quote.Volume:N0}";
    }

    [KernelFunction("get_ohlcv")]
    [Description("Get historical OHLCV price data for a stock")]
    public async Task<string> GetOhlcvAsync(
        [Description("Stock ticker symbol")] string ticker,
        [Description("Time period (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y)")] string period = "1mo",
        [Description("Data interval (e.g., 1d, 1wk)")] string interval = "1d")
    {
        var data = await _client.GetOhlcvAsync(ticker, period, interval);
        if (data == null || data.Bars.Count == 0) return $"No price data available for {ticker}";

        var latest = data.Bars.Last();
        var first = data.Bars.First();
        var high = data.Bars.Max(b => b.High);
        var low = data.Bars.Min(b => b.Low);
        var avgVolume = (long)data.Bars.Average(b => b.Volume);

        return $"{ticker} ({period}): Open ${first.Open:F2} → Close ${latest.Close:F2} | " +
               $"High ${high:F2} Low ${low:F2} | Avg Volume: {avgVolume:N0} | {data.Bars.Count} bars";
    }

    [KernelFunction("calculate_indicators")]
    [Description("Calculate technical indicators like RSI, SMA, MACD for a stock")]
    public async Task<string> CalculateIndicatorsAsync(
        [Description("Stock ticker symbol")] string ticker,
        [Description("Comma-separated indicator names (sma_20, sma_50, rsi_14, macd, ema_12, atr_14, bbands_upper, bbands_lower)")] string indicators = "sma_20,sma_50,rsi_14,macd")
    {
        var indicatorList = indicators.Split(',').Select(i => i.Trim()).ToList();
        var request = new IndicatorRequest(ticker, "3mo", "1d", indicatorList);
        var result = await _client.CalculateIndicatorsAsync(request);

        if (result == null || result.Bars.Count == 0) return $"No indicator data for {ticker}";

        var latest = result.Bars.Last();
        var parts = new List<string> { $"{ticker} latest indicators:" };

        foreach (var (name, value) in latest.Indicators)
        {
            if (value.HasValue)
                parts.Add($"  {name}: {value.Value:F2}");
        }

        return string.Join("\n", parts);
    }

    [KernelFunction("run_screener")]
    [Description("Screen stocks based on technical criteria like price range, volume, RSI")]
    public async Task<string> RunScreenerAsync(
        [Description("Minimum price filter")] double? minPrice = null,
        [Description("Maximum price filter")] double? maxPrice = null,
        [Description("Minimum volume ratio vs 20-day average")] double? minVolumeRatio = null,
        [Description("Minimum RSI value")] double? minRsi = null,
        [Description("Maximum RSI value")] double? maxRsi = null,
        [Description("Stock universe: sp500, nasdaq100")] string universe = "sp500",
        [Description("Max number of results")] int limit = 10)
    {
        var criteria = new ScreenerCriteria(
            Price: (minPrice.HasValue || maxPrice.HasValue) ? new RangeCriteria(minPrice, maxPrice) : null,
            VolumeRatio: minVolumeRatio.HasValue ? new RangeCriteria(minVolumeRatio, null) : null,
            Rsi14: (minRsi.HasValue || maxRsi.HasValue) ? new RangeCriteria(minRsi, maxRsi) : null
        );

        var request = new ScreenerRequest(criteria, universe, null, limit);
        var result = await _client.RunScreenerAsync(request);

        if (result == null || result.Matches.Count == 0) return "No stocks matched the screening criteria.";

        var lines = new List<string> { $"Screener results ({result.Matches.Count} matches, {result.TotalScanned} scanned):" };
        foreach (var match in result.Matches)
        {
            var line = $"  {match.Ticker}: ${match.Price:F2} ({match.ChangePercent:+0.00;-0.00}%) Vol ratio: {match.VolumeRatio:F1}x";
            if (match.Rsi14.HasValue) line += $" RSI: {match.Rsi14:F0}";
            lines.Add(line);
        }

        return string.Join("\n", lines);
    }
}
