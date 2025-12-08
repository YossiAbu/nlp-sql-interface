import { test, expect } from '@playwright/test';
import { LoginPage, RegisterPage, LayoutComponent } from './utils/page-objects';
import {
  generateTestUser,
  registerUser,
  registerAndLoginViaUI,
} from './utils/test-helpers';

test.describe('Authentication Flow Tests', () => {
  /**
   * Test 1: Complete Registration Flow
   */
  test('should complete registration flow successfully', async ({ page, request }) => {
    const registerPage = new RegisterPage(page);
    const testUser = generateTestUser();

    await registerPage.goto();
    await registerPage.expectOnRegisterPage();
    await registerPage.register(testUser.fullName, testUser.email, testUser.password);

    // Wait for navigation to login page
    await page.waitForURL(/.*\/login/, { timeout: 10000 });

    const loginPage = new LoginPage(page);
    await loginPage.expectOnLoginPage();
  });

  /**
   * Test 2: Complete Login Flow
   */
  test('should complete login flow successfully', async ({ page, request }) => {
    const loginPage = new LoginPage(page);
    const layout = new LayoutComponent(page);
    const testUser = generateTestUser();

    // Register via API first
    await registerUser(request, testUser);

    await loginPage.goto();
    await loginPage.expectOnLoginPage();
    await loginPage.login(testUser.email, testUser.password);

    // Wait for navigation to interface page
    await page.waitForURL(/.*\/interface/, { timeout: 10000 });

    // Verify user info is displayed
    await layout.expectUserLoggedIn(testUser.email);
  });

  /**
   * Test 3: Login with Invalid Credentials
   */
  test('should show error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectOnLoginPage();
    await loginPage.login('invalid@example.com', 'WrongPassword123!');

    // Wait for error message
    await loginPage.expectError(/invalid credentials/i);

    // Verify still on login page
    await loginPage.expectOnLoginPage();
  });

  /**
   * Test 4: Register with Duplicate Email
   */
  test('should show error when registering with duplicate email', async ({ page, request }) => {
    const registerPage = new RegisterPage(page);
    const testUser = generateTestUser();

    // Register via API first
    await registerUser(request, testUser);

    await registerPage.goto();
    await registerPage.expectOnRegisterPage();
    await registerPage.register('Another Name', testUser.email, 'DifferentPass123!');

    // Wait for error message
    await registerPage.expectError(/already registered/i);

    // Verify still on register page
    await registerPage.expectOnRegisterPage();
  });

  /**
   * Test 5: Logout Flow
   */
  test('should logout successfully', async ({ page, request }) => {
    const layout = new LayoutComponent(page);
    const loginPage = new LoginPage(page);

    // Register and login via UI
    const testUser = await registerAndLoginViaUI(page, request);

    // Verify user is logged in
    await layout.expectUserLoggedIn(testUser.email);

    // Click logout button
    await layout.logout();

    // Wait for navigation to login page
    await page.waitForURL(/.*\/login/, { timeout: 10000 });

    // Verify on login page
    await loginPage.expectOnLoginPage();
  });
});
