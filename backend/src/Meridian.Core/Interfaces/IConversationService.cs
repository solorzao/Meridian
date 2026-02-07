using Meridian.Core.Models;

namespace Meridian.Core.Interfaces;

public interface IConversationService
{
    Task<Conversation?> GetByIdAsync(string id, string userId);
    Task<IEnumerable<Conversation>> GetByUserIdAsync(string userId, string? agentType = null, int limit = 20);
    Task<Conversation> CreateAsync(Conversation conversation);
    Task<Conversation> AddMessageAsync(string id, string userId, ChatMessage message);
    Task DeleteAsync(string id, string userId);
}
