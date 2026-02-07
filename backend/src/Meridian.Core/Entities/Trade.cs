using Meridian.Core.Enums;

namespace Meridian.Core.Entities;

public class Trade
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public required string Ticker { get; set; }
    public TradeDirection Direction { get; set; }
    public DateTime EntryDate { get; set; }
    public decimal EntryPrice { get; set; }
    public DateTime? ExitDate { get; set; }
    public decimal? ExitPrice { get; set; }
    public decimal PositionSize { get; set; }
    public decimal? StopLoss { get; set; }
    public decimal? TakeProfit { get; set; }
    public decimal? Pnl { get; set; }
    public decimal? PnlPercent { get; set; }
    public TradeStatus Status { get; set; } = TradeStatus.Open;
    public string? Thesis { get; set; }
    public string? EmotionalState { get; set; }
    public string? MarketConditions { get; set; }
    public string? Notes { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public User? User { get; set; }
    public ICollection<TradeStrategyTag> StrategyTags { get; set; } = new List<TradeStrategyTag>();
    public ICollection<TradeScreenshot> Screenshots { get; set; } = new List<TradeScreenshot>();
}
