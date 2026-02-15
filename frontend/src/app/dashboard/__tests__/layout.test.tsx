import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DashboardLayout from '../layout';

vi.mock('next/navigation', () => ({
  usePathname: () => '/dashboard',
}));

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock('next/image', () => ({
  default: (props: any) => <img {...props} />,
}));

describe('DashboardLayout', () => {
  it('renders all nav items: Overview, Journal, Analytics, AI Agents, Settings', () => {
    render(
      <DashboardLayout>
        <div>Child content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Journal')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
    expect(screen.getByText('AI Agents')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders children in the content area', () => {
    render(
      <DashboardLayout>
        <div data-testid="child-content">Test Child Content</div>
      </DashboardLayout>
    );

    expect(screen.getByTestId('child-content')).toBeInTheDocument();
    expect(screen.getByText('Test Child Content')).toBeInTheDocument();
  });

  it('has correct nav link hrefs', () => {
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );

    const overviewLink = screen.getByText('Overview').closest('a');
    expect(overviewLink).toHaveAttribute('href', '/dashboard');

    const journalLink = screen.getByText('Journal').closest('a');
    expect(journalLink).toHaveAttribute('href', '/dashboard/journal');

    const analyticsLink = screen.getByText('Analytics').closest('a');
    expect(analyticsLink).toHaveAttribute('href', '/dashboard/analytics');

    const agentsLink = screen.getByText('AI Agents').closest('a');
    expect(agentsLink).toHaveAttribute('href', '/dashboard/agents');

    const settingsLink = screen.getByText('Settings').closest('a');
    expect(settingsLink).toHaveAttribute('href', '/dashboard/settings');
  });
});
