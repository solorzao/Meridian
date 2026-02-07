using Meridian.Agents.Agents;
using Meridian.Agents.Plugins;
using Meridian.Core.Interfaces;
using Meridian.Core.Models;
using Meridian.Infrastructure.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;

namespace Meridian.Agents.Services;

public class AgentOrchestrator
{
    private readonly IServiceProvider _serviceProvider;

    public AgentOrchestrator(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    public async Task<string> ChatAsync(string agentType, string userId, Guid userGuid, string message, string? conversationId = null)
    {
        // Load or create conversation
        var conversationService = _serviceProvider.GetService<IConversationService>();
        Conversation? conversation = null;

        if (conversationId != null && conversationService != null)
        {
            conversation = await conversationService.GetByIdAsync(conversationId, userId);
        }

        if (conversation == null && conversationService != null)
        {
            conversation = await conversationService.CreateAsync(new Conversation
            {
                UserId = userId,
                AgentType = agentType,
                Title = message.Length > 50 ? message[..50] + "..." : message,
            });
        }

        // Create agent with plugins
        var agent = CreateAgent(agentType, userId, userGuid);

        // Add conversation history as context
        if (conversation?.Messages.Any() == true)
        {
            foreach (var msg in conversation.Messages.TakeLast(20))
            {
                if (msg.Role == "user")
                    agent.AddContext($"[Previous user message]: {msg.Content}");
                else if (msg.Role == "assistant")
                    agent.AddContext($"[Previous assistant response]: {msg.Content}");
            }
        }

        // Get response
        var response = await agent.ChatAsync(message);

        // Save messages
        if (conversation != null && conversationService != null)
        {
            await conversationService.AddMessageAsync(conversation.Id, userId,
                new ChatMessage { Role = "user", Content = message });
            await conversationService.AddMessageAsync(conversation.Id, userId,
                new ChatMessage { Role = "assistant", Content = response });
        }

        return response;
    }

    private BaseAgent CreateAgent(string agentType, string userId, Guid userGuid)
    {
        var baseKernel = _serviceProvider.GetRequiredService<Kernel>();
        var kernelBuilder = Kernel.CreateBuilder();

        // Copy AI service from the base kernel
        foreach (var service in baseKernel.GetAllServices<Microsoft.SemanticKernel.ChatCompletion.IChatCompletionService>())
        {
            kernelBuilder.Services.AddSingleton(service);
        }

        var kernel = kernelBuilder.Build();

        // Add plugins
        var analyticsClient = _serviceProvider.GetRequiredService<PythonAnalyticsClient>();
        kernel.ImportPluginFromObject(new MarketDataPlugin(analyticsClient), "MarketData");

        var tradeRepository = _serviceProvider.GetRequiredService<ITradeRepository>();
        kernel.ImportPluginFromObject(new TradeHistoryPlugin(tradeRepository, userGuid), "TradeHistory");

        var profileService = _serviceProvider.GetService<IUserProfileService>();
        if (profileService != null)
        {
            kernel.ImportPluginFromObject(new UserProfilePlugin(profileService, userId), "UserProfile");
        }

        return agentType.ToLower() switch
        {
            "screener" => new ScreenerAgent(kernel),
            "analyst" => new AnalystAgent(kernel),
            "coach" => new CoachAgent(kernel),
            _ => throw new ArgumentException($"Unknown agent type: {agentType}")
        };
    }
}
