using Meridian.Infrastructure.Services;
using Microsoft.AspNetCore.Mvc;

namespace Meridian.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class BillingController : ControllerBase
{
    private readonly StripeService _stripeService;

    public BillingController(StripeService stripeService)
    {
        _stripeService = stripeService;
    }

    private Guid GetUserId() => Guid.Parse("00000000-0000-0000-0000-000000000001");

    [HttpPost("checkout")]
    public async Task<IActionResult> CreateCheckout([FromBody] CheckoutRequest request)
    {
        var url = await _stripeService.CreateCheckoutSessionAsync(
            GetUserId(), request.SuccessUrl, request.CancelUrl);
        return Ok(new { url });
    }

    [HttpPost("portal")]
    public async Task<IActionResult> CreatePortal([FromBody] PortalRequest request)
    {
        var url = await _stripeService.CreatePortalSessionAsync(GetUserId(), request.ReturnUrl);
        return Ok(new { url });
    }

    [HttpPost("webhook")]
    public async Task<IActionResult> Webhook()
    {
        var json = await new StreamReader(HttpContext.Request.Body).ReadToEndAsync();
        var signature = Request.Headers["Stripe-Signature"].FirstOrDefault() ?? "";

        await _stripeService.HandleWebhookAsync(json, signature);
        return Ok();
    }
}

public record CheckoutRequest(string SuccessUrl, string CancelUrl);
public record PortalRequest(string ReturnUrl);
