# E2E Testing with Playwright

This directory contains end-to-end tests for the NLP-SQL Interface application using [Playwright](https://playwright.dev/).

## Prerequisites

Before running E2E tests, make sure you have:

1. **Node.js 18+** installed
2. **Backend server** running on `http://localhost:8000`
3. **Playwright browsers** installed

## Quick Start

### 1. Install dependencies (if not already done)

```bash
cd frontend-app
npm install
```

### 2. Install Playwright browsers

```bash
npx playwright install
```

### 3. Start the backend server

In a separate terminal:

```bash
cd backend
python -m uvicorn main:app --reload
```

### 4. Run E2E tests

```bash
# Run all tests (headless)
npm run test:e2e

# Run tests with UI (interactive mode)
npm run test:e2e:ui

# Run tests with visible browser
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug
```

## Test Structure

```
e2e/
├── auth.spec.ts        # Authentication tests (login, register, logout)
├── query.spec.ts       # Query interface tests
├── history.spec.ts     # History management tests
├── navigation.spec.ts  # Navigation and routing tests
├── utils/
│   ├── test-helpers.ts # API helpers and data generators
│   └── page-objects.ts # Page Object Models
└── README.md           # This file
```

## Test Categories

### Authentication Tests (`auth.spec.ts`)
- Complete registration flow
- Complete login flow
- Login with invalid credentials
- Register with duplicate email
- Logout flow

### Query Interface Tests (`query.spec.ts`)
- Submit query and view results
- Empty query validation
- Query from URL parameter
- Feature highlights display

### History Management Tests (`history.spec.ts`)
- View query history
- Search history
- Filter by status
- Clear history
- Rerun query from history

### Navigation Tests (`navigation.spec.ts`)
- Protected route behavior
- Session persistence
- Page navigation
- Theme toggle

## Running Specific Tests

```bash
# Run a specific test file
npx playwright test e2e/auth.spec.ts

# Run tests matching a pattern
npx playwright test -g "login"

# Run tests in a specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Debugging Tests

### Interactive UI Mode

The best way to debug tests:

```bash
npm run test:e2e:ui
```

This opens a visual interface where you can:
- See each test step
- Time-travel through test execution
- View screenshots and traces
- Pick locators

### Debug Mode

Run a specific test with step-by-step debugging:

```bash
npm run test:e2e:debug
```

### View Test Report

After running tests, view the HTML report:

```bash
npx playwright show-report
```

## Test Data Strategy

Tests use a combination of:

1. **API-based setup**: Register/login users, submit queries via API before UI testing
2. **Unique test data**: Each test generates unique email addresses to avoid conflicts
3. **Clean isolation**: Tests don't depend on each other

### Helper Functions

```typescript
// Generate unique test user
const user = generateTestUser();

// Register and login via API
await registerAndLogin(request, context);

// Submit query via API
await submitQuery(request, 'Show all players');
```

## Page Object Models

Use Page Objects for cleaner, more maintainable tests:

```typescript
const loginPage = new LoginPage(page);
await loginPage.goto();
await loginPage.login('user@example.com', 'password');
await loginPage.expectError('Invalid credentials');
```

## Configuration

See `playwright.config.ts` for:
- Base URL configuration
- Browser settings
- Timeout settings
- Parallel execution
- Screenshot/video on failure

## CI/CD Integration

E2E tests run automatically in GitHub Actions:

1. After unit tests pass
2. Against a real PostgreSQL database
3. With Chromium browser
4. Artifacts uploaded on failure

## Troubleshooting

### Tests fail with "Connection refused"

Make sure the backend server is running:

```bash
cd backend
python -m uvicorn main:app --reload
```

### Tests are flaky

1. Increase timeouts in `playwright.config.ts`
2. Add explicit waits: `await page.waitForLoadState('networkidle')`
3. Use `await expect().toBeVisible()` instead of immediate assertions

### Can't find elements

Use Playwright's locator tools:

```bash
npx playwright codegen http://localhost:5173
```

This opens a browser where you can click elements to generate selectors.

### Browser installation issues

Reinstall browsers:

```bash
npx playwright install --with-deps
```

## Adding New Tests

1. Create a new `.spec.ts` file or add to existing one
2. Use Page Objects for selectors
3. Use helper functions for common operations
4. Follow existing patterns for consistency

Example:

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from './utils/page-objects';
import { registerAndLogin } from './utils/test-helpers';

test.describe('My Feature Tests', () => {
  test('should do something', async ({ page, request, context }) => {
    // Setup
    await registerAndLogin(request, context);
    
    // Test
    await page.goto('/my-page');
    await expect(page.getByText('Expected Text')).toBeVisible();
  });
});
```

