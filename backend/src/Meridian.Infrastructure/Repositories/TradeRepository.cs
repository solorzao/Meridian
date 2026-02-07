using Meridian.Core.Entities;
using Meridian.Core.Enums;
using Meridian.Core.Interfaces;
using Meridian.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace Meridian.Infrastructure.Repositories;

public class TradeRepository : ITradeRepository
{
    private readonly MeridianDbContext _context;

    public TradeRepository(MeridianDbContext context)
    {
        _context = context;
    }

    public async Task<Trade?> GetByIdAsync(Guid id, Guid userId)
    {
        return await _context.Trades
            .Include(t => t.StrategyTags)
                .ThenInclude(st => st.Strategy)
            .Include(t => t.Screenshots)
            .FirstOrDefaultAsync(t => t.Id == id && t.UserId == userId);
    }

    public async Task<IEnumerable<Trade>> GetByUserIdAsync(Guid userId, TradeStatus? status = null, int skip = 0, int take = 50)
    {
        var query = _context.Trades
            .Include(t => t.StrategyTags)
                .ThenInclude(st => st.Strategy)
            .Where(t => t.UserId == userId);

        if (status.HasValue)
        {
            query = query.Where(t => t.Status == status.Value);
        }

        return await query
            .OrderByDescending(t => t.EntryDate)
            .Skip(skip)
            .Take(take)
            .ToListAsync();
    }

    public async Task<Trade> CreateAsync(Trade trade)
    {
        _context.Trades.Add(trade);
        await _context.SaveChangesAsync();
        return trade;
    }

    public async Task<Trade> UpdateAsync(Trade trade)
    {
        trade.UpdatedAt = DateTime.UtcNow;
        _context.Trades.Update(trade);
        await _context.SaveChangesAsync();
        return trade;
    }

    public async Task DeleteAsync(Guid id, Guid userId)
    {
        var trade = await _context.Trades.FirstOrDefaultAsync(t => t.Id == id && t.UserId == userId);
        if (trade != null)
        {
            _context.Trades.Remove(trade);
            await _context.SaveChangesAsync();
        }
    }

    public async Task<int> GetCountByUserIdAsync(Guid userId, TradeStatus? status = null)
    {
        var query = _context.Trades.Where(t => t.UserId == userId);

        if (status.HasValue)
        {
            query = query.Where(t => t.Status == status.Value);
        }

        return await query.CountAsync();
    }
}
