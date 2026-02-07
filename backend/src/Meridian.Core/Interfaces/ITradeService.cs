using Meridian.Core.DTOs;
using Meridian.Core.Enums;

namespace Meridian.Core.Interfaces;

public interface ITradeService
{
    Task<TradeResponseDto?> GetByIdAsync(Guid id, Guid userId);
    Task<IEnumerable<TradeResponseDto>> GetByUserIdAsync(Guid userId, TradeStatus? status = null, int skip = 0, int take = 50);
    Task<TradeResponseDto> CreateAsync(Guid userId, CreateTradeDto dto);
    Task<TradeResponseDto> UpdateAsync(Guid id, Guid userId, UpdateTradeDto dto);
    Task DeleteAsync(Guid id, Guid userId);
}
