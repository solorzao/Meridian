using Meridian.Core.Entities;
using Meridian.Core.Interfaces;
using Meridian.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace Meridian.Infrastructure.Repositories;

public class UserRepository : IUserRepository
{
    private readonly MeridianDbContext _context;

    public UserRepository(MeridianDbContext context)
    {
        _context = context;
    }

    public async Task<User?> GetByIdAsync(Guid id)
    {
        return await _context.Users.FindAsync(id);
    }

    public async Task<User?> GetByAzureAdB2CIdAsync(string azureAdB2CId)
    {
        return await _context.Users.FirstOrDefaultAsync(u => u.AzureAdB2CId == azureAdB2CId);
    }

    public async Task<User> CreateAsync(User user)
    {
        _context.Users.Add(user);
        await _context.SaveChangesAsync();
        return user;
    }

    public async Task<User> UpdateAsync(User user)
    {
        user.UpdatedAt = DateTime.UtcNow;
        _context.Users.Update(user);
        await _context.SaveChangesAsync();
        return user;
    }
}
