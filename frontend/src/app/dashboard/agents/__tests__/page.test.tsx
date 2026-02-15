import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AgentsPage from '../page';

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn(), replace: vi.fn() }),
  usePathname: () => '/dashboard/agents',
}));

describe('AgentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.restoreAllMocks();
  });

  it('renders agent cards when no agent is selected', () => {
    render(<AgentsPage />);

    // Page heading
    expect(screen.getByText('AI Agents')).toBeInTheDocument();
    expect(
      screen.getByText('Intelligent assistants to enhance your trading workflow.')
    ).toBeInTheDocument();

    // Agent cards
    expect(screen.getByText('Screener Agent')).toBeInTheDocument();
    expect(
      screen.getByText('Find stocks matching your criteria using AI-powered screening')
    ).toBeInTheDocument();

    expect(screen.getByText('Analyst Agent')).toBeInTheDocument();
    expect(
      screen.getByText('Deep analysis of your open positions and market conditions')
    ).toBeInTheDocument();

    expect(screen.getByText('Coach Agent')).toBeInTheDocument();
    expect(
      screen.getByText('Review your trading patterns and get personalized coaching')
    ).toBeInTheDocument();

    // Each card should have "Start conversation"
    const startConvoTexts = screen.getAllByText('Start conversation');
    expect(startConvoTexts).toHaveLength(3);
  });

  it('clicking agent card shows chat interface', async () => {
    const user = userEvent.setup();
    render(<AgentsPage />);

    // Click the Screener Agent card
    const screenerButton = screen.getByText('Screener Agent').closest('button')!;
    await user.click(screenerButton);

    // Chat interface should be visible with agent name in header
    // The agent name appears in the chat header
    await waitFor(() => {
      // Chat input should be visible
      expect(screen.getByPlaceholderText('Ask your agent...')).toBeInTheDocument();
    });

    // The empty chat state message
    expect(screen.getByText('Start a conversation')).toBeInTheDocument();
  });

  it('back button returns to agent selection', async () => {
    const user = userEvent.setup();
    render(<AgentsPage />);

    // Select an agent
    const analystButton = screen.getByText('Analyst Agent').closest('button')!;
    await user.click(analystButton);

    // Chat interface should show
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Ask your agent...')).toBeInTheDocument();
    });

    // Click the back button (first button in the chat interface, which is the ArrowLeft)
    // In the chat view, the buttons are: back arrow, send button
    const buttons = screen.getAllByRole('button');
    // The back button is the first button in the chat header
    const backButton = buttons[0];
    await user.click(backButton);

    // Should be back on agent selection
    await waitFor(() => {
      expect(screen.getByText('Screener Agent')).toBeInTheDocument();
      expect(screen.getByText('Analyst Agent')).toBeInTheDocument();
      expect(screen.getByText('Coach Agent')).toBeInTheDocument();
    });
  });

  it('sending a message calls fetch and displays messages', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Here is my analysis of AAPL.' }),
    } as Response);

    render(<AgentsPage />);

    // Select Coach Agent
    const coachButton = screen.getByText('Coach Agent').closest('button')!;
    await user.click(coachButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Ask your agent...')).toBeInTheDocument();
    });

    // Type and send a message
    const input = screen.getByPlaceholderText('Ask your agent...');
    await user.type(input, 'Analyze my recent trades');
    await user.keyboard('{Enter}');

    // User message should appear
    await waitFor(() => {
      expect(screen.getByText('Analyze my recent trades')).toBeInTheDocument();
    });

    // Verify fetch was called
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain('/api/agents/coach/chat');
    expect(options).toMatchObject({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const body = JSON.parse(options!.body as string);
    expect(body.message).toBe('Analyze my recent trades');

    // Assistant response should appear
    await waitFor(() => {
      expect(screen.getByText('Here is my analysis of AAPL.')).toBeInTheDocument();
    });
  });

  it('shows loading indicator while waiting for response', async () => {
    const user = userEvent.setup();

    let resolvePromise!: (value: Response) => void;
    const pendingPromise = new Promise<Response>((resolve) => {
      resolvePromise = resolve;
    });
    vi.spyOn(global, 'fetch').mockReturnValueOnce(pendingPromise);

    render(<AgentsPage />);

    // Select Screener Agent
    const screenerButton = screen.getByText('Screener Agent').closest('button')!;
    await user.click(screenerButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Ask your agent...')).toBeInTheDocument();
    });

    // Type and send a message
    const input = screen.getByPlaceholderText('Ask your agent...');
    await user.type(input, 'Find me tech stocks');
    await user.keyboard('{Enter}');

    // Loading indicator should appear with "Thinking" text
    await waitFor(() => {
      expect(screen.getByText('Thinking')).toBeInTheDocument();
    });

    // Resolve the fetch
    resolvePromise({
      ok: true,
      json: async () => ({ message: 'Found 5 matching stocks.' }),
    } as Response);

    // Loading should disappear and response should appear
    await waitFor(() => {
      expect(screen.queryByText('Thinking')).not.toBeInTheDocument();
      expect(screen.getByText('Found 5 matching stocks.')).toBeInTheDocument();
    });
  });
});
