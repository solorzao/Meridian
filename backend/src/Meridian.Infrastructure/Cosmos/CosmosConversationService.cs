using Meridian.Core.Interfaces;
using Meridian.Core.Models;
using Microsoft.Azure.Cosmos;
using Microsoft.Azure.Cosmos.Linq;

namespace Meridian.Infrastructure.Cosmos;

public class CosmosConversationService : IConversationService
{
    private readonly Container _container;

    public CosmosConversationService(CosmosClient cosmosClient, string databaseName = "meridian")
    {
        _container = cosmosClient.GetContainer(databaseName, "conversations");
    }

    public async Task<Conversation?> GetByIdAsync(string id, string userId)
    {
        try
        {
            var response = await _container.ReadItemAsync<Conversation>(id, new PartitionKey(userId));
            return response.Resource;
        }
        catch (CosmosException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return null;
        }
    }

    public async Task<IEnumerable<Conversation>> GetByUserIdAsync(string userId, string? agentType = null, int limit = 20)
    {
        var queryable = _container.GetItemLinqQueryable<Conversation>()
            .Where(c => c.UserId == userId);

        if (!string.IsNullOrEmpty(agentType))
        {
            queryable = queryable.Where(c => c.AgentType == agentType);
        }

        var iterator = queryable
            .OrderByDescending(c => c.UpdatedAt)
            .Take(limit)
            .ToFeedIterator();

        var results = new List<Conversation>();
        while (iterator.HasMoreResults)
        {
            var response = await iterator.ReadNextAsync();
            results.AddRange(response);
        }

        return results;
    }

    public async Task<Conversation> CreateAsync(Conversation conversation)
    {
        var response = await _container.CreateItemAsync(conversation, new PartitionKey(conversation.UserId));
        return response.Resource;
    }

    public async Task<Conversation> AddMessageAsync(string id, string userId, ChatMessage message)
    {
        var conversation = await GetByIdAsync(id, userId)
            ?? throw new InvalidOperationException($"Conversation {id} not found");

        conversation.Messages.Add(message);
        conversation.UpdatedAt = DateTime.UtcNow;

        var response = await _container.ReplaceItemAsync(conversation, id, new PartitionKey(userId));
        return response.Resource;
    }

    public async Task DeleteAsync(string id, string userId)
    {
        await _container.DeleteItemAsync<Conversation>(id, new PartitionKey(userId));
    }
}
