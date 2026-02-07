using Meridian.Core.DTOs;
using Meridian.Core.Entities;
using Meridian.Core.Enums;
using Meridian.Core.Interfaces;

namespace Meridian.Infrastructure.Services;

public class TradeService : ITradeService
{
    private readonly ITradeRepository _tradeRepository;

    public TradeService(ITradeRepository tradeRepository)
    {
        _tradeRepository = tradeRepository;
    }

    public async Task<TradeResponseDto?> GetByIdAsync(Guid id, Guid userId)
    {
        var trade = await _tradeRepository.GetByIdAsync(id, userId);
        return trade != null ? MapToDto(trade) : null;
    }

    public async Task<IEnumerable<TradeResponseDto>> GetByUserIdAsync(Guid userId, TradeStatus? status = null, int skip = 0, int take = 50)
    {
        var trades = await _tradeRepository.GetByUserIdAsync(userId, status, skip, take);
        return trades.Select(MapToDto);
    }

    public async Task<TradeResponseDto> CreateAsync(Guid userId, CreateTradeDto dto)
    {
        var trade = new Trade
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            Ticker = dto.Ticker.ToUpperInvariant(),
            Direction = dto.Direction,
            EntryDate = dto.EntryDate,
            EntryPrice = dto.EntryPrice,
            PositionSize = dto.PositionSize,
            StopLoss = dto.StopLoss,
            TakeProfit = dto.TakeProfit,
            Thesis = dto.Thesis,
            EmotionalState = dto.EmotionalState,
            MarketConditions = dto.MarketConditions,
            Notes = dto.Notes,
            Status = TradeStatus.Open,
        };

        if (dto.StrategyIds?.Any() == true)
        {
            foreach (var strategyId in dto.StrategyIds)
            {
                trade.StrategyTags.Add(new TradeStrategyTag
                {
                    TradeId = trade.Id,
                    StrategyId = strategyId,
                    Source = "user",
                });
            }
        }

        var created = await _tradeRepository.CreateAsync(trade);
        return MapToDto(created);
    }

    public async Task<TradeResponseDto> UpdateAsync(Guid id, Guid userId, UpdateTradeDto dto)
    {
        var trade = await _tradeRepository.GetByIdAsync(id, userId)
            ?? throw new InvalidOperationException($"Trade {id} not found");

        if (dto.ExitDate.HasValue) trade.ExitDate = dto.ExitDate;
        if (dto.ExitPrice.HasValue) trade.ExitPrice = dto.ExitPrice;
        if (dto.StopLoss.HasValue) trade.StopLoss = dto.StopLoss;
        if (dto.TakeProfit.HasValue) trade.TakeProfit = dto.TakeProfit;
        if (dto.Status.HasValue) trade.Status = dto.Status.Value;
        if (dto.Thesis != null) trade.Thesis = dto.Thesis;
        if (dto.EmotionalState != null) trade.EmotionalState = dto.EmotionalState;
        if (dto.MarketConditions != null) trade.MarketConditions = dto.MarketConditions;
        if (dto.Notes != null) trade.Notes = dto.Notes;

        // Calculate P&L if trade is being closed
        if (trade.ExitPrice.HasValue && trade.Status == TradeStatus.Closed)
        {
            var multiplier = trade.Direction == TradeDirection.Long ? 1 : -1;
            trade.Pnl = (trade.ExitPrice.Value - trade.EntryPrice) * trade.PositionSize * multiplier;
            trade.PnlPercent = trade.EntryPrice != 0
                ? (trade.ExitPrice.Value - trade.EntryPrice) / trade.EntryPrice * 100 * multiplier
                : 0;
        }

        var updated = await _tradeRepository.UpdateAsync(trade);
        return MapToDto(updated);
    }

    public async Task DeleteAsync(Guid id, Guid userId)
    {
        await _tradeRepository.DeleteAsync(id, userId);
    }

    private static TradeResponseDto MapToDto(Trade trade)
    {
        return new TradeResponseDto(
            Id: trade.Id,
            Ticker: trade.Ticker,
            Direction: trade.Direction,
            EntryDate: trade.EntryDate,
            EntryPrice: trade.EntryPrice,
            ExitDate: trade.ExitDate,
            ExitPrice: trade.ExitPrice,
            PositionSize: trade.PositionSize,
            StopLoss: trade.StopLoss,
            TakeProfit: trade.TakeProfit,
            Pnl: trade.Pnl,
            PnlPercent: trade.PnlPercent,
            Status: trade.Status,
            Thesis: trade.Thesis,
            EmotionalState: trade.EmotionalState,
            MarketConditions: trade.MarketConditions,
            Notes: trade.Notes,
            StrategyTags: trade.StrategyTags?
                .Select(st => st.Strategy?.Name ?? "Unknown")
                .ToList() ?? new List<string>(),
            CreatedAt: trade.CreatedAt,
            UpdatedAt: trade.UpdatedAt
        );
    }
}
