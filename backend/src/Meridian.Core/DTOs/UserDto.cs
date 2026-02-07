using Meridian.Core.Enums;

namespace Meridian.Core.DTOs;

public record UserProfileDto(
    Guid Id,
    string Email,
    string? DisplayName,
    SubscriptionTier SubscriptionTier,
    DateTime CreatedAt
);
