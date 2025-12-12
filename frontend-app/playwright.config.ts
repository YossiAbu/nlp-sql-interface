/// <reference types="node" />
import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Test directory
  testDir: './e2e',

  // Run tests in parallel (reduced for stability)
  fullyParallel: false,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry failed tests
  retries: process.env.CI ? 2 : 1,

  // Limit parallel workers for stability
  workers: process.env.CI ? 1 : 2,

  // Reporter configuration
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],

  // Shared settings for all projects
  use: {
    // Base URL for navigation
    baseURL: 'http://localhost:5173',

    // Collect trace on first retry
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'on-first-retry',

    // Default timeout for actions (increased for API calls)
    actionTimeout: 15000,

    // Default timeout for navigation
    navigationTimeout: 30000,
  },

  // Test timeout (increased for real backend calls)
  timeout: 60000,

  // Expect timeout
  expect: {
    timeout: 10000,
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  // Web server configuration
  // IMPORTANT: Stop your development backend before running tests!
  // The tests will start a fresh backend with the test database.
  webServer: [
    // Frontend dev server
    {
      command: 'npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    // Backend API server with test database
    {
      command: 'node start-test-backend.js > backend-e2e.log 2>&1',  // Redirect logs to file
      url: 'http://localhost:8000/health',
      reuseExistingServer: false,  // Never reuse - always start fresh with test DB
      timeout: 120000,
      env: {
        // Pass through environment variables (from CI or local environment)
        DATABASE_URL: process.env.DATABASE_URL || 'postgresql://myuser:mypassword@localhost/nlp_sql_test',
        OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
        OPENAI_MODEL: process.env.OPENAI_MODEL || 'gpt-4o-mini',
      },
    },
  ],
});

