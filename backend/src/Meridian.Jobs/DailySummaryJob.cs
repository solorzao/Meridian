using Meridian.Core.Enums;
using Meridian.Core.Interfaces;
using Meridian.Infrastructure.Http;
using Microsoft.Extensions.Logging;

namespace Meridian.Jobs;

public class DailySummaryJob
{
    private readonly ITradeRepository _tradeRepository;
    private readonly PythonAnalyticsClient _analyticsClient;
    private readonly ILogger<DailySummaryJob> _logger;

    public DailySummaryJob(
        ITradeRepository tradeRepository,
        PythonAnalyticsClient analyticsClient,
        ILogger<DailySummaryJob> logger)
    {
        _tradeRepository = tradeRepository;
        _analyticsClient = analyticsClient;
        _logger = logger;
    }

    public async Task ExecuteAsync(Guid userId)
    {
        _logger.LogInformation("Generating daily summary for user {UserId}", userId);

        var openTrades = await _tradeRepository.GetByUserIdAsync(userId, TradeStatus.Open, 0, 100);
        var openList = openTrades.ToList();

        if (openList.Count == 0)
        {
            _logger.LogInformation("No open trades for user {UserId}, skipping summary", userId);
            return;
        }

        // Fetch current quotes for all open positions
        foreach (var trade in openList)
        {
            try
            {
                var quote = await _analyticsClient.GetQuoteAsync(trade.Ticker);
                if (quote != null)
                {
                    var unrealizedPnl = trade.Direction == TradeDirection.Long
                        ? (decimal)(quote.Price) - trade.EntryPrice
                        : trade.EntryPrice - (decimal)(quote.Price);

                    _logger.LogInformation(
                        "Position {Ticker}: Entry ${EntryPrice:F2}, Current ${CurrentPrice:F2}, Unrealized P&L: ${Pnl:F2}",
                        trade.Ticker, trade.EntryPrice, quote.Price, unrealizedPnl * trade.PositionSize);
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to fetch quote for {Ticker}", trade.Ticker);
            }
        }

        // TODO: Format summary and send via email/notification
    }
}
