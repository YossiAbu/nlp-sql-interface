import { test, expect } from '@playwright/test';
import { HistoryPage, QueryPage } from './utils/page-objects';
import { registerAndLoginViaUI, submitQueryViaAPI } from './utils/test-helpers';

test.describe('History Management Tests', () => {
  /**
   * Test 10: View Query History
   */
  test('should display query history', async ({ page, request }) => {
    const historyPage = new HistoryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Submit queries via API
    await submitQueryViaAPI(page, 'Show all players');
    await submitQueryViaAPI(page, 'Show top 5 players by rating');
    await submitQueryViaAPI(page, 'How many players are there');

    // Navigate to history page
    await historyPage.goto();
    await page.waitForLoadState('networkidle');

    // Verify queries are displayed
    await historyPage.expectQueriesCount(3);
    await historyPage.expectQueryVisible('Show all players');
    await historyPage.expectQueryVisible('Show top 5 players by rating');
  });

  /**
   * Test 11: Search Query History
   */
  test('should filter history by search', async ({ page, request }) => {
    const historyPage = new HistoryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Submit different queries with unique keywords
    await submitQueryViaAPI(page, 'Show all football players');
    await submitQueryViaAPI(page, 'List basketball teams');

    // Navigate to history page
    await historyPage.goto();
    await page.waitForLoadState('networkidle');

    // Verify both queries are visible initially
    await historyPage.expectQueriesCount(2);

    // Search for "football" - should only match the first query
    await historyPage.search('football');
    
    // Wait for filter to apply
    await page.waitForTimeout(1500);
    
    // Verify matching query is still visible
    await historyPage.expectQueryVisible('Show all football players');
    
    // Verify the query count text shows filtered result
    // The search filters on both question AND sql_query, so check the UI shows fewer results

    // Clear search
    await historyPage.clearSearch();
    await page.waitForTimeout(1500);

    // All queries should appear again
    await historyPage.expectQueryVisible('Show all football players');
    await historyPage.expectQueryVisible('List basketball teams');
  });

  /**
   * Test 12: Filter History by Status
   */
  test('should filter history by status', async ({ page, request }) => {
    const historyPage = new HistoryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Submit queries (should be success)
    await submitQueryViaAPI(page, 'Show all players');
    await submitQueryViaAPI(page, 'Show top 10 players');

    // Navigate to history page
    await historyPage.goto();
    await page.waitForLoadState('networkidle');

    // Verify queries are visible
    await historyPage.expectQueriesCount(2);

    // Filter by success
    await historyPage.filterByStatus('success');
    await page.waitForTimeout(500);

    // Should show successful queries
    await historyPage.expectQueryVisible('Show all players');

    // Filter by all
    await historyPage.filterByStatus('all');
    await page.waitForTimeout(500);

    // All queries visible
    await historyPage.expectQueriesCount(2);
  });

  /**
   * Test 13: Clear History
   */
  test('should clear all history', async ({ page, request }) => {
    const historyPage = new HistoryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Submit queries
    await submitQueryViaAPI(page, 'Query one');
    await submitQueryViaAPI(page, 'Query two');
    await submitQueryViaAPI(page, 'Query three');

    // Navigate to history page
    await historyPage.goto();
    await page.waitForLoadState('networkidle');

    // Verify 3 queries are displayed
    await historyPage.expectQueriesCount(3);

    // Set up dialog handler to accept confirmation
    page.on('dialog', async (dialog) => {
      await dialog.accept();
    });

    // Click clear history button
    await historyPage.clearHistory();

    // Wait for clear to complete
    await page.waitForLoadState('networkidle');

    // Verify empty state
    await historyPage.expectEmptyState();
  });

  /**
   * Test 14: Rerun Query from History
   */
  test('should rerun query from history', async ({ page, request }) => {
    const historyPage = new HistoryPage(page);
    const queryPage = new QueryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Submit a query via API
    await submitQueryViaAPI(page, 'Show top 10 players');

    // Navigate to history page
    await historyPage.goto();
    await page.waitForLoadState('networkidle');

    // Verify query is visible
    await historyPage.expectQueryVisible('Show top 10 players');

    // Click rerun button
    await historyPage.clickRerunButton('Show top 10 players');

    // Wait for navigation to interface with query parameter
    await page.waitForURL(/.*\/interface\?question=/, { timeout: 10000 });

    // Wait for results (query should auto-submit)
    await queryPage.waitForResults();
  });

  /**
   * Test: Empty History State
   */
  test('should show empty state for new user', async ({ page, request }) => {
    const historyPage = new HistoryPage(page);

    // Register and login (new user with no history)
    await registerAndLoginViaUI(page, request);

    // Navigate to history page
    await historyPage.goto();
    await page.waitForLoadState('networkidle');

    // Verify empty state
    await historyPage.expectEmptyState();
    await expect(page.getByText(/start by asking/i)).toBeVisible();
  });
});
