using Meridian.Core.Interfaces;
using Meridian.Core.Models;
using Microsoft.Azure.Cosmos;
using Microsoft.Azure.Cosmos.Linq;

namespace Meridian.Infrastructure.Cosmos;

public class CosmosAgentConfigService : IAgentConfigService
{
    private readonly Container _container;

    public CosmosAgentConfigService(CosmosClient cosmosClient, string databaseName = "meridian")
    {
        _container = cosmosClient.GetContainer(databaseName, "agent_configs");
    }

    public async Task<AgentConfig?> GetAsync(string userId, string agentType)
    {
        var iterator = _container.GetItemLinqQueryable<AgentConfig>()
            .Where(c => c.UserId == userId && c.AgentType == agentType)
            .ToFeedIterator();

        if (iterator.HasMoreResults)
        {
            var response = await iterator.ReadNextAsync();
            return response.FirstOrDefault();
        }

        return null;
    }

    public async Task<IEnumerable<AgentConfig>> GetAllForUserAsync(string userId)
    {
        var iterator = _container.GetItemLinqQueryable<AgentConfig>()
            .Where(c => c.UserId == userId)
            .ToFeedIterator();

        var results = new List<AgentConfig>();
        while (iterator.HasMoreResults)
        {
            var response = await iterator.ReadNextAsync();
            results.AddRange(response);
        }

        return results;
    }

    public async Task<AgentConfig> UpsertAsync(AgentConfig config)
    {
        config.UpdatedAt = DateTime.UtcNow;
        var response = await _container.UpsertItemAsync(config, new PartitionKey(config.UserId));
        return response.Resource;
    }
}
