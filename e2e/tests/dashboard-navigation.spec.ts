import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
  test('dashboard loads with overview content', async ({ page }) => {
    await page.goto('/dashboard');

    // Verify the welcome header is displayed
    await expect(page.getByRole('heading', { name: /Good evening, Trader/i })).toBeVisible();
    await expect(
      page.getByText('Here is your trading overview. Start by logging your first trade.')
    ).toBeVisible();

    // Verify stat cards are rendered
    await expect(page.getByText('Open Trades')).toBeVisible();
    await expect(page.getByText('Total P&L')).toBeVisible();
    await expect(page.getByText('Win Rate')).toBeVisible();
    await expect(page.getByText('Profit Factor')).toBeVisible();

    // Verify Quick Actions section
    await expect(page.getByText('Quick Actions')).toBeVisible();
    await expect(page.getByText('Log a Trade')).toBeVisible();
    await expect(page.getByText('Chat with Agent')).toBeVisible();
    await expect(page.getByText('View Analytics')).toBeVisible();
  });

  test('sidebar nav items navigate to correct pages', async ({ page }) => {
    await page.goto('/dashboard');

    // Verify the sidebar contains expected nav items
    const sidebar = page.locator('aside');
    await expect(sidebar.getByText('Overview')).toBeVisible();
    await expect(sidebar.getByText('Journal')).toBeVisible();
    await expect(sidebar.getByText('Analytics')).toBeVisible();
    await expect(sidebar.getByText('AI Agents')).toBeVisible();
    await expect(sidebar.getByText('Settings')).toBeVisible();

    // Navigate to Journal via sidebar
    await sidebar.getByText('Journal').click();
    await expect(page).toHaveURL(/\/dashboard\/journal/);
    await expect(page.getByRole('heading', { name: 'Trade Journal' })).toBeVisible();

    // Navigate to AI Agents via sidebar
    await sidebar.getByText('AI Agents').click();
    await expect(page).toHaveURL(/\/dashboard\/agents/);
    await expect(page.getByRole('heading', { name: 'AI Agents' })).toBeVisible();

    // Navigate back to Overview via sidebar
    await sidebar.getByText('Overview').click();
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: /Good evening, Trader/i })).toBeVisible();
  });

  test('active nav state updates on navigation', async ({ page }) => {
    await page.goto('/dashboard');

    const sidebar = page.locator('aside');

    // Overview link should have the active class on the dashboard page
    const overviewLink = sidebar.getByRole('link', { name: 'Overview' });
    await expect(overviewLink).toHaveClass(/meridian-nav-link-active/);

    // Journal link should not be active yet
    const journalLink = sidebar.getByRole('link', { name: 'Journal' });
    await expect(journalLink).not.toHaveClass(/meridian-nav-link-active/);

    // Click Journal and verify active state changes
    await journalLink.click();
    await expect(page).toHaveURL(/\/dashboard\/journal/);
    await expect(journalLink).toHaveClass(/meridian-nav-link-active/);
    await expect(overviewLink).not.toHaveClass(/meridian-nav-link-active/);
  });
});
