using Meridian.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace Meridian.Jobs;

public class EmbeddingJob
{
    private readonly ITradeRepository _tradeRepository;
    private readonly ILogger<EmbeddingJob> _logger;

    public EmbeddingJob(ITradeRepository tradeRepository, ILogger<EmbeddingJob> logger)
    {
        _tradeRepository = tradeRepository;
        _logger = logger;
    }

    public async Task ExecuteAsync(Guid tradeId, Guid userId)
    {
        _logger.LogInformation("Generating embedding for trade {TradeId}", tradeId);

        var trade = await _tradeRepository.GetByIdAsync(tradeId, userId);
        if (trade == null)
        {
            _logger.LogWarning("Trade {TradeId} not found for embedding", tradeId);
            return;
        }

        // Build text representation for embedding
        var tradeText = $"{trade.Ticker} {trade.Direction} trade. " +
                       $"Entry: ${trade.EntryPrice:F2} on {trade.EntryDate:yyyy-MM-dd}. " +
                       (trade.ExitPrice.HasValue ? $"Exit: ${trade.ExitPrice:F2} on {trade.ExitDate:yyyy-MM-dd}. " : "") +
                       (trade.Pnl.HasValue ? $"P&L: ${trade.Pnl:F2}. " : "") +
                       (trade.Thesis != null ? $"Thesis: {trade.Thesis}. " : "") +
                       (trade.Notes != null ? $"Notes: {trade.Notes}." : "");

        // TODO: Call Azure OpenAI embeddings API and store vector
        // var embedding = await _openAIClient.GetEmbeddingAsync(tradeText);
        // await _embeddingRepository.StoreAsync(tradeId, embedding);

        _logger.LogInformation("Embedding generated for trade {TradeId} ({Length} chars)", tradeId, tradeText.Length);
    }
}
