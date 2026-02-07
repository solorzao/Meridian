'use client';

import { useState } from 'react';
import { Search, BarChart3, GraduationCap, ArrowLeft, Send, Bot, Sparkles } from 'lucide-react';

const agentTypes = [
  {
    id: 'screener',
    name: 'Screener Agent',
    description: 'Find stocks matching your criteria using AI-powered screening',
    icon: Search,
    color: '#3B82F6',
    bg: 'bg-blue-500/10',
  },
  {
    id: 'analyst',
    name: 'Analyst Agent',
    description: 'Deep analysis of your open positions and market conditions',
    icon: BarChart3,
    color: '#10B981',
    bg: 'bg-emerald-500/10',
  },
  {
    id: 'coach',
    name: 'Coach Agent',
    description: 'Review your trading patterns and get personalized coaching',
    icon: GraduationCap,
    color: '#F59E0B',
    bg: 'bg-amber-500/10',
  },
];

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const activeAgent = agentTypes.find((a) => a.id === selectedAgent);

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
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-meridian-text-heading">AI Agents</h1>
        <p className="text-meridian-text-muted text-sm mt-1">
          Intelligent assistants to enhance your trading workflow.
        </p>
      </div>

      {!selectedAgent ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {agentTypes.map((agent) => {
            const Icon = agent.icon;
            return (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent.id)}
                className="group relative meridian-card-hover p-6 text-left overflow-hidden"
              >
                {/* Colored left border */}
                <div
                  className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
                  style={{ backgroundColor: agent.color }}
                />
                <div className="relative">
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${agent.bg}`}
                  >
                    <Icon className="h-6 w-6" style={{ color: agent.color }} />
                  </div>
                  <h3 className="text-lg font-semibold text-meridian-text-heading mb-1.5">{agent.name}</h3>
                  <p className="text-sm text-meridian-text-muted leading-relaxed">{agent.description}</p>
                  <div className="mt-4 flex items-center gap-1.5 text-xs font-medium" style={{ color: agent.color }}>
                    <Sparkles className="h-3.5 w-3.5" />
                    Start conversation
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      ) : (
        /* Chat interface -- dark/navy for terminal feel */
        <div className="bg-meridian-navy-800 rounded-xl border border-meridian-navy-200 flex flex-col h-[600px] overflow-hidden shadow-meridian-lg">
          {/* Chat Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/10 bg-meridian-navy-800">
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setSelectedAgent(null);
                  setMessages([]);
                }}
                className="p-1.5 rounded-lg text-meridian-slate-300 hover:text-white hover:bg-white/10 transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
              </button>
              {activeAgent && (
                <>
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${activeAgent.color}20` }}
                  >
                    <activeAgent.icon className="h-4 w-4" style={{ color: activeAgent.color }} />
                  </div>
                  <div>
                    <h2 className="font-semibold text-white text-sm">{activeAgent.name}</h2>
                    <p className="text-xs text-meridian-slate-400">Online</p>
                  </div>
                </>
              )}
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs text-meridian-slate-400">Ready</span>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-auto p-5 space-y-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-14 h-14 rounded-2xl bg-meridian-navy-950 border border-white/10 flex items-center justify-center mb-4">
                  <Bot className="h-7 w-7 text-meridian-slate-400" />
                </div>
                <p className="text-white font-medium mb-1">Start a conversation</p>
                <p className="text-meridian-slate-400 text-sm max-w-xs">
                  Ask your {activeAgent?.name?.toLowerCase()} anything about your trading.
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[80%] rounded-xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-meridian-crimson text-white rounded-br-sm'
                      : 'bg-meridian-navy-950 text-meridian-slate-100 border border-white/10 rounded-bl-sm'
                  }`}
                >
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{msg.content}</pre>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-meridian-navy-950 border border-white/10 rounded-xl rounded-bl-sm px-4 py-3">
                  <div className="flex items-center gap-2 text-meridian-slate-300 text-sm">
                    <div className="flex gap-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-meridian-slate-300 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-1.5 h-1.5 rounded-full bg-meridian-slate-300 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-1.5 h-1.5 rounded-full bg-meridian-slate-300 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    Thinking
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="px-5 py-4 border-t border-white/10 bg-meridian-navy-800">
            <div className="flex gap-3">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask your agent..."
                className="flex-1 rounded-xl border border-white/10 bg-meridian-navy-950 px-4 py-2.5 text-sm text-white placeholder-meridian-slate-400 focus:outline-none focus:ring-2 focus:ring-meridian-crimson/50 focus:border-meridian-crimson transition-colors"
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !message.trim()}
                className="rounded-xl bg-meridian-crimson px-4 py-2.5 text-white text-sm font-medium hover:bg-meridian-crimson-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
