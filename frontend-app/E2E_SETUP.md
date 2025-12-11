# E2E Testing Setup Guide

## Simple E2E Testing Workflow

The E2E tests **automatically start a fresh backend with the test database**. You just need to make sure your development backend is stopped first.

### Prerequisites (One-Time Setup)

1. **Create Test Database**
   ```sql
   CREATE DATABASE nlp_sql_test;
   ```

2. **Set Environment Variables**
   
   Make sure you have your OpenAI API key available:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key-here"
   
   # Windows CMD
   set OPENAI_API_KEY=your-api-key-here
   
   # macOS/Linux
   export OPENAI_API_KEY=your-api-key-here
   ```

3. **Verify Database Credentials (Optional)**
   
   The default test database URL is `postgresql://myuser:mypassword@localhost/nlp_sql_test`.
   
   If your PostgreSQL credentials are different, you can set them via environment variable:
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL="postgresql://your_user:your_pass@localhost/nlp_sql_test"
   
   # macOS/Linux
   export DATABASE_URL="postgresql://your_user:your_pass@localhost/nlp_sql_test"
   ```
   
   Or update the default in `frontend-app/playwright.config.ts`.

---

## Running E2E Tests

### Step 1: Stop Your Development Backend

**IMPORTANT:** Before running tests, stop any backend server running on port 8000.

- If running in a terminal, press `Ctrl+C`
- Or close the terminal running the backend

### Step 2: Run Tests

```bash
cd frontend-app
npm run test:e2e
```

Or for a specific browser:
```bash
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=firefox
npm run test:e2e -- --project=webkit
```

---

## How It Works

1. ✅ You stop your development backend (port 8000)
2. ✅ Playwright starts a fresh backend with **test database** (port 8000)
3. ✅ Tests run against the test database
4. ✅ After tests, Playwright shuts down the test backend
5. ✅ You can restart your development backend

**Result:** Your production database stays clean! 🎉

---

## Benefits

✅ **Simple workflow** - Just stop backend, run tests  
✅ **Test isolation** - Uses separate `nlp_sql_test` database  
✅ **Production safe** - Production database never touched  
✅ **Always fresh** - Backend starts clean every test run  
✅ **Cross-platform** - Works on Windows, Mac, Linux  

---

## CI/CD Integration

The E2E tests run automatically in GitHub Actions on every push to `main` or `dev` branches.

**How CI Works:**
- Playwright automatically starts the backend with the test database
- Environment variables (`DATABASE_URL`, `OPENAI_API_KEY`) are passed from GitHub Actions secrets
- Tests run in parallel across different steps (backend tests → frontend tests → E2E tests)
- No manual backend startup needed - Playwright handles everything

**Required GitHub Secrets:**
- `OPENAI_API_KEY` - Your OpenAI API key (must be set in repository secrets)

---

## Troubleshooting

**"Port 8000 already in use" (Local)**
- You forgot to stop your development backend
- Solution: Stop it with `Ctrl+C` or close the terminal

**"Port 8000 already in use" (CI)**
- This error should no longer occur after the latest updates
- Playwright now exclusively manages the backend in CI (no duplicate startup)

**Backend fails to start**
- Verify test database exists: `CREATE DATABASE nlp_sql_test;`
- Check PostgreSQL is running
- Verify `OPENAI_API_KEY` environment variable is set
- Verify credentials in `playwright.config.ts` are correct

**Tests still hitting production database**
- Make sure you stopped your development backend
- The test backend should show `DATABASE_URL` with `nlp_sql_test` in the logs

**Missing OPENAI_API_KEY**
- Local: Set the environment variable before running tests (see Prerequisites)
- CI: Ensure the secret is configured in GitHub repository settings

