import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api } from '../api';

const mockFetch = vi.fn();
global.fetch = mockFetch;

function mockJsonResponse(data: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    json: () => Promise.resolve(data),
  };
}

beforeEach(() => {
  mockFetch.mockReset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('api.getTrades', () => {
  it('fetches trades without status filter', async () => {
    const trades = [{ id: '1', ticker: 'AAPL' }];
    mockFetch.mockResolvedValue(mockJsonResponse(trades));

    const result = await api.getTrades();
    expect(result).toEqual(trades);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/trades',
      expect.objectContaining({ headers: expect.objectContaining({ 'Content-Type': 'application/json' }) })
    );
  });

  it('fetches trades with status filter', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse([]));

    await api.getTrades('Open');
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/trades?status=Open',
      expect.any(Object)
    );
  });
});

describe('api.getTrade', () => {
  it('fetches a single trade by id', async () => {
    const trade = { id: 'abc', ticker: 'MSFT' };
    mockFetch.mockResolvedValue(mockJsonResponse(trade));

    const result = await api.getTrade('abc');
    expect(result).toEqual(trade);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/trades/abc',
      expect.any(Object)
    );
  });
});

describe('api.createTrade', () => {
  it('sends POST with trade data', async () => {
    const newTrade = { ticker: 'TSLA', direction: 'Long' as const, entryDate: '2026-01-01', entryPrice: 100, positionSize: 10 };
    const response = { id: '1', ...newTrade };
    mockFetch.mockResolvedValue(mockJsonResponse(response));

    const result = await api.createTrade(newTrade);
    expect(result).toEqual(response);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/trades',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(newTrade),
      })
    );
  });
});

describe('api.updateTrade', () => {
  it('sends PUT with update data', async () => {
    const update = { exitPrice: 120, status: 'Closed' as const };
    mockFetch.mockResolvedValue(mockJsonResponse({ id: '1', ...update }));

    await api.updateTrade('1', update);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/trades/1',
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify(update),
      })
    );
  });
});

describe('api.deleteTrade', () => {
  it('sends DELETE request', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse(undefined));

    await api.deleteTrade('1');
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/trades/1',
      expect.objectContaining({ method: 'DELETE' })
    );
  });
});

describe('api.getStrategies', () => {
  it('fetches strategies', async () => {
    const strategies = [{ id: '1', name: 'Momentum' }];
    mockFetch.mockResolvedValue(mockJsonResponse(strategies));

    const result = await api.getStrategies();
    expect(result).toEqual(strategies);
  });
});

describe('api.createStrategy', () => {
  it('sends POST with strategy data', async () => {
    const data = { name: 'Breakout' };
    mockFetch.mockResolvedValue(mockJsonResponse({ id: '1', ...data }));

    await api.createStrategy(data);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/strategies',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(data),
      })
    );
  });
});

describe('api.getQuote', () => {
  it('fetches quote for ticker', async () => {
    const quote = { ticker: 'AAPL', price: 150 };
    mockFetch.mockResolvedValue(mockJsonResponse(quote));

    const result = await api.getQuote('AAPL');
    expect(result).toEqual(quote);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/analytics/quote/AAPL',
      expect.any(Object)
    );
  });
});

describe('api.getOhlcv', () => {
  it('fetches ohlcv data', async () => {
    const data = { ticker: 'AAPL', bars: [] };
    mockFetch.mockResolvedValue(mockJsonResponse(data));

    const result = await api.getOhlcv('AAPL', '6mo');
    expect(result).toEqual(data);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/analytics/ohlcv/AAPL?period=6mo',
      expect.any(Object)
    );
  });

  it('fetches ohlcv without period', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({ ticker: 'MSFT', bars: [] }));

    await api.getOhlcv('MSFT');
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/analytics/ohlcv/MSFT',
      expect.any(Object)
    );
  });
});

describe('api.chatWithAgent', () => {
  it('sends chat message to agent', async () => {
    const response = { message: 'Response from agent' };
    mockFetch.mockResolvedValue(mockJsonResponse(response));

    const result = await api.chatWithAgent('screener', 'Find momentum stocks');
    expect(result).toEqual(response);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/agents/screener/chat',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ message: 'Find momentum stocks', conversationId: undefined }),
      })
    );
  });

  it('includes conversation ID when provided', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({ message: 'hi' }));

    await api.chatWithAgent('coach', 'Review my trades', 'conv-123');
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/agents/coach/chat',
      expect.objectContaining({
        body: JSON.stringify({ message: 'Review my trades', conversationId: 'conv-123' }),
      })
    );
  });
});

describe('api.getConversations', () => {
  it('fetches conversations', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse([]));

    await api.getConversations();
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/agents/conversations',
      expect.any(Object)
    );
  });

  it('filters by agent type', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse([]));

    await api.getConversations('analyst');
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/agents/conversations?agentType=analyst',
      expect.any(Object)
    );
  });
});

describe('fetchApi error handling', () => {
  it('throws on non-OK responses', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({}, 404));

    await expect(api.getTrades()).rejects.toThrow('API error: 404');
  });

  it('throws on server errors', async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({}, 500));

    await expect(api.getStrategies()).rejects.toThrow('API error: 500');
  });
});
