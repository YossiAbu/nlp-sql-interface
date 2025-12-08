import { Page, Locator, expect } from '@playwright/test';

/**
 * Login Page Object Model
 */
export class LoginPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly registerLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: 'Login' });
    this.emailInput = page.locator('input[placeholder="Enter your email"]');
    this.passwordInput = page.locator('input[placeholder="Enter your password"]');
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.text-red-500');
    this.registerLink = page.getByRole('link', { name: /register here/i });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string | RegExp) {
    await expect(this.errorMessage).toContainText(message);
  }

  async expectOnLoginPage() {
    await expect(this.heading).toBeVisible();
  }
}

/**
 * Register Page Object Model
 */
export class RegisterPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly fullNameInput: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly loginLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: 'Register' });
    this.fullNameInput = page.locator('input[placeholder="Enter your full name"]');
    this.emailInput = page.locator('input[placeholder="Enter your email"]');
    this.passwordInput = page.locator('input[placeholder="Enter your password"]');
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.text-red-500');
    this.loginLink = page.getByRole('link', { name: /login here/i });
  }

  async goto() {
    await this.page.goto('/register');
  }

  async register(fullName: string, email: string, password: string) {
    await this.fullNameInput.fill(fullName);
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string | RegExp) {
    await expect(this.errorMessage).toContainText(message);
  }

  async expectOnRegisterPage() {
    await expect(this.heading).toBeVisible();
  }
}

/**
 * Query Interface Page Object Model
 */
export class QueryPage {
  readonly page: Page;
  readonly queryInput: Locator;
  readonly submitButton: Locator;
  readonly resultsSection: Locator;

  constructor(page: Page) {
    this.page = page;
    this.queryInput = page.locator('textarea');
    this.submitButton = page.locator('button[type="submit"]');
    this.resultsSection = page.locator('table').first();
  }

  async goto() {
    await this.page.goto('/interface');
  }

  async gotoWithQuestion(question: string) {
    await this.page.goto(`/interface?question=${encodeURIComponent(question)}`);
  }

  async submitQuery(question: string) {
    await this.queryInput.fill(question);
    await this.submitButton.click();
  }

  async waitForResults() {
    // Wait for either results table or SQL display to appear
    await this.page.waitForSelector('table, pre, code', { timeout: 60000 });
  }

  async expectProcessing() {
    await expect(this.page.getByText('Processing')).toBeVisible();
  }

  async expectSubmitButtonDisabled() {
    await expect(this.submitButton).toBeDisabled();
  }

  async expectFeatureCardsVisible() {
    await expect(this.page.getByText('Natural-Language Input')).toBeVisible();
  }

  async expectFeatureCardsHidden() {
    await expect(this.page.getByText('Natural-Language Input')).not.toBeVisible();
  }
}

/**
 * History Page Object Model
 */
export class HistoryPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly searchInput: Locator;
  readonly statusFilter: Locator;
  readonly clearHistoryButton: Locator;
  readonly emptyState: Locator;
  readonly loginPrompt: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByText('My Query History');
    this.searchInput = page.locator('input[placeholder="Search queries or SQL..."]');
    this.statusFilter = page.locator('select');
    this.clearHistoryButton = page.getByRole('button', { name: /clear history/i });
    this.emptyState = page.getByText(/no queries yet/i);
    this.loginPrompt = page.getByText('Log in to access your personal query history.');
  }

  async goto() {
    await this.page.goto('/history');
  }

  async search(query: string) {
    await this.searchInput.fill(query);
  }

  async clearSearch() {
    await this.searchInput.clear();
  }

  async filterByStatus(status: 'all' | 'success' | 'error') {
    await this.statusFilter.selectOption(status);
  }

  async clearHistory() {
    await this.clearHistoryButton.click();
  }

  async clickRerunButton(question: string) {
    // Find the card containing the question, then click its Rerun button
    const card = this.page.locator('div').filter({ hasText: question }).first();
    await card.hover();
    await card.getByRole('button', { name: /rerun/i }).click();
  }

  async expectLoginPromptVisible() {
    await expect(this.loginPrompt).toBeVisible();
  }

  async expectEmptyState() {
    await expect(this.emptyState).toBeVisible();
  }

  async expectQueriesCount(count: number) {
    await expect(this.page.getByText(new RegExp(`${count}\\s*Total`, 'i'))).toBeVisible();
  }

  async expectQueryVisible(question: string) {
    await expect(this.page.getByText(question)).toBeVisible();
  }

  async expectQueryNotVisible(question: string) {
    // Use toBeHidden for more reliable checking
    await expect(this.page.getByText(question).first()).toBeHidden({ timeout: 5000 });
  }
}

/**
 * Layout Component (Navigation, Footer, User Info)
 */
export class LayoutComponent {
  readonly page: Page;
  readonly logoutButton: Locator;
  readonly loginButton: Locator;
  readonly queryInterfaceLink: Locator;
  readonly historyLink: Locator;
  readonly themeToggle: Locator;

  constructor(page: Page) {
    this.page = page;
    this.logoutButton = page.locator('button').filter({ has: page.locator('.lucide-log-out') });
    this.loginButton = page.getByRole('button', { name: /login.*sign up/i });
    this.queryInterfaceLink = page.getByRole('link', { name: 'Query Interface' });
    this.historyLink = page.getByRole('link', { name: 'My History' });
    this.themeToggle = page.getByRole('button', { name: /light mode|dark mode/i });
  }

  async logout() {
    await this.logoutButton.click();
  }

  async navigateToQueryInterface() {
    await this.queryInterfaceLink.click();
  }

  async navigateToHistory() {
    await this.historyLink.click();
  }

  async toggleTheme() {
    await this.themeToggle.click();
  }

  async expectUserLoggedIn(email: string) {
    await expect(this.page.getByText(email)).toBeVisible({ timeout: 10000 });
  }

  async expectUserLoggedOut() {
    await expect(this.loginButton).toBeVisible({ timeout: 10000 });
  }
}
