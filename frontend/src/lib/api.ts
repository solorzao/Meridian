const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Trades
  getTrades: (status?: string) =>
    fetchApi<TradeResponse[]>(`/api/trades${status ? `?status=${status}` : ''}`),
  getTrade: (id: string) => fetchApi<TradeResponse>(`/api/trades/${id}`),
  createTrade: (data: CreateTradeRequest) =>
    fetchApi<TradeResponse>('/api/trades', { method: 'POST', body: JSON.stringify(data) }),
  updateTrade: (id: string, data: UpdateTradeRequest) =>
    fetchApi<TradeResponse>(`/api/trades/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTrade: (id: string) =>
    fetchApi<void>(`/api/trades/${id}`, { method: 'DELETE' }),

  // Strategies
  getStrategies: () => fetchApi<StrategyResponse[]>('/api/strategies'),
  createStrategy: (data: CreateStrategyRequest) =>
    fetchApi<StrategyResponse>('/api/strategies', { method: 'POST', body: JSON.stringify(data) }),

  // Analytics
  getQuote: (ticker: string) => fetchApi<QuoteData>(`/api/analytics/quote/${ticker}`),
  getOhlcv: (ticker: string, period?: string) =>
    fetchApi<OhlcvData>(`/api/analytics/ohlcv/${ticker}${period ? `?period=${period}` : ''}`),

  // Agents
  chatWithAgent: (agentType: string, message: string, conversationId?: string) =>
    fetchApi<ChatResponse>(`/api/agents/${agentType}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, conversationId }),
    }),
  getConversations: (agentType?: string) =>
    fetchApi<ConversationSummary[]>(`/api/agents/conversations${agentType ? `?agentType=${agentType}` : ''}`),
};

// Types
export interface TradeResponse {
  id: string;
  ticker: string;
  direction: 'Long' | 'Short';
  entryDate: string;
  entryPrice: number;
  exitDate?: string;
  exitPrice?: number;
  positionSize: number;
  stopLoss?: number;
  takeProfit?: number;
  pnl?: number;
  pnlPercent?: number;
  status: 'Open' | 'Closed' | 'Cancelled';
  entryThesis?: string;
  exitThesis?: string;
  marketSentiment?: number;
  emotionalState?: string;
  marketConditions?: string;
  notes?: string;
  strategyTags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateTradeRequest {
  ticker: string;
  direction: 'Long' | 'Short';
  entryDate: string;
  entryPrice: number;
  positionSize: number;
  stopLoss?: number;
  takeProfit?: number;
  entryThesis?: string;
  exitThesis?: string;
  marketSentiment?: number;
  emotionalState?: string;
  marketConditions?: string;
  notes?: string;
  strategyIds?: string[];
}

export interface UpdateTradeRequest {
  exitDate?: string;
  exitPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  status?: 'Open' | 'Closed' | 'Cancelled';
  entryThesis?: string;
  exitThesis?: string;
  marketSentiment?: number;
  emotionalState?: string;
  marketConditions?: string;
  notes?: string;
}

export interface StrategyResponse {
  id: string;
  name: string;
  description?: string;
  source: string;
  createdAt: string;
  tradeCount: number;
}

export interface CreateStrategyRequest {
  name: string;
  description?: string;
}

export interface QuoteData {
  ticker: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
}

export interface OhlcvData {
  ticker: string;
  bars: Array<{ date: string; open: number; high: number; low: number; close: number; volume: number }>;
}

export interface ChatResponse {
  message: string;
}

export interface ConversationSummary {
  id: string;
  agentType: string;
  title: string;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}
