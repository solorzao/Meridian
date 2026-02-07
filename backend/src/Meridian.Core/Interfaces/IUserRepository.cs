using Meridian.Core.Entities;

namespace Meridian.Core.Interfaces;

public interface IUserRepository
{
    Task<User?> GetByIdAsync(Guid id);
    Task<User?> GetByAzureAdB2CIdAsync(string azureAdB2CId);
    Task<User> CreateAsync(User user);
    Task<User> UpdateAsync(User user);
}
