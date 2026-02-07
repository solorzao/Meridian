using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;

namespace Meridian.Agents.Agents;

public abstract class BaseAgent
{
    protected readonly Kernel Kernel;
    protected readonly IChatCompletionService ChatService;
    protected readonly ChatHistory ChatHistory;

    protected BaseAgent(Kernel kernel, string systemPrompt)
    {
        Kernel = kernel;
        ChatService = kernel.GetRequiredService<IChatCompletionService>();
        ChatHistory = new ChatHistory(systemPrompt);
    }

    public abstract string AgentType { get; }

    public async Task<string> ChatAsync(string userMessage)
    {
        ChatHistory.AddUserMessage(userMessage);

        var settings = new PromptExecutionSettings
        {
            FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
        };

        var response = await ChatService.GetChatMessageContentAsync(
            ChatHistory,
            settings,
            Kernel
        );

        var assistantMessage = response.Content ?? "I'm sorry, I couldn't generate a response.";
        ChatHistory.AddAssistantMessage(assistantMessage);

        return assistantMessage;
    }

    public void AddContext(string context)
    {
        ChatHistory.AddSystemMessage(context);
    }
}
