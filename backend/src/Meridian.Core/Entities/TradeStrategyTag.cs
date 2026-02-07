namespace Meridian.Core.Entities;

public class TradeStrategyTag
{
    public Guid TradeId { get; set; }
    public Guid StrategyId { get; set; }
    public required string Source { get; set; } // "user" or "ai"

    // Navigation properties
    public Trade? Trade { get; set; }
    public Strategy? Strategy { get; set; }
}
