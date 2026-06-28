#!/usr/bin/env node

/**
 * E2E Test Runner
 * Provides automated checks for common functionality
 */

import http from 'http';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Test utilities
const tests = {
  passed: 0,
  failed: 0,
  results: [],
};

function pass(testName, message = '') {
  tests.passed++;
  tests.results.push({ status: '✓', name: testName, message });
  console.log(`✓ ${testName}${message ? ': ' + message : ''}`);
}

function fail(testName, message = '') {
  tests.failed++;
  tests.results.push({ status: '✗', name: testName, message });
  console.log(`✗ ${testName}${message ? ': ' + message : ''}`);
}

// File checks
async function checkFiles() {
  console.log('\n## Checking Required Files\n');

  const requiredFiles = [
    { path: 'index.html', name: 'Main HTML' },
    { path: 'assets/js/app.js', name: 'App JavaScript' },
    { path: 'assets/css/app.css', name: 'App CSS' },
    { path: 'manifest.json', name: 'PWA Manifest' },
    { path: 'data/wods/wods-full-body.json', name: 'Full Body WOD Data' },
    { path: 'data/wods/wods-upper-body.json', name: 'Upper Body WOD Data' },
    { path: 'data/wods/wods-lower-body.json', name: 'Lower Body WOD Data' },
    { path: 'data/wods/wods-cardio.json', name: 'Cardio WOD Data' },
    { path: 'data/wods/wods-strength.json', name: 'Strength WOD Data' },
    { path: 'data/programs/back-in-shape-2w.json', name: 'Back in Shape 2w Program' },
    { path: 'data/programs/back-in-shape-3w.json', name: 'Back in Shape 3w Program' },
    { path: 'data/programs/back-in-shape-4w.json', name: 'Back in Shape 4w Program' },
  ];

  const fs = await import('fs/promises');
  const docsPath = join(__dirname, '../../');

  for (const file of requiredFiles) {
    try {
      const fullPath = join(docsPath, file.path);
      await fs.access(fullPath);
      pass(`File exists: ${file.name}`, file.path);
    } catch {
      fail(`File exists: ${file.name}`, `Missing: ${file.path}`);
    }
  }
}

// Content checks
async function checkContent() {
  console.log('\n## Checking Content Integrity\n');

  const fs = await import('fs/promises');
  const docsPath = join(__dirname, '../../');

  // Check HTML doesn't contain NULL
  try {
    const html = await fs.readFile(join(docsPath, 'index.html'), 'utf-8');
    if (!html.includes('prog.weeks}')) {
      pass('HTML rendering', 'Program name rendering fixed (no weeks placeholder)');
    } else {
      fail('HTML rendering', 'Program name still renders weeks placeholder');
    }
  } catch (e) {
    fail('HTML check', e.message);
  }

  // Check frequency options (should be 3, 4, 5 only)
  try {
    const html = await fs.readFile(join(docsPath, 'index.html'), 'utf-8');
    const has3days = html.includes('data-freq="3"');
    const has4days = html.includes('data-freq="4"');
    const has5days = html.includes('data-freq="5"');
    const has6days = html.includes('data-freq="6"');

    if (has3days && has4days && has5days && !has6days) {
      pass('Frequency options', '3, 4, 5 days per week (6 days removed)');
    } else {
      fail('Frequency options', 'Missing expected frequencies or 6 days still present');
    }
  } catch (e) {
    fail('Frequency check', e.message);
  }

  // Check WOD categories
  try {
    const html = await fs.readFile(join(docsPath, 'index.html'), 'utf-8');
    const categories = ['full-body', 'upper-body', 'lower-body', 'cardio', 'strength'];
    const missing = categories.filter(cat => !html.includes(`data-category="${cat}"`));

    if (missing.length === 0) {
      pass('WOD categories', 'All 5 categories present');
    } else {
      fail('WOD categories', `Missing: ${missing.join(', ')}`);
    }
  } catch (e) {
    fail('Category check', e.message);
  }

  // Check async handler
  try {
    const js = await fs.readFile(join(docsPath, 'assets/js/app.js'), 'utf-8');
    if (js.includes('await loadRandomWod(category)')) {
      pass('Async WOD loading', 'Filter button handler is async');
    } else {
      fail('Async WOD loading', 'Missing await for loadRandomWod()');
    }
  } catch (e) {
    fail('JS check', e.message);
  }
}

// Data validation
async function checkData() {
  console.log('\n## Checking Data Files\n');

  const fs = await import('fs/promises');
  const docsPath = join(__dirname, '../../');

  const dataFiles = [
    { path: 'data/wods/wods-full-body.json', type: 'wods' },
    { path: 'data/programs/back-in-shape-2w.json', type: 'program' },
  ];

  for (const file of dataFiles) {
    try {
      const content = await fs.readFile(join(docsPath, file.path), 'utf-8');
      const data = JSON.parse(content);

      if (file.type === 'wods') {
        if (data.wods && Array.isArray(data.wods) && data.wods.length > 0) {
          pass(`WOD data valid: ${file.path}`, `${data.wods.length} WODs loaded`);
        } else {
          fail(`WOD data valid: ${file.path}`, 'Missing or empty wods array');
        }
      } else if (file.type === 'program') {
        if (data.program && data.program.sessions && Array.isArray(data.program.sessions)) {
          pass(`Program data valid: ${file.path}`, `${data.program.sessions.length} sessions`);
        } else {
          fail(`Program data valid: ${file.path}`, 'Invalid program structure');
        }
      }
    } catch (e) {
      fail(`Data parse: ${file.path}`, e.message);
    }
  }
}

// Server connectivity
async function checkServer() {
  console.log('\n## Checking Server\n');

  return new Promise((resolve) => {
    const req = http.get('http://localhost:8080', (res) => {
      if (res.statusCode === 200) {
        pass('Server running', 'Connected to http://localhost:8080');
      } else {
        fail('Server running', `Status code: ${res.statusCode}`);
      }
      res.resume(); // Drain response
      resolve();
    });

    req.on('error', (e) => {
      fail('Server running', 'Cannot connect (make sure Python server is running on port 8080)');
      resolve();
    });

    req.setTimeout(2000);
  });
}

// Summary
function printSummary() {
  console.log('\n========== TEST SUMMARY ==========\n');
  console.log(`Passed: ${tests.passed}`);
  console.log(`Failed: ${tests.failed}`);
  console.log(`Total:  ${tests.passed + tests.failed}\n`);

  if (tests.failed > 0) {
    console.log('Failed tests:');
    tests.results
      .filter(r => r.status === '✗')
      .forEach(r => console.log(`  - ${r.name}: ${r.message}`));
  }

  console.log('\n==================================\n');

  process.exit(tests.failed > 0 ? 1 : 0);
}

// Main
async function main() {
  console.log('========== WODDY E2E TEST RUNNER ==========\n');

  await checkFiles();
  await checkContent();
  await checkData();
  await checkServer();

  printSummary();
}

main().catch(console.error);
