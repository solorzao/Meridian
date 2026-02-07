using Meridian.Agents.Services;
using Meridian.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace Meridian.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AgentsController : ControllerBase
{
    private readonly AgentOrchestrator _orchestrator;
    private readonly IConversationService? _conversationService;

    public AgentsController(AgentOrchestrator orchestrator, IConversationService? conversationService = null)
    {
        _orchestrator = orchestrator;
        _conversationService = conversationService;
    }

    private Guid GetUserId() => Guid.Parse("00000000-0000-0000-0000-000000000001");
    private string GetUserIdString() => "00000000-0000-0000-0000-000000000001";

    [HttpPost("{agentType}/chat")]
    public async Task<IActionResult> Chat(string agentType, [FromBody] ChatRequest request)
    {
        var validTypes = new[] { "screener", "analyst", "coach" };
        if (!validTypes.Contains(agentType.ToLower()))
        {
            return BadRequest(new { error = $"Invalid agent type. Must be one of: {string.Join(", ", validTypes)}" });
        }

        var response = await _orchestrator.ChatAsync(
            agentType.ToLower(),
            GetUserIdString(),
            GetUserId(),
            request.Message,
            request.ConversationId
        );

        return Ok(new ChatResponse(response));
    }

    [HttpGet("conversations")]
    public async Task<IActionResult> GetConversations([FromQuery] string? agentType = null, [FromQuery] int limit = 20)
    {
        if (_conversationService == null)
            return Ok(Array.Empty<object>());

        var conversations = await _conversationService.GetByUserIdAsync(GetUserIdString(), agentType, limit);
        return Ok(conversations.Select(c => new
        {
            c.Id,
            c.AgentType,
            c.Title,
            MessageCount = c.Messages.Count,
            c.CreatedAt,
            c.UpdatedAt,
        }));
    }

    [HttpGet("conversations/{id}")]
    public async Task<IActionResult> GetConversation(string id)
    {
        if (_conversationService == null)
            return NotFound();

        var conversation = await _conversationService.GetByIdAsync(id, GetUserIdString());
        return conversation != null ? Ok(conversation) : NotFound();
    }

    [HttpDelete("conversations/{id}")]
    public async Task<IActionResult> DeleteConversation(string id)
    {
        if (_conversationService == null)
            return NotFound();

        await _conversationService.DeleteAsync(id, GetUserIdString());
        return NoContent();
    }
}

public record ChatRequest(string Message, string? ConversationId = null);
public record ChatResponse(string Message);
