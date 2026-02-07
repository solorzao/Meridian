namespace Meridian.Core.DTOs;

public record CreateStrategyDto(
    string Name,
    string? Description
);

public record StrategyResponseDto(
    Guid Id,
    string Name,
    string? Description,
    string Source,
    DateTime CreatedAt,
    int TradeCount
);
