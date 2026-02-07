using Meridian.Core.Models;

namespace Meridian.Core.Interfaces;

public interface IUserProfileService
{
    Task<UserProfile?> GetAsync(string userId);
    Task<UserProfile> UpsertAsync(UserProfile profile);
}
