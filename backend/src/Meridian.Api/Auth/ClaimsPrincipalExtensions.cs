using System.Security.Claims;

namespace Meridian.Api.Auth;

public static class ClaimsPrincipalExtensions
{
    public static string? GetAzureAdB2CId(this ClaimsPrincipal principal)
    {
        return principal.FindFirstValue(ClaimTypes.NameIdentifier)
            ?? principal.FindFirstValue("sub");
    }

    public static string? GetEmail(this ClaimsPrincipal principal)
    {
        return principal.FindFirstValue(ClaimTypes.Email)
            ?? principal.FindFirstValue("emails");
    }

    public static string? GetDisplayName(this ClaimsPrincipal principal)
    {
        return principal.FindFirstValue("name")
            ?? principal.FindFirstValue(ClaimTypes.GivenName);
    }
}
