namespace Meridian.Core.Entities;

public class Strategy
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public required string Source { get; set; } // "user" or "ai"
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public User? User { get; set; }
    public ICollection<TradeStrategyTag> TradeStrategyTags { get; set; } = new List<TradeStrategyTag>();
}
