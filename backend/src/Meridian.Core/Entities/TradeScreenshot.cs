namespace Meridian.Core.Entities;

public class TradeScreenshot
{
    public Guid Id { get; set; }
    public Guid TradeId { get; set; }
    public required string BlobUrl { get; set; }
    public string? Caption { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public Trade? Trade { get; set; }
}
