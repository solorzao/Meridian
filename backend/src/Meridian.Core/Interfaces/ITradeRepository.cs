using Meridian.Core.Entities;
using Meridian.Core.Enums;

namespace Meridian.Core.Interfaces;

public interface ITradeRepository
{
    Task<Trade?> GetByIdAsync(Guid id, Guid userId);
    Task<IEnumerable<Trade>> GetByUserIdAsync(Guid userId, TradeStatus? status = null, int skip = 0, int take = 50);
    Task<Trade> CreateAsync(Trade trade);
    Task<Trade> UpdateAsync(Trade trade);
    Task DeleteAsync(Guid id, Guid userId);
    Task<int> GetCountByUserIdAsync(Guid userId, TradeStatus? status = null);
}
