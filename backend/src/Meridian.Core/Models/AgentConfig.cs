namespace Meridian.Core.Models;

public class AgentConfig
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public required string UserId { get; set; }
    public required string AgentType { get; set; }
    public string? CustomSystemPrompt { get; set; }
    public Dictionary<string, object> Settings { get; set; } = new();
    public bool IsEnabled { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
