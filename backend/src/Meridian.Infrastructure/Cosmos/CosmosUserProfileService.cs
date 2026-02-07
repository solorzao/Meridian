using Meridian.Core.Interfaces;
using Meridian.Core.Models;
using Microsoft.Azure.Cosmos;

namespace Meridian.Infrastructure.Cosmos;

public class CosmosUserProfileService : IUserProfileService
{
    private readonly Container _container;

    public CosmosUserProfileService(CosmosClient cosmosClient, string databaseName = "meridian")
    {
        _container = cosmosClient.GetContainer(databaseName, "user_profiles");
    }

    public async Task<UserProfile?> GetAsync(string userId)
    {
        try
        {
            var response = await _container.ReadItemAsync<UserProfile>(userId, new PartitionKey(userId));
            return response.Resource;
        }
        catch (CosmosException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return null;
        }
    }

    public async Task<UserProfile> UpsertAsync(UserProfile profile)
    {
        var response = await _container.UpsertItemAsync(profile, new PartitionKey(profile.UserId));
        return response.Resource;
    }
}
