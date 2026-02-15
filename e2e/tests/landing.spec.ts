import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('loads with hero content and tagline', async ({ page }) => {
    await page.goto('/');

    // Verify the Meridian logo/image is present
    const logo = page.getByAltText('Meridian');
    await expect(logo).toBeVisible();

    // Verify the tagline text
    await expect(page.getByText('We help you find')).toBeVisible();
    await expect(page.getByText('your way.')).toBeVisible();

    // Verify the description paragraph
    await expect(
      page.getByText(
        'An AI-powered trading journal and research assistant that turns your trade data into actionable insights.'
      )
    ).toBeVisible();

    // Verify core feature cards are rendered
    await expect(page.getByText('AI Agents')).toBeVisible();
    await expect(page.getByText('Trade Journal')).toBeVisible();
    await expect(page.getByText('Analytics')).toBeVisible();

    // Verify the features section heading
    await expect(page.getByText('Everything you need to trade better')).toBeVisible();

    // Verify the CTA section
    await expect(page.getByText('Ready to navigate your trading?')).toBeVisible();

    // Verify footer
    await expect(page.getByText('Built for traders who want to improve.')).toBeVisible();
  });

  test('Get Started button navigates to dashboard', async ({ page }) => {
    await page.goto('/');

    // There are multiple "Get Started" links; click the prominent hero CTA
    const getStartedButtons = page.getByRole('link', { name: /Get Started/ });
    await getStartedButtons.first().click();

    // Should navigate to the dashboard
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
