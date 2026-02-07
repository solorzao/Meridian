namespace Meridian.Core.Models;

public class Conversation
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public required string UserId { get; set; }
    public required string AgentType { get; set; } // "screener", "analyst", "coach"
    public string? Title { get; set; }
    public List<ChatMessage> Messages { get; set; } = new();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}

public class ChatMessage
{
    public required string Role { get; set; } // "user", "assistant", "system"
    public required string Content { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}
