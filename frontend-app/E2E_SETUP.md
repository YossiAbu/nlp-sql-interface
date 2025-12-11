# E2E Testing Setup Guide

## Simple E2E Testing Workflow

The E2E tests **automatically start a fresh backend with the test database**. You just need to make sure your development backend is stopped first.

### Prerequisites (One-Time Setup)

1. **Create Test Database**
   ```sql
   CREATE DATABASE nlp_sql_test;
   ```

2. **Verify Database Credentials**
   Update the `DATABASE_URL` in `frontend-app/playwright.config.ts` and `frontend-app/start-test-backend.js` with your PostgreSQL credentials:
   ```
   postgresql://your_username:your_password@localhost/nlp_sql_test
   ```

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

## Troubleshooting

**"Port 8000 already in use"**
- You forgot to stop your development backend
- Solution: Stop it with `Ctrl+C` or close the terminal

**Backend fails to start**
- Verify test database exists: `CREATE DATABASE nlp_sql_test;`
- Check PostgreSQL is running
- Verify credentials in `playwright.config.ts` are correct

**Tests still hitting production database**
- Make sure you stopped your development backend
- The test backend should show `DATABASE_URL` with `nlp_sql_test` in the logs

