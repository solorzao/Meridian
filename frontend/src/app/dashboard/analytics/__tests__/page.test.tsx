import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import AnalyticsPage from '../page';

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe('AnalyticsPage', () => {
  it('renders page header', () => {
    render(<AnalyticsPage />);

    expect(screen.getByText('Analytics')).toBeInTheDocument();
    expect(
      screen.getByText('Insights and performance metrics for your trading activity.')
    ).toBeInTheDocument();
  });

  it('renders stat cards: Total P&L, Win Rate, Avg R:R, Total Trades', () => {
    render(<AnalyticsPage />);

    expect(screen.getByText('Total P&L')).toBeInTheDocument();
    expect(screen.getByText('Win Rate')).toBeInTheDocument();
    expect(screen.getByText('Avg R:R')).toBeInTheDocument();
    expect(screen.getByText('Total Trades')).toBeInTheDocument();

    // Check stat values
    expect(screen.getByText('$0.00')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('renders chart sections: P&L Over Time, Strategy Breakdown, Monthly Performance', () => {
    render(<AnalyticsPage />);

    expect(screen.getByText('P&L Over Time')).toBeInTheDocument();
    expect(screen.getByText('Cumulative profit and loss')).toBeInTheDocument();
    expect(screen.getByText('Add trades to see your P&L chart')).toBeInTheDocument();

    expect(screen.getByText('Strategy Breakdown')).toBeInTheDocument();
    expect(screen.getByText('Performance by strategy type')).toBeInTheDocument();
    expect(screen.getByText('Strategy data will appear here')).toBeInTheDocument();

    expect(screen.getByText('Monthly Performance')).toBeInTheDocument();
    expect(screen.getByText('Monthly P&L heatmap view')).toBeInTheDocument();
    expect(
      screen.getByText('Monthly heatmap will populate with your trading data')
    ).toBeInTheDocument();
  });
});
