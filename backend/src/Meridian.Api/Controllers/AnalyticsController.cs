using Meridian.Infrastructure.Http;
using Microsoft.AspNetCore.Mvc;

namespace Meridian.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AnalyticsController : ControllerBase
{
    private readonly PythonAnalyticsClient _analyticsClient;

    public AnalyticsController(PythonAnalyticsClient analyticsClient)
    {
        _analyticsClient = analyticsClient;
    }

    [HttpGet("quote/{ticker}")]
    public async Task<IActionResult> GetQuote(string ticker)
    {
        var quote = await _analyticsClient.GetQuoteAsync(ticker);
        return Ok(quote);
    }

    [HttpGet("ohlcv/{ticker}")]
    public async Task<IActionResult> GetOhlcv(string ticker, [FromQuery] string period = "1y", [FromQuery] string interval = "1d")
    {
        var data = await _analyticsClient.GetOhlcvAsync(ticker, period, interval);
        return Ok(data);
    }

    [HttpPost("indicators")]
    public async Task<IActionResult> CalculateIndicators([FromBody] IndicatorRequest request)
    {
        var result = await _analyticsClient.CalculateIndicatorsAsync(request);
        return Ok(result);
    }

    [HttpPost("screen")]
    public async Task<IActionResult> RunScreener([FromBody] ScreenerRequest request)
    {
        var result = await _analyticsClient.RunScreenerAsync(request);
        return Ok(result);
    }
}
