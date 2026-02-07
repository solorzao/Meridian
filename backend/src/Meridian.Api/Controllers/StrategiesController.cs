using Meridian.Core.DTOs;
using Meridian.Core.Entities;
using Meridian.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace Meridian.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StrategiesController : ControllerBase
{
    private readonly IStrategyRepository _strategyRepository;

    public StrategiesController(IStrategyRepository strategyRepository)
    {
        _strategyRepository = strategyRepository;
    }

    private Guid GetUserId() => Guid.Parse("00000000-0000-0000-0000-000000000001");

    [HttpGet]
    public async Task<ActionResult<IEnumerable<StrategyResponseDto>>> GetStrategies()
    {
        var strategies = await _strategyRepository.GetByUserIdAsync(GetUserId());
        var dtos = strategies.Select(s => new StrategyResponseDto(
            s.Id, s.Name, s.Description, s.Source, s.CreatedAt,
            s.TradeStrategyTags?.Count ?? 0
        ));
        return Ok(dtos);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<StrategyResponseDto>> GetStrategy(Guid id)
    {
        var strategy = await _strategyRepository.GetByIdAsync(id, GetUserId());
        if (strategy == null) return NotFound();

        return Ok(new StrategyResponseDto(
            strategy.Id, strategy.Name, strategy.Description, strategy.Source,
            strategy.CreatedAt, strategy.TradeStrategyTags?.Count ?? 0
        ));
    }

    [HttpPost]
    public async Task<ActionResult<StrategyResponseDto>> CreateStrategy([FromBody] CreateStrategyDto dto)
    {
        var strategy = new Strategy
        {
            Id = Guid.NewGuid(),
            UserId = GetUserId(),
            Name = dto.Name,
            Description = dto.Description,
            Source = "user",
        };

        var created = await _strategyRepository.CreateAsync(strategy);
        var response = new StrategyResponseDto(
            created.Id, created.Name, created.Description, created.Source, created.CreatedAt, 0
        );
        return CreatedAtAction(nameof(GetStrategy), new { id = response.Id }, response);
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> DeleteStrategy(Guid id)
    {
        await _strategyRepository.DeleteAsync(id, GetUserId());
        return NoContent();
    }
}
