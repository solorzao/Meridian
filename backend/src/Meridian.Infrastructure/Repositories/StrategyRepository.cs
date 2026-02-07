using Meridian.Core.Entities;
using Meridian.Core.Interfaces;
using Meridian.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace Meridian.Infrastructure.Repositories;

public class StrategyRepository : IStrategyRepository
{
    private readonly MeridianDbContext _context;

    public StrategyRepository(MeridianDbContext context)
    {
        _context = context;
    }

    public async Task<Strategy?> GetByIdAsync(Guid id, Guid userId)
    {
        return await _context.Strategies
            .Include(s => s.TradeStrategyTags)
            .FirstOrDefaultAsync(s => s.Id == id && s.UserId == userId);
    }

    public async Task<IEnumerable<Strategy>> GetByUserIdAsync(Guid userId)
    {
        return await _context.Strategies
            .Include(s => s.TradeStrategyTags)
            .Where(s => s.UserId == userId)
            .OrderBy(s => s.Name)
            .ToListAsync();
    }

    public async Task<Strategy> CreateAsync(Strategy strategy)
    {
        _context.Strategies.Add(strategy);
        await _context.SaveChangesAsync();
        return strategy;
    }

    public async Task<Strategy> UpdateAsync(Strategy strategy)
    {
        _context.Strategies.Update(strategy);
        await _context.SaveChangesAsync();
        return strategy;
    }

    public async Task DeleteAsync(Guid id, Guid userId)
    {
        var strategy = await _context.Strategies.FirstOrDefaultAsync(s => s.Id == id && s.UserId == userId);
        if (strategy != null)
        {
            _context.Strategies.Remove(strategy);
            await _context.SaveChangesAsync();
        }
    }
}
