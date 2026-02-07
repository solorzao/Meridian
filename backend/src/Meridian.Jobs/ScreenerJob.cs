using Meridian.Core.Interfaces;
using Meridian.Infrastructure.Http;
using Microsoft.Extensions.Logging;

namespace Meridian.Jobs;

public class ScreenerJob
{
    private readonly IAgentConfigService? _agentConfigService;
    private readonly PythonAnalyticsClient _analyticsClient;
    private readonly ILogger<ScreenerJob> _logger;

    public ScreenerJob(
        PythonAnalyticsClient analyticsClient,
        ILogger<ScreenerJob> logger,
        IAgentConfigService? agentConfigService = null)
    {
        _analyticsClient = analyticsClient;
        _logger = logger;
        _agentConfigService = agentConfigService;
    }

    public async Task ExecuteAsync(string userId)
    {
        _logger.LogInformation("Running screener job for user {UserId}", userId);

        if (_agentConfigService == null)
        {
            _logger.LogWarning("AgentConfigService not available, skipping screener job");
            return;
        }

        var config = await _agentConfigService.GetAsync(userId, "screener");
        if (config == null || !config.IsEnabled)
        {
            _logger.LogInformation("Screener not configured or disabled for user {UserId}", userId);
            return;
        }

        // Run screener with user's saved criteria
        var request = new ScreenerRequest(
            new ScreenerCriteria(),
            "sp500",
            null,
            20
        );

        var results = await _analyticsClient.RunScreenerAsync(request);
        _logger.LogInformation("Screener found {Count} matches for user {UserId}",
            results?.Matches.Count ?? 0, userId);

        // TODO: Store results and notify user
    }
}
