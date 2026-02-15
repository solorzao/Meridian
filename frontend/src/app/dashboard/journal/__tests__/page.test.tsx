import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import JournalPage from '../page';

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe('JournalPage', () => {
  it('renders page header "Trade Journal"', () => {
    render(<JournalPage />);

    expect(screen.getByText('Trade Journal')).toBeInTheDocument();
    expect(
      screen.getByText('Track, review, and learn from every trade.')
    ).toBeInTheDocument();
  });

  it('renders filter tabs: All Trades, Open, Closed', () => {
    render(<JournalPage />);

    expect(screen.getByText('All Trades')).toBeInTheDocument();
    expect(screen.getByText('Open')).toBeInTheDocument();
    expect(screen.getByText('Closed')).toBeInTheDocument();
  });

  it('renders "New Trade" link pointing to /dashboard/journal/new', () => {
    render(<JournalPage />);

    const newTradeLink = screen.getByText('New Trade').closest('a');
    expect(newTradeLink).toBeInTheDocument();
    expect(newTradeLink).toHaveAttribute('href', '/dashboard/journal/new');
  });

  it('renders table headers and empty state', () => {
    render(<JournalPage />);

    // Table headers
    expect(screen.getByText('Date')).toBeInTheDocument();
    expect(screen.getByText('Ticker')).toBeInTheDocument();
    expect(screen.getByText('Direction')).toBeInTheDocument();
    expect(screen.getByText('Entry Price')).toBeInTheDocument();
    expect(screen.getByText('Exit Price')).toBeInTheDocument();
    expect(screen.getByText('P&L')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();

    // Empty state
    expect(screen.getByText('No trades recorded yet')).toBeInTheDocument();
    expect(screen.getByText('Log Your First Trade')).toBeInTheDocument();
  });
});
