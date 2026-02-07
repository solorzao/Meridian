using System.ComponentModel;
using Meridian.Core.Interfaces;
using Microsoft.SemanticKernel;

namespace Meridian.Agents.Plugins;

public class UserProfilePlugin
{
    private readonly IUserProfileService _profileService;
    private readonly string _userId;

    public UserProfilePlugin(IUserProfileService profileService, string userId)
    {
        _profileService = profileService;
        _userId = userId;
    }

    [KernelFunction("get_user_profile")]
    [Description("Get the user's trading profile including style, preferred sectors, and watchlist")]
    public async Task<string> GetUserProfileAsync()
    {
        var profile = await _profileService.GetAsync(_userId);
        if (profile == null) return "No user profile found. This appears to be a new user.";

        var lines = new List<string>
        {
            "User Trading Profile:",
            $"  Trading Style: {profile.TradingStyle ?? "Not set"}",
            $"  Risk Profile: {profile.RiskProfile ?? "Not set"}",
            $"  Preferred Sectors: {(profile.PreferredSectors.Any() ? string.Join(", ", profile.PreferredSectors) : "None set")}",
            $"  Watchlist: {(profile.WatchlistTickers.Any() ? string.Join(", ", profile.WatchlistTickers) : "Empty")}",
            $"  Last Refreshed: {profile.LastRefreshed:MMM dd, yyyy}",
        };

        if (profile.StrategyPerformance.Any())
        {
            lines.Add("  Strategy Performance:");
            foreach (var (strategy, winRate) in profile.StrategyPerformance)
            {
                lines.Add($"    {strategy}: {winRate:P0} win rate");
            }
        }

        return string.Join("\n", lines);
    }

    [KernelFunction("get_watchlist")]
    [Description("Get the user's stock watchlist")]
    public async Task<string> GetWatchlistAsync()
    {
        var profile = await _profileService.GetAsync(_userId);
        if (profile == null || !profile.WatchlistTickers.Any())
            return "Watchlist is empty.";

        return $"Watchlist: {string.Join(", ", profile.WatchlistTickers)}";
    }
}
