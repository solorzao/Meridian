import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SettingsPage from '../page';

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe('SettingsPage', () => {
  it('renders all section headings', () => {
    render(<SettingsPage />);

    // Page heading
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(
      screen.getByText('Manage your account, subscription, and agent preferences.')
    ).toBeInTheDocument();

    // Section headings
    expect(screen.getByText('Account')).toBeInTheDocument();
    expect(screen.getByText('Subscription')).toBeInTheDocument();
    expect(screen.getByText('Agent Configuration')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Security')).toBeInTheDocument();
    expect(screen.getByText('Danger Zone')).toBeInTheDocument();
  });

  it('renders agent configuration toggle items', () => {
    render(<SettingsPage />);

    // Agent configuration toggles
    expect(screen.getByText('Auto-analyze new trades')).toBeInTheDocument();
    expect(
      screen.getByText('Run analysis agent on every new journal entry')
    ).toBeInTheDocument();

    expect(screen.getByText('Weekly performance digest')).toBeInTheDocument();
    expect(
      screen.getByText('Receive a coaching summary every Sunday')
    ).toBeInTheDocument();

    expect(screen.getByText('Risk alerts')).toBeInTheDocument();
    expect(
      screen.getByText('Get notified when positions exceed risk parameters')
    ).toBeInTheDocument();

    expect(screen.getByText('Market screener notifications')).toBeInTheDocument();
    expect(
      screen.getByText('Alert when screener finds matching opportunities')
    ).toBeInTheDocument();

    // Notification toggles
    expect(screen.getByText('Email notifications')).toBeInTheDocument();
    expect(screen.getByText('Browser notifications')).toBeInTheDocument();
  });

  it('renders Danger Zone with Delete Account button', () => {
    render(<SettingsPage />);

    expect(screen.getByText('Danger Zone')).toBeInTheDocument();
    expect(screen.getByText('Irreversible actions')).toBeInTheDocument();
    expect(screen.getByText('Delete Account', { selector: 'p' })).toBeInTheDocument();
    expect(
      screen.getByText(
        'Permanently delete your account and all associated data. This cannot be undone.'
      )
    ).toBeInTheDocument();

    // The delete button
    const deleteButton = screen.getByRole('button', { name: 'Delete Account' });
    expect(deleteButton).toBeInTheDocument();
  });
});
