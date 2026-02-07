using System.Net.Http.Json;

namespace Meridian.Infrastructure.Http;

public class PythonAnalyticsClient
{
    private readonly HttpClient _httpClient;

    public PythonAnalyticsClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<OhlcvResponse?> GetOhlcvAsync(string ticker, string period = "1y", string interval = "1d")
    {
        var response = await _httpClient.GetAsync($"/market-data/{ticker}?period={period}&interval={interval}");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<OhlcvResponse>();
    }

    public async Task<QuoteResponse?> GetQuoteAsync(string ticker)
    {
        var response = await _httpClient.GetAsync($"/market-data/quote/{ticker}");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<QuoteResponse>();
    }

    public async Task<IndicatorResponse?> CalculateIndicatorsAsync(IndicatorRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync("/indicators", request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<IndicatorResponse>();
    }

    public async Task<ScreenerResponse?> RunScreenerAsync(ScreenerRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync("/screen", request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ScreenerResponse>();
    }

    public async Task<PerformanceResponse?> CalculatePerformanceAsync(List<TradeInputDto> trades)
    {
        var response = await _httpClient.PostAsJsonAsync("/stats/performance", trades);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<PerformanceResponse>();
    }
}

// DTOs matching the Python service API
public record OhlcvBar(DateTime Date, double Open, double High, double Low, double Close, long Volume);
public record OhlcvResponse(string Ticker, List<OhlcvBar> Bars, string Period, string Interval);
public record QuoteResponse(string Ticker, double Price, double Change, double ChangePercent, long Volume, DateTime Timestamp);

public record IndicatorRequest(
    string Ticker,
    string Period = "1y",
    string Interval = "1d",
    List<string>? Indicators = null
);
public record IndicatorBar(string Date, double Open, double High, double Low, double Close, long Volume, Dictionary<string, double?> Indicators);
public record IndicatorResponse(string Ticker, List<IndicatorBar> Bars, List<string> IndicatorsCalculated);

public record RangeCriteria(double? Min = null, double? Max = null);
public record ScreenerCriteria(
    RangeCriteria? Price = null,
    RangeCriteria? GapPercent = null,
    RangeCriteria? VolumeRatio = null,
    int? MinVolume = null,
    RangeCriteria? Rsi14 = null
);
public record ScreenerRequest(
    ScreenerCriteria Criteria,
    string Universe = "sp500",
    List<string>? CustomTickers = null,
    int Limit = 20
);
public record ScreenerMatch(
    string Ticker, string? Name, double Price, double ChangePercent,
    long Volume, double? VolumeRatio, double? Rsi14, double? GapPercent,
    string? Sector, long? MarketCap
);
public record ScreenerResponse(List<ScreenerMatch> Matches, int TotalScanned, string CriteriaSummary);

public record TradeInputDto(
    string Id, string Ticker, string Direction, DateTime EntryDate,
    double EntryPrice, DateTime? ExitDate, double? ExitPrice,
    double PositionSize, double? Pnl, List<string> StrategyTags
);
public record PerformanceStatsDto(
    int TotalTrades, int WinningTrades, int LosingTrades, double WinRate,
    double ProfitFactor, double TotalPnl, double AvgWin, double AvgLoss,
    double LargestWin, double LargestLoss, double AvgHoldDays, double Expectancy
);
public record StrategyStatsDto(string StrategyName, int TotalTrades, double WinRate, double ProfitFactor, double TotalPnl, double AvgPnl);
public record PerformanceResponse(
    PerformanceStatsDto Overall,
    List<StrategyStatsDto> ByStrategy,
    Dictionary<string, PerformanceStatsDto> ByTicker,
    Dictionary<string, double> MonthlyPnl
);
