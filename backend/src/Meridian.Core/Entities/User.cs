using Meridian.Core.Enums;

namespace Meridian.Core.Entities;

public class User
{
    public Guid Id { get; set; }
    public required string AzureAdB2CId { get; set; }
    public required string Email { get; set; }
    public string? DisplayName { get; set; }
    public SubscriptionTier SubscriptionTier { get; set; } = SubscriptionTier.Free;
    public string? StripeCustomerId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<Trade> Trades { get; set; } = new List<Trade>();
    public ICollection<Strategy> Strategies { get; set; } = new List<Strategy>();
}
