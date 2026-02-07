using System.ComponentModel;
using Meridian.Core.Enums;
using Meridian.Core.Interfaces;
using Microsoft.SemanticKernel;

namespace Meridian.Agents.Plugins;

public class TradeHistoryPlugin
{
    private readonly ITradeRepository _tradeRepository;
    private readonly Guid _userId;

    public TradeHistoryPlugin(ITradeRepository tradeRepository, Guid userId)
    {
        _tradeRepository = tradeRepository;
        _userId = userId;
    }

    [KernelFunction("get_open_trades")]
    [Description("Get all currently open trades for the user")]
    public async Task<string> GetOpenTradesAsync()
    {
        var trades = await _tradeRepository.GetByUserIdAsync(_userId, TradeStatus.Open, 0, 100);
        var tradeList = trades.ToList();

        if (tradeList.Count == 0) return "No open trades.";

        var lines = new List<string> { $"Open trades ({tradeList.Count}):" };
        foreach (var t in tradeList)
        {
            var strategyNames = t.StrategyTags?.Select(st => st.Strategy?.Name).Where(n => n != null) ?? Enumerable.Empty<string>();
            lines.Add($"  {t.Ticker} {t.Direction} @ ${t.EntryPrice:F2} ({t.EntryDate:MMM dd}) | " +
                       $"Size: {t.PositionSize} | SL: {(t.StopLoss.HasValue ? $"${t.StopLoss:F2}" : "none")} | " +
                       $"TP: {(t.TakeProfit.HasValue ? $"${t.TakeProfit:F2}" : "none")} | " +
                       $"Tags: [{string.Join(", ", strategyNames)}]");
        }

        return string.Join("\n", lines);
    }

    [KernelFunction("get_recent_closed_trades")]
    [Description("Get recently closed trades with P&L")]
    public async Task<string> GetRecentClosedTradesAsync(
        [Description("Number of recent trades to fetch")] int count = 20)
    {
        var trades = await _tradeRepository.GetByUserIdAsync(_userId, TradeStatus.Closed, 0, count);
        var tradeList = trades.ToList();

        if (tradeList.Count == 0) return "No closed trades found.";

        var totalPnl = tradeList.Where(t => t.Pnl.HasValue).Sum(t => t.Pnl!.Value);
        var winCount = tradeList.Count(t => t.Pnl > 0);

        var lines = new List<string>
        {
            $"Recent closed trades ({tradeList.Count}): Total P&L: ${totalPnl:F2} | Win rate: {(double)winCount / tradeList.Count:P0}"
        };

        foreach (var t in tradeList.Take(10))
        {
            lines.Add($"  {t.Ticker} {t.Direction}: ${t.EntryPrice:F2} → ${t.ExitPrice:F2} | " +
                       $"P&L: ${t.Pnl:F2} ({t.PnlPercent:+0.0;-0.0}%) | {t.EntryDate:MMM dd}-{t.ExitDate:MMM dd}");
        }

        return string.Join("\n", lines);
    }

    [KernelFunction("get_trades_for_ticker")]
    [Description("Get trade history for a specific stock ticker")]
    public async Task<string> GetTradesForTickerAsync(
        [Description("Stock ticker symbol")] string ticker)
    {
        var allTrades = await _tradeRepository.GetByUserIdAsync(_userId, null, 0, 200);
        var tickerTrades = allTrades.Where(t => t.Ticker.Equals(ticker, StringComparison.OrdinalIgnoreCase)).ToList();

        if (tickerTrades.Count == 0) return $"No trade history for {ticker}.";

        var closed = tickerTrades.Where(t => t.Status == TradeStatus.Closed && t.Pnl.HasValue).ToList();
        var totalPnl = closed.Sum(t => t.Pnl!.Value);
        var winRate = closed.Count > 0 ? (double)closed.Count(t => t.Pnl > 0) / closed.Count : 0;

        var lines = new List<string>
        {
            $"{ticker} history: {tickerTrades.Count} trades ({closed.Count} closed) | Total P&L: ${totalPnl:F2} | Win rate: {winRate:P0}"
        };

        foreach (var t in tickerTrades.Take(5))
        {
            var status = t.Status == TradeStatus.Open ? "OPEN" : $"${t.Pnl:F2}";
            lines.Add($"  {t.Direction} @ ${t.EntryPrice:F2} ({t.EntryDate:MMM dd}) → {status}");
        }

        return string.Join("\n", lines);
    }

    [KernelFunction("get_trade_count")]
    [Description("Get the total number of trades for the user")]
    public async Task<string> GetTradeCountAsync()
    {
        var openCount = await _tradeRepository.GetCountByUserIdAsync(_userId, TradeStatus.Open);
        var closedCount = await _tradeRepository.GetCountByUserIdAsync(_userId, TradeStatus.Closed);
        return $"Trade counts: {openCount} open, {closedCount} closed, {openCount + closedCount} total";
    }
}
