import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Home from '../page';

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

describe('Home page', () => {
  it('renders the hero tagline', () => {
    render(<Home />);
    expect(screen.getByText(/We help you find/i)).toBeInTheDocument();
    expect(screen.getByText('your way.')).toBeInTheDocument();
    expect(
      screen.getByText(
        /AI-powered trading journal and research assistant that turns your trade data into actionable insights/i
      )
    ).toBeInTheDocument();
  });

  it('renders feature cards: AI Agents, Trade Journal, Analytics', () => {
    render(<Home />);
    expect(screen.getByText('AI Agents')).toBeInTheDocument();
    expect(screen.getByText('Trade Journal')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();

    // Also check highlight cards
    expect(screen.getByText('Pattern Recognition')).toBeInTheDocument();
    expect(screen.getByText('Risk Awareness')).toBeInTheDocument();
    expect(screen.getByText('Find Your Edge')).toBeInTheDocument();
  });

  it('has Get Started links pointing to /dashboard', () => {
    render(<Home />);
    const getStartedLinks = screen.getAllByText('Get Started');
    expect(getStartedLinks.length).toBeGreaterThanOrEqual(1);
    getStartedLinks.forEach((link) => {
      expect(link.closest('a')).toHaveAttribute('href', '/dashboard');
    });

    // Also check Open Dashboard CTA link
    const openDashboardLink = screen.getByText('Open Dashboard');
    expect(openDashboardLink.closest('a')).toHaveAttribute('href', '/dashboard');

    // Dashboard nav link
    const dashboardLink = screen.getByText('Dashboard');
    expect(dashboardLink.closest('a')).toHaveAttribute('href', '/dashboard');
  });
});
