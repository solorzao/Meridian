using Meridian.Core.Entities;

namespace Meridian.Core.Interfaces;

public interface IStrategyRepository
{
    Task<Strategy?> GetByIdAsync(Guid id, Guid userId);
    Task<IEnumerable<Strategy>> GetByUserIdAsync(Guid userId);
    Task<Strategy> CreateAsync(Strategy strategy);
    Task<Strategy> UpdateAsync(Strategy strategy);
    Task DeleteAsync(Guid id, Guid userId);
}
