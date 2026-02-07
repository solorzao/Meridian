'use client';

import { useState } from 'react';

const agentTypes = [
  { id: 'screener', name: 'Screener Agent', description: 'Find stocks matching your criteria', emoji: '🔍' },
  { id: 'analyst', name: 'Analyst Agent', description: 'Analyze your open positions', emoji: '📊' },
  { id: 'coach', name: 'Coach Agent', description: 'Review your trading performance', emoji: '🎯' },
];

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim() || !selectedAgent || isLoading) return;

    const userMessage = message;
    setMessage('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/api/agents/${selectedAgent}/chat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userMessage }),
        }
      );
      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'assistant', content: data.message }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">AI Agents</h1>

      {!selectedAgent ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {agentTypes.map((agent) => (
            <button
              key={agent.id}
              onClick={() => setSelectedAgent(agent.id)}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:border-blue-500 transition-colors text-left"
            >
              <span className="text-3xl">{agent.emoji}</span>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-3">{agent.name}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{agent.description}</p>
            </button>
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col h-[600px]">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="font-semibold text-gray-900 dark:text-white">
              {agentTypes.find((a) => a.id === selectedAgent)?.name}
            </h2>
            <button
              onClick={() => { setSelectedAgent(null); setMessages([]); }}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Back
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-auto p-4 space-y-4">
            {messages.length === 0 && (
              <p className="text-center text-gray-400 mt-8">Start a conversation with your AI agent.</p>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                }`}>
                  <pre className="whitespace-pre-wrap font-sans text-sm">{msg.content}</pre>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2 text-gray-500">
                  Thinking...
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask your agent..."
                className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSend}
                disabled={isLoading}
                className="rounded-lg bg-blue-600 px-4 py-2 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
