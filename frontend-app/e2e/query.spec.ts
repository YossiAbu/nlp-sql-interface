import { test, expect } from '@playwright/test';
import { QueryPage } from './utils/page-objects';
import { registerAndLoginViaUI } from './utils/test-helpers';

test.describe('Query Interface Tests', () => {
  /**
   * Test 6: Submit Query and View Results
   */
  test('should submit query and display results', async ({ page, request }) => {
    const queryPage = new QueryPage(page);

    // Register and login via UI
    await registerAndLoginViaUI(page, request);

    // Should already be on /interface after login
    await expect(page).toHaveURL(/.*\/interface/);

    // Submit a query
    await queryPage.submitQuery('Show me top 5 players by rating');

    // Wait for results
    await queryPage.waitForResults();

    // Verify SQL query is displayed
    await expect(page.locator('pre, code').first()).toBeVisible();

    // Verify execution time is shown
    await expect(page.getByText(/\d+\s*ms/)).toBeVisible();
  });

  /**
   * Test 7: Submit Empty Query
   */
  test('should not submit empty query', async ({ page, request }) => {
    const queryPage = new QueryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Verify submit button is disabled when input is empty
    await expect(queryPage.queryInput).toHaveValue('');
    await queryPage.expectSubmitButtonDisabled();

    // Enter whitespace only
    await queryPage.queryInput.fill('   ');

    // Button should still be disabled (whitespace is trimmed)
    await queryPage.expectSubmitButtonDisabled();
  });

  /**
   * Test 8: Query with URL Parameter
   */
  test('should auto-submit query from URL parameter', async ({ page, request }) => {
    // Register and login first
    await registerAndLoginViaUI(page, request);

    // Navigate with question in URL
    await page.goto('/interface?question=Show%20all%20players');

    // Wait for results (auto-submitted)
    await page.waitForSelector('pre, code, table', { timeout: 60000 });

    // Verify SQL is displayed
    await expect(page.locator('pre, code').first()).toBeVisible();
  });

  /**
   * Test 9: Feature Highlights Display
   */
  test('should hide feature highlights after query submission', async ({ page, request }) => {
    const queryPage = new QueryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Navigate to fresh interface (no previous query)
    await page.goto('/interface');

    // Verify feature highlights are visible initially
    await queryPage.expectFeatureCardsVisible();
    await expect(page.getByText('Instant Results')).toBeVisible();
    await expect(page.getByText('Query History')).toBeVisible();

    // Submit a query
    await queryPage.submitQuery('Show top 10 players');

    // Wait for results
    await queryPage.waitForResults();

    // Verify feature cards are hidden after results appear
    await queryPage.expectFeatureCardsHidden();
  });

  /**
   * Test: Click example question
   */
  test('should fill textarea when clicking example question', async ({ page, request }) => {
    const queryPage = new QueryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Navigate to fresh interface
    await page.goto('/interface');

    // Click on an example question
    await page.getByText('Show me the top 10 players by overall rating').click();

    // Verify textarea is filled
    await expect(queryPage.queryInput).toHaveValue('Show me the top 10 players by overall rating');
  });
});
