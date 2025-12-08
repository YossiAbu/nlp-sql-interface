import { test, expect } from '@playwright/test';
import { LoginPage, HistoryPage, QueryPage, LayoutComponent } from './utils/page-objects';
import { registerAndLoginViaUI, submitQueryViaAPI } from './utils/test-helpers';

test.describe('Protected Routes & Navigation Tests', () => {
  /**
   * Test 15: Protected Route Behavior (redirects to login)
   */
  test('should redirect to login when accessing history without authentication', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Navigate directly to /history without logging in
    await page.goto('/history');
    await page.waitForLoadState('networkidle');

    // The app redirects to login page for unauthenticated users
    await loginPage.expectOnLoginPage();
    
    // Verify the login form is visible
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
  });

  /**
   * Test 16: Session Persistence
   */
  test('should persist session after page reload', async ({ page, request }) => {
    const queryPage = new QueryPage(page);
    const historyPage = new HistoryPage(page);
    const layout = new LayoutComponent(page);

    // Register and login
    const testUser = await registerAndLoginViaUI(page, request);

    // Verify user is logged in
    await layout.expectUserLoggedIn(testUser.email);

    // Reload the page
    await page.reload();

    // Verify user is still logged in after reload
    await layout.expectUserLoggedIn(testUser.email);

    // Submit a query
    await queryPage.submitQuery('Show top players');
    await queryPage.waitForResults();

    // Navigate to history
    await historyPage.goto();
    await page.waitForLoadState('networkidle');

    // Verify the query appears in history
    await historyPage.expectQueryVisible('Show top players');
  });

  /**
   * Test 17: Navigation Between Pages
   */
  test('should navigate between pages using sidebar links', async ({ page, request }) => {
    const layout = new LayoutComponent(page);
    const queryPage = new QueryPage(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Click History link in navigation
    await layout.navigateToHistory();

    // Verify on history page
    await expect(page).toHaveURL(/.*\/history/);
    await expect(page.getByText('My Query History')).toBeVisible();

    // Click Query Interface link in navigation
    await layout.navigateToQueryInterface();

    // Verify on interface page
    await expect(page).toHaveURL(/.*\/interface/);
    await expect(queryPage.queryInput).toBeVisible();
  });

  /**
   * Test 18: Theme Toggle
   */
  test('should toggle theme between light and dark mode', async ({ page, request }) => {
    const layout = new LayoutComponent(page);

    // Register and login
    await registerAndLoginViaUI(page, request);

    // Verify theme toggle button exists
    await expect(layout.themeToggle).toBeVisible();

    // Get initial theme state
    const htmlElement = page.locator('html');
    const initialClass = await htmlElement.getAttribute('class') || '';

    // Click theme toggle
    await layout.toggleTheme();
    await page.waitForTimeout(500);

    // Verify theme has changed
    const newClass = await htmlElement.getAttribute('class') || '';
    
    // Theme should have changed (either added or removed 'dark' class)
    const themeChanged = initialClass.includes('dark') !== newClass.includes('dark');
    expect(themeChanged).toBe(true);

    // Click theme toggle again
    await layout.toggleTheme();
    await page.waitForTimeout(500);

    // Verify theme reverted
    const revertedClass = await htmlElement.getAttribute('class') || '';
    expect(revertedClass.includes('dark')).toBe(initialClass.includes('dark'));
  });

  /**
   * Test: Login page links
   */
  test('should navigate between login and register pages', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Navigate to login page
    await loginPage.goto();
    await loginPage.expectOnLoginPage();

    // Click register link
    await loginPage.registerLink.click();

    // Verify on register page
    await expect(page).toHaveURL(/.*\/register/);

    // Click login link
    await page.getByRole('link', { name: /login here/i }).click();

    // Verify on login page
    await expect(page).toHaveURL(/.*\/login/);
  });
});
