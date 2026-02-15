import { test, expect } from '@playwright/test';

test.describe('Agents Chat', () => {
  test('agent selection page shows all agent cards', async ({ page }) => {
    await page.goto('/dashboard/agents');

    // Verify page heading
    await expect(page.getByRole('heading', { name: 'AI Agents' })).toBeVisible();
    await expect(
      page.getByText('Intelligent assistants to enhance your trading workflow.')
    ).toBeVisible();

    // Verify all three agent cards are displayed
    await expect(page.getByText('Screener Agent')).toBeVisible();
    await expect(
      page.getByText('Find stocks matching your criteria using AI-powered screening')
    ).toBeVisible();

    await expect(page.getByText('Analyst Agent')).toBeVisible();
    await expect(
      page.getByText('Deep analysis of your open positions and market conditions')
    ).toBeVisible();

    await expect(page.getByText('Coach Agent')).toBeVisible();
    await expect(
      page.getByText('Review your trading patterns and get personalized coaching')
    ).toBeVisible();

    // Verify each card has a "Start conversation" prompt
    const startConversationLabels = page.getByText('Start conversation');
    await expect(startConversationLabels).toHaveCount(3);
  });

  test('clicking an agent opens the chat UI', async ({ page }) => {
    await page.goto('/dashboard/agents');

    // Click the Screener Agent card
    await page.getByText('Screener Agent').click();

    // The chat interface should appear
    // Verify the chat header shows the selected agent name
    await expect(page.getByText('Screener Agent')).toBeVisible();
    await expect(page.getByText('Online')).toBeVisible();
    await expect(page.getByText('Ready')).toBeVisible();

    // Verify the empty chat state prompt
    await expect(page.getByText('Start a conversation')).toBeVisible();
    await expect(
      page.getByText(/Ask your screener agent anything about your trading/)
    ).toBeVisible();

    // Verify the message input and send button are present
    await expect(page.getByPlaceholder('Ask your agent...')).toBeVisible();

    // Verify the back button exists to return to agent selection
    const backButton = page.locator('button').filter({ has: page.locator('svg') }).first();
    await backButton.click();

    // Should return to agent selection view with all cards visible
    await expect(page.getByText('Analyst Agent')).toBeVisible();
    await expect(page.getByText('Coach Agent')).toBeVisible();
  });
});
