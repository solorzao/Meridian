using Meridian.Core.Enums;
using Meridian.Core.Interfaces;
using Meridian.Core.Models;
using Microsoft.Extensions.Logging;

namespace Meridian.Jobs;

public class ProfileRefreshJob
{
    private readonly ITradeRepository _tradeRepository;
    private readonly IUserProfileService? _profileService;
    private readonly ILogger<ProfileRefreshJob> _logger;

    public ProfileRefreshJob(
        ITradeRepository tradeRepository,
        ILogger<ProfileRefreshJob> logger,
        IUserProfileService? profileService = null)
    {
        _tradeRepository = tradeRepository;
        _logger = logger;
        _profileService = profileService;
    }

    public async Task ExecuteAsync(Guid userId, string userIdString)
    {
        _logger.LogInformation("Refreshing trading profile for user {UserId}", userId);

        if (_profileService == null)
        {
            _logger.LogWarning("UserProfileService not available, skipping profile refresh");
            return;
        }

        var closedTrades = await _tradeRepository.GetByUserIdAsync(userId, TradeStatus.Closed, 0, 500);
        var tradeList = closedTrades.ToList();

        if (tradeList.Count == 0) return;

        // Analyze trading patterns
        var strategyPerformance = new Dictionary<string, double>();
        var strategyGroups = tradeList
            .SelectMany(t => t.StrategyTags?.Select(st => new { Strategy = st.Strategy?.Name ?? "Unknown", t.Pnl }) ?? Enumerable.Empty<dynamic>())
            .GroupBy(x => (string)x.Strategy);

        foreach (var group in strategyGroups)
        {
            var trades = group.ToList();
            var wins = trades.Count(t => t.Pnl > 0);
            strategyPerformance[group.Key] = trades.Count > 0 ? (double)wins / trades.Count : 0;
        }

        // Determine trading style
        var avgHoldDays = tradeList
            .Where(t => t.ExitDate.HasValue)
            .Select(t => (t.ExitDate!.Value - t.EntryDate).TotalDays)
            .DefaultIfEmpty(0)
            .Average();

        var tradingStyle = avgHoldDays switch
        {
            < 1 => "Day Trader",
            < 5 => "Swing Trader",
            < 30 => "Position Trader",
            _ => "Investor"
        };

        // Get most-traded tickers as watchlist candidates
        var topTickers = tradeList
            .GroupBy(t => t.Ticker)
            .OrderByDescending(g => g.Count())
            .Take(10)
            .Select(g => g.Key)
            .ToList();

        var profile = await _profileService.GetAsync(userIdString) ?? new UserProfile
        {
            UserId = userIdString,
        };

        profile.TradingStyle = tradingStyle;
        profile.StrategyPerformance = strategyPerformance;
        profile.WatchlistTickers = topTickers;
        profile.LastRefreshed = DateTime.UtcNow;

        await _profileService.UpsertAsync(profile);

        _logger.LogInformation("Profile refreshed for user {UserId}: style={Style}, strategies={Count}",
            userId, tradingStyle, strategyPerformance.Count);
    }
}
