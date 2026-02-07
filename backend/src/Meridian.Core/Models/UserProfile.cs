namespace Meridian.Core.Models;

public class UserProfile
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public required string UserId { get; set; }
    public string? TradingStyle { get; set; }
    public List<string> PreferredSectors { get; set; } = new();
    public List<string> WatchlistTickers { get; set; } = new();
    public Dictionary<string, double> StrategyPerformance { get; set; } = new();
    public string? RiskProfile { get; set; }
    public DateTime LastRefreshed { get; set; } = DateTime.UtcNow;
}
