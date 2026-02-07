using Meridian.Core.Entities;
using Meridian.Core.Enums;
using Meridian.Core.Interfaces;
using Microsoft.Extensions.Configuration;
using Stripe;
using Stripe.Checkout;

namespace Meridian.Infrastructure.Services;

public class StripeService
{
    private readonly IConfiguration _configuration;
    private readonly IUserRepository _userRepository;

    public StripeService(IConfiguration configuration, IUserRepository userRepository)
    {
        _configuration = configuration;
        _userRepository = userRepository;
        StripeConfiguration.ApiKey = configuration["Stripe:SecretKey"];
    }

    public async Task<string> CreateCheckoutSessionAsync(Guid userId, string successUrl, string cancelUrl)
    {
        var user = await _userRepository.GetByIdAsync(userId)
            ?? throw new InvalidOperationException("User not found");

        // Ensure customer exists in Stripe
        if (string.IsNullOrEmpty(user.StripeCustomerId))
        {
            var customerService = new CustomerService();
            var customer = await customerService.CreateAsync(new CustomerCreateOptions
            {
                Email = user.Email,
                Metadata = new Dictionary<string, string>
                {
                    { "meridian_user_id", userId.ToString() }
                }
            });

            user.StripeCustomerId = customer.Id;
            await _userRepository.UpdateAsync(user);
        }

        var options = new SessionCreateOptions
        {
            Customer = user.StripeCustomerId,
            PaymentMethodTypes = new List<string> { "card" },
            LineItems = new List<SessionLineItemOptions>
            {
                new()
                {
                    Price = _configuration["Stripe:PremiumPriceId"],
                    Quantity = 1,
                }
            },
            Mode = "subscription",
            SuccessUrl = successUrl,
            CancelUrl = cancelUrl,
        };

        var service = new SessionService();
        var session = await service.CreateAsync(options);
        return session.Url;
    }

    public async Task HandleWebhookAsync(string json, string signature)
    {
        var webhookSecret = _configuration["Stripe:WebhookSecret"];
        var stripeEvent = EventUtility.ConstructEvent(json, signature, webhookSecret);

        switch (stripeEvent.Type)
        {
            case EventTypes.CheckoutSessionCompleted:
                await HandleCheckoutCompleted(stripeEvent);
                break;
            case EventTypes.CustomerSubscriptionDeleted:
                await HandleSubscriptionCancelled(stripeEvent);
                break;
        }
    }

    private async Task HandleCheckoutCompleted(Event stripeEvent)
    {
        var session = stripeEvent.Data.Object as Session;
        if (session?.Customer is null) return;

        var customerService = new CustomerService();
        var customer = await customerService.GetAsync(session.Customer.ToString()!);

        if (customer.Metadata.TryGetValue("meridian_user_id", out var userIdStr) &&
            Guid.TryParse(userIdStr, out var userId))
        {
            var user = await _userRepository.GetByIdAsync(userId);
            if (user != null)
            {
                user.SubscriptionTier = SubscriptionTier.Premium;
                await _userRepository.UpdateAsync(user);
            }
        }
    }

    private async Task HandleSubscriptionCancelled(Event stripeEvent)
    {
        var subscription = stripeEvent.Data.Object as Stripe.Subscription;
        if (subscription?.Customer is null) return;

        var customerService = new CustomerService();
        var customer = await customerService.GetAsync(subscription.Customer.ToString()!);

        if (customer.Metadata.TryGetValue("meridian_user_id", out var userIdStr) &&
            Guid.TryParse(userIdStr, out var userId))
        {
            var user = await _userRepository.GetByIdAsync(userId);
            if (user != null)
            {
                user.SubscriptionTier = SubscriptionTier.Free;
                await _userRepository.UpdateAsync(user);
            }
        }
    }

    public async Task<string> CreatePortalSessionAsync(Guid userId, string returnUrl)
    {
        var user = await _userRepository.GetByIdAsync(userId)
            ?? throw new InvalidOperationException("User not found");

        if (string.IsNullOrEmpty(user.StripeCustomerId))
            throw new InvalidOperationException("No Stripe customer found");

        var options = new Stripe.BillingPortal.SessionCreateOptions
        {
            Customer = user.StripeCustomerId,
            ReturnUrl = returnUrl,
        };

        var service = new Stripe.BillingPortal.SessionService();
        var session = await service.CreateAsync(options);
        return session.Url;
    }
}
