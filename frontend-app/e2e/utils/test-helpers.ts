import { APIRequestContext, Page, BrowserContext } from '@playwright/test';

// API Base URL
const API_URL = 'http://localhost:8000';

// Types
export interface TestUser {
  fullName: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  full_name: string;
}

export interface QueryResponse {
  sql_query: string;
  results: string;
  raw_rows: Record<string, unknown>[];
  execution_time: number;
  status: 'success' | 'error';
  error_message?: string;
}

export interface HistoryResponse {
  items: Array<{
    id: string;
    question: string;
    sql_query: string;
    status: string;
    execution_time: number;
    created_date: string;
  }>;
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Generate a unique test email using timestamp and random string
 */
export function generateTestEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `test_${timestamp}_${random}@e2e-test.com`;
}

/**
 * Generate a test user with unique email
 */
export function generateTestUser(overrides?: Partial<TestUser>): TestUser {
  return {
    fullName: 'E2E Test User',
    email: generateTestEmail(),
    password: 'TestPass123!',
    ...overrides,
  };
}

/**
 * Register a new user via API
 */
export async function registerUser(
  request: APIRequestContext,
  user: TestUser
): Promise<void> {
  const response = await request.post(`${API_URL}/register`, {
    data: {
      full_name: user.fullName,
      email: user.email,
      password: user.password,
    },
  });

  if (!response.ok()) {
    const error = await response.json();
    throw new Error(`Registration failed: ${error.detail || response.statusText()}`);
  }
}

/**
 * Login a user via the UI (to properly set HttpOnly cookies)
 */
export async function loginViaUI(
  page: Page,
  email: string,
  password: string
): Promise<void> {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  
  // Wait for the form to be ready
  const emailInput = page.locator('input[placeholder="Enter your email"]');
  await emailInput.waitFor({ state: 'visible', timeout: 10000 });
  
  await emailInput.fill(email);
  await page.fill('input[placeholder="Enter your password"]', password);
  
  // Click and wait for navigation
  await Promise.all([
    page.waitForURL(/.*\/interface/, { timeout: 30000 }),
    page.click('button[type="submit"]'),
  ]);
  
  // Wait for page to fully load
  await page.waitForLoadState('networkidle');
}

/**
 * Register and login a user via UI, returning the user data
 */
export async function registerAndLoginViaUI(
  page: Page,
  request: APIRequestContext,
  user?: TestUser
): Promise<TestUser> {
  const testUser = user || generateTestUser();
  
  // Register via API (faster)
  await registerUser(request, testUser);
  
  // Login via UI (to set cookies properly)
  await loginViaUI(page, testUser.email, testUser.password);
  
  return testUser;
}

/**
 * Submit a query via API (requires cookies from browser context)
 */
export async function submitQueryViaAPI(
  page: Page,
  question: string
): Promise<QueryResponse> {
  // Use page.request which includes cookies from the browser context
  const response = await page.request.post(`${API_URL}/query`, {
    data: { question },
    timeout: 60000, // Increase timeout for OpenAI API calls
  });

  if (!response.ok()) {
    let errorMessage = response.statusText();
    try {
      const error = await response.json();
      errorMessage = error.detail || errorMessage;
    } catch {
      // Response was not JSON
      const text = await response.text();
      errorMessage = text.substring(0, 100);
    }
    throw new Error(`Query failed (${response.status()}): ${errorMessage}`);
  }

  return response.json();
}

/**
 * Get user's query history via API
 */
export async function getHistoryViaAPI(
  page: Page
): Promise<HistoryResponse> {
  const response = await page.request.get(`${API_URL}/history`);

  if (!response.ok()) {
    const error = await response.json();
    throw new Error(`Get history failed: ${error.detail || response.statusText()}`);
  }

  return response.json();
}

/**
 * Clear user's query history via API
 */
export async function clearHistoryViaAPI(
  page: Page
): Promise<void> {
  const response = await page.request.delete(`${API_URL}/history`);

  if (!response.ok()) {
    const error = await response.json();
    throw new Error(`Clear history failed: ${error.detail || response.statusText()}`);
  }
}

/**
 * Logout user via API
 */
export async function logoutViaAPI(
  page: Page
): Promise<void> {
  const response = await page.request.post(`${API_URL}/logout`);

  if (!response.ok()) {
    const error = await response.json();
    throw new Error(`Logout failed: ${error.detail || response.statusText()}`);
  }
}

/**
 * Wait for the page to be fully loaded
 */
export async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
}

/**
 * Submit a query through the UI
 */
export async function submitQueryViaUI(
  page: Page,
  question: string
): Promise<void> {
  await page.fill('textarea', question);
  await page.click('button[type="submit"]');
}
