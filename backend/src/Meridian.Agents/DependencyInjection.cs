using Meridian.Agents.Configuration;
using Meridian.Agents.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Meridian.Agents;

public static class DependencyInjection
{
    public static IServiceCollection AddAgents(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddSemanticKernel(configuration);
        services.AddScoped<AgentOrchestrator>();

        return services;
    }
}
