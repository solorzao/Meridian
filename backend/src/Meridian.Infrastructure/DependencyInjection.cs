using Meridian.Core.Interfaces;
using Meridian.Infrastructure.Cosmos;
using Meridian.Infrastructure.Data;
using Meridian.Infrastructure.Http;
using Meridian.Infrastructure.Repositories;
using Meridian.Infrastructure.Services;
using Microsoft.Azure.Cosmos;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Meridian.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        // Entity Framework
        services.AddDbContext<MeridianDbContext>(options =>
            options.UseSqlServer(
                configuration.GetConnectionString("SqlConnection"),
                b => b.MigrationsAssembly(typeof(MeridianDbContext).Assembly.FullName)
            )
        );

        // Repositories
        services.AddScoped<ITradeRepository, TradeRepository>();
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IStrategyRepository, StrategyRepository>();

        // Services
        services.AddScoped<ITradeService, TradeService>();

        // Cosmos DB (only register if connection string is configured)
        var cosmosConnection = configuration.GetConnectionString("CosmosConnection");
        if (!string.IsNullOrEmpty(cosmosConnection))
        {
            services.AddSingleton(sp =>
            {
                return new CosmosClient(cosmosConnection, new CosmosClientOptions
                {
                    SerializerOptions = new CosmosSerializationOptions
                    {
                        PropertyNamingPolicy = CosmosPropertyNamingPolicy.CamelCase
                    }
                });
            });

            services.AddScoped<IConversationService, CosmosConversationService>();
            services.AddScoped<IAgentConfigService, CosmosAgentConfigService>();
            services.AddScoped<IUserProfileService, CosmosUserProfileService>();
        }

        // Python Analytics HTTP Client
        var pythonServiceUrl = configuration["Services:PythonAnalytics"] ?? "http://localhost:8000";
        services.AddHttpClient<PythonAnalyticsClient>(client =>
        {
            client.BaseAddress = new Uri(pythonServiceUrl);
            client.Timeout = TimeSpan.FromSeconds(30);
        });

        return services;
    }
}
