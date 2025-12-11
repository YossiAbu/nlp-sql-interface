#!/usr/bin/env node
/**
 * Start backend server with test database for E2E tests
 * This script sets up the test database URL and starts the backend
 * Works cross-platform (Windows, Mac, Linux)
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Define __dirname for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Get credentials from environment or .env.test file
const databaseUrl = process.env.DATABASE_URL || 
  'postgresql://myuser:mypassword@localhost/nlp_sql_test';

const env = {
  ...process.env,
  DATABASE_URL: databaseUrl,
  PYTHONUNBUFFERED: '1', // Ensure Python output is unbuffered
};

console.log('Starting backend with test database...');
console.log('DATABASE_URL:', databaseUrl);

// Spawn the backend process
const backend = spawn('python', ['-m', 'uvicorn', 'main:app', '--reload', '--port', '8000'], {
  cwd: path.join(__dirname, '../backend'),
  env: env,
  stdio: 'inherit', // Inherit stdio to see backend logs
});

// Handle process termination
backend.on('error', (err) => {
  console.error('Failed to start backend:', err);
  process.exit(1);
});

backend.on('exit', (code) => {
  if (code !== null && code !== 0) {
    console.error(`Backend exited with code ${code}`);
  }
  process.exit(code || 0);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down backend...');
  backend.kill();
});

process.on('SIGTERM', () => {
  console.log('\nTerminating backend...');
  backend.kill();
});