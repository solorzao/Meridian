import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import NewTradePage from '../page';

const mockPush = vi.fn();
const mockBack = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush, back: mockBack, replace: vi.fn() }),
}));

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe('NewTradePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.restoreAllMocks();
  });

  it('renders all form fields', () => {
    render(<NewTradePage />);

    // Page heading
    expect(screen.getByText('New Trade')).toBeInTheDocument();
    expect(
      screen.getByText('Record a new trade entry in your journal.')
    ).toBeInTheDocument();

    // Section headings
    expect(screen.getByText('Trade Details')).toBeInTheDocument();
    expect(screen.getByText('Journal Entry')).toBeInTheDocument();

    // Labels
    expect(screen.getByText('Ticker')).toBeInTheDocument();
    expect(screen.getByText('Direction')).toBeInTheDocument();
    expect(screen.getByText('Entry Date')).toBeInTheDocument();
    expect(screen.getByText('Entry Price')).toBeInTheDocument();
    expect(screen.getByText('Position Size')).toBeInTheDocument();
    expect(screen.getByText('Stop Loss')).toBeInTheDocument();
    expect(screen.getByText('Take Profit')).toBeInTheDocument();
    expect(screen.getByText('Thesis')).toBeInTheDocument();
    expect(screen.getByText('Emotional State')).toBeInTheDocument();
    expect(screen.getByText('Notes')).toBeInTheDocument();

    // Buttons
    expect(screen.getByText('Create Trade')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();

    // Back link
    expect(screen.getByText('Back to Journal')).toBeInTheDocument();
    expect(screen.getByText('Back to Journal').closest('a')).toHaveAttribute(
      'href',
      '/dashboard/journal'
    );
  });

  it('converts ticker input to uppercase', async () => {
    const user = userEvent.setup();
    render(<NewTradePage />);

    const tickerInput = screen.getByPlaceholderText('AAPL');
    await user.type(tickerInput, 'msft');

    expect(tickerInput).toHaveValue('MSFT');
  });

  it('submits form with correct payload and navigates on success', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response);

    render(<NewTradePage />);

    // Fill required fields
    const tickerInput = screen.getByPlaceholderText('AAPL');
    await user.type(tickerInput, 'AAPL');

    const entryPriceInput = screen.getByPlaceholderText('0.00');
    await user.type(entryPriceInput, '150.50');

    const positionSizeInput = screen.getByPlaceholderText('100');
    await user.type(positionSizeInput, '50');

    // Submit
    const submitButton = screen.getByText('Create Trade');
    await user.click(submitButton);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    // Verify fetch was called with correct URL and method
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain('/api/trades');
    expect(options).toMatchObject({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    // Verify payload contains the entered data
    const body = JSON.parse(options!.body as string);
    expect(body.ticker).toBe('AAPL');
    expect(body.entryPrice).toBe(150.5);
    expect(body.positionSize).toBe(50);
    expect(body.direction).toBe('Long');

    // Should navigate to journal on success
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard/journal');
    });
  });

  it('shows loading state during submission', async () => {
    const user = userEvent.setup();

    // Use a promise we can control to keep the fetch pending
    let resolvePromise!: (value: Response) => void;
    const pendingPromise = new Promise<Response>((resolve) => {
      resolvePromise = resolve;
    });
    vi.spyOn(global, 'fetch').mockReturnValueOnce(pendingPromise);

    render(<NewTradePage />);

    // Fill required fields
    await user.type(screen.getByPlaceholderText('AAPL'), 'TSLA');
    await user.type(screen.getByPlaceholderText('0.00'), '200');
    await user.type(screen.getByPlaceholderText('100'), '10');

    const submitButton = screen.getByText('Create Trade');
    await user.click(submitButton);

    // Button should show loading text
    await waitFor(() => {
      expect(screen.getByText('Creating...')).toBeInTheDocument();
    });

    // Resolve the fetch to clean up
    resolvePromise({ ok: true, json: async () => ({}) } as Response);

    await waitFor(() => {
      expect(screen.getByText('Create Trade')).toBeInTheDocument();
    });
  });

  it('calls router.back() when Cancel button is clicked', async () => {
    const user = userEvent.setup();
    render(<NewTradePage />);

    const cancelButton = screen.getByText('Cancel');
    await user.click(cancelButton);

    expect(mockBack).toHaveBeenCalledTimes(1);
  });
});
