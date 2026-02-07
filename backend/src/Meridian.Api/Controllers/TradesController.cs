using Meridian.Core.DTOs;
using Meridian.Core.Enums;
using Meridian.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace Meridian.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
// [Authorize] // Uncomment when auth is configured
public class TradesController : ControllerBase
{
    private readonly ITradeService _tradeService;

    public TradesController(ITradeService tradeService)
    {
        _tradeService = tradeService;
    }

    // TODO: Replace with actual user ID from auth claims
    private Guid GetUserId() => Guid.Parse("00000000-0000-0000-0000-000000000001");

    [HttpGet]
    public async Task<ActionResult<IEnumerable<TradeResponseDto>>> GetTrades(
        [FromQuery] TradeStatus? status = null,
        [FromQuery] int skip = 0,
        [FromQuery] int take = 50)
    {
        var trades = await _tradeService.GetByUserIdAsync(GetUserId(), status, skip, take);
        return Ok(trades);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<TradeResponseDto>> GetTrade(Guid id)
    {
        var trade = await _tradeService.GetByIdAsync(id, GetUserId());
        return trade != null ? Ok(trade) : NotFound();
    }

    [HttpPost]
    public async Task<ActionResult<TradeResponseDto>> CreateTrade([FromBody] CreateTradeDto dto)
    {
        var trade = await _tradeService.CreateAsync(GetUserId(), dto);
        return CreatedAtAction(nameof(GetTrade), new { id = trade.Id }, trade);
    }

    [HttpPut("{id:guid}")]
    public async Task<ActionResult<TradeResponseDto>> UpdateTrade(Guid id, [FromBody] UpdateTradeDto dto)
    {
        var trade = await _tradeService.UpdateAsync(id, GetUserId(), dto);
        return Ok(trade);
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> DeleteTrade(Guid id)
    {
        await _tradeService.DeleteAsync(id, GetUserId());
        return NoContent();
    }
}
