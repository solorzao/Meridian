using Meridian.Core.Enums;

namespace Meridian.Core.DTOs;

public record CreateTradeDto(
    string Ticker,
    TradeDirection Direction,
    DateTime EntryDate,
    decimal EntryPrice,
    decimal PositionSize,
    decimal? StopLoss,
    decimal? TakeProfit,
    string? Thesis,
    string? EmotionalState,
    string? MarketConditions,
    string? Notes,
    List<Guid>? StrategyIds
);

public record UpdateTradeDto(
    DateTime? ExitDate,
    decimal? ExitPrice,
    decimal? StopLoss,
    decimal? TakeProfit,
    TradeStatus? Status,
    string? Thesis,
    string? EmotionalState,
    string? MarketConditions,
    string? Notes,
    List<Guid>? StrategyIds
);

public record TradeResponseDto(
    Guid Id,
    string Ticker,
    TradeDirection Direction,
    DateTime EntryDate,
    decimal EntryPrice,
    DateTime? ExitDate,
    decimal? ExitPrice,
    decimal PositionSize,
    decimal? StopLoss,
    decimal? TakeProfit,
    decimal? Pnl,
    decimal? PnlPercent,
    TradeStatus Status,
    string? Thesis,
    string? EmotionalState,
    string? MarketConditions,
    string? Notes,
    List<string> StrategyTags,
    DateTime CreatedAt,
    DateTime UpdatedAt
);
