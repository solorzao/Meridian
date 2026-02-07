using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;

namespace Meridian.Agents.Configuration;

public static class SemanticKernelConfig
{
    public static IServiceCollection AddSemanticKernel(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddSingleton<Kernel>(sp =>
        {
            var builder = Kernel.CreateBuilder();

            var endpoint = configuration["AzureOpenAI:Endpoint"] ?? "";
            var apiKey = configuration["AzureOpenAI:ApiKey"] ?? "";
            var deploymentName = configuration["AzureOpenAI:DeploymentName"] ?? "gpt-4o";

            if (!string.IsNullOrEmpty(endpoint) && !string.IsNullOrEmpty(apiKey))
            {
                builder.AddAzureOpenAIChatCompletion(deploymentName, endpoint, apiKey);
            }

            return builder.Build();
        });

        return services;
    }
}
