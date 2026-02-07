using Meridian.Core.Models;

namespace Meridian.Core.Interfaces;

public interface IAgentConfigService
{
    Task<AgentConfig?> GetAsync(string userId, string agentType);
    Task<IEnumerable<AgentConfig>> GetAllForUserAsync(string userId);
    Task<AgentConfig> UpsertAsync(AgentConfig config);
}
