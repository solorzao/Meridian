using System.Threading.RateLimiting;
using Microsoft.AspNetCore.RateLimiting;

namespace Meridian.Api.Middleware;

public static class RateLimitingConfig
{
    public static IServiceCollection AddRateLimiting(this IServiceCollection services)
    {
        services.AddRateLimiter(options =>
        {
            options.RejectionStatusCode = 429;

            // Global rate limit
            options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
                RateLimitPartition.GetFixedWindowLimiter(
                    context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                    _ => new FixedWindowRateLimiterOptions
                    {
                        PermitLimit = 100,
                        Window = TimeSpan.FromMinutes(1),
                    }));

            // Stricter limit for agent chat endpoints
            options.AddFixedWindowLimiter("AgentChat", opt =>
            {
                opt.PermitLimit = 20;
                opt.Window = TimeSpan.FromMinutes(1);
            });

            // Stricter limit for screener (heavy API calls)
            options.AddFixedWindowLimiter("Screener", opt =>
            {
                opt.PermitLimit = 5;
                opt.Window = TimeSpan.FromMinutes(1);
            });
        });

        return services;
    }
}
