import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DashboardPage from '../page';

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe('DashboardPage', () => {
  it('renders stat cards: Open Trades, Total P&L, Win Rate, Profit Factor', () => {
    render(<DashboardPage />);

    expect(screen.getByText('Open Trades')).toBeInTheDocument();
    expect(screen.getByText('Total P&L')).toBeInTheDocument();
    expect(screen.getByText('Win Rate')).toBeInTheDocument();
    expect(screen.getByText('Profit Factor')).toBeInTheDocument();
  });

  it('renders quick action cards: Log a Trade, Chat with Agent, View Analytics', () => {
    render(<DashboardPage />);

    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Log a Trade')).toBeInTheDocument();
    expect(screen.getByText('Chat with Agent')).toBeInTheDocument();
    expect(screen.getByText('View Analytics')).toBeInTheDocument();

    // Check quick action descriptions
    expect(screen.getByText('Record a new trade entry')).toBeInTheDocument();
    expect(screen.getByText('Get AI-powered insights')).toBeInTheDocument();
    expect(screen.getByText('Check your performance')).toBeInTheDocument();

    // Check quick action links
    const logTradeLink = screen.getByText('Log a Trade').closest('a');
    expect(logTradeLink).toHaveAttribute('href', '/dashboard/journal');

    const chatLink = screen.getByText('Chat with Agent').closest('a');
    expect(chatLink).toHaveAttribute('href', '/dashboard/agents');

    const analyticsLink = screen.getByText('View Analytics').closest('a');
    expect(analyticsLink).toHaveAttribute('href', '/dashboard/analytics');
  });

  it('renders Recent Trades and Agent Insights sections', () => {
    render(<DashboardPage />);

    expect(screen.getByText('Recent Trades')).toBeInTheDocument();
    expect(screen.getByText('Agent Insights')).toBeInTheDocument();

    // Check empty states
    expect(screen.getByText('No trades yet')).toBeInTheDocument();
    expect(screen.getByText('Your AI co-pilot awaits')).toBeInTheDocument();

    // Check links in sections
    expect(screen.getByText('View All')).toBeInTheDocument();
    expect(screen.getByText('Open Chat')).toBeInTheDocument();
    expect(screen.getByText('Log Your First Trade')).toBeInTheDocument();
    expect(screen.getByText('Start a Conversation')).toBeInTheDocument();
  });
});
