# Woddy Testing Guide

This guide covers how to run tests locally to ensure everything works correctly.

## Setup

Install dependencies:

```bash
npm install
```

## Running Tests

### Unit Tests (Jest)

Run all unit tests:

```bash
npm test
```

Watch mode (re-run tests when files change):

```bash
npm run test:watch
```

Coverage report:

```bash
npm run test:coverage
```

### E2E Tests

Automated checks (file integrity, content validation, server connectivity):

```bash
npm run test:e2e
```

**Note**: Make sure the Python server is running on port 8080:

```bash
python3 -m http.server 8080
```

### Manual E2E Tests

For comprehensive manual testing, use the checklist in `tests/e2e/manual-tests.js`:

```bash
node tests/e2e/manual-tests.js
```

This prints a detailed checklist of features to test manually in the browser.

## Test Coverage

### Unit Tests (in `tests/unit/`)

**app.test.js** - Core functionality tests:
- Program name rendering (no NULL values)
- State management (duration, frequency, WOD selection)
- localStorage persistence
- DOM visibility toggles
- Event handler attachment
- Acronym expansion

**data-loading.test.js** - Data loading tests:
- WOD data fetching and caching
- Program data loading and filtering
- Training grouping by week
- Category selection and filtering
- Error handling and fallbacks

### E2E Tests (in `tests/e2e/`)

**manual-tests.js** - Manual test checklist:
- Onboarding flow
- Program selection and configuration
- Trainings list display
- WOD mode navigation
- Data persistence across reloads
- Timer functionality
- Responsive design
- Performance

**runner.js** - Automated checks:
- Required files exist
- HTML rendering is correct (no NULL)
- Frequency options are 3-5 days (no 6)
- WOD categories present
- Async handlers correctly implemented
- Data files are valid JSON
- Server is accessible

## Common Issues and Fixes

### Issue: Tests fail with "Cannot find module"

**Fix**: Make sure you've run `npm install` to install all dependencies.

### Issue: E2E tests fail to connect to server

**Fix**: Start the Python server:
```bash
cd /Users/arpa/projects/Woddy/docs
python3 -m http.server 8080
```

### Issue: Tests show "ReferenceError: fetch is not defined"

**Fix**: Jest is properly mocked in `tests/setup.js`. If this persists, clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: App shows "Back in Shape NULL" in the UI

**Fix**: This was caused by rendering `${prog.weeks}` when weeks was null. This has been fixed in app.js (line 144).

### Issue: WOD buttons don't load WODs

**Fix**: The filter button handler must be async. This has been fixed in app.js (line 938).

## Key Fixes Applied

### 1. Program Name Display (app.js:144)

**Before**:
```html
<h3>${prog.name} ${prog.weeks}w</h3>
```

**After**:
```html
<h3>${prog.name}</h3>
```

### 2. Async WOD Loading (app.js:938)

**Before**:
```javascript
btn.addEventListener('click', function(e) {
  // ...
  loadRandomWod(category);
});
```

**After**:
```javascript
btn.addEventListener('click', async function(e) {
  // ...
  await loadRandomWod(category);
});
```

### 3. Frequency Options (index.html)

Removed the 6-day option. Only 3, 4, 5 days/week are available.

## Performance Tips

- Limit unit test runs to specific files: `npm test -- app.test.js`
- Use `test:watch` during development for instant feedback
- Run full suite before committing: `npm run test:all`

## Adding New Tests

1. Create test file in `tests/unit/` or `tests/e2e/`
2. Follow existing test pattern (describe/test blocks)
3. Use meaningful test names and descriptions
4. Test both success and error cases

Example:

```javascript
test('should do something specific', () => {
  const result = myFunction();
  expect(result).toBe(expectedValue);
});
```

## CI/CD Integration

These scripts can be integrated into CI/CD pipelines:

```bash
npm run test:all  # Run all tests (exit 1 if any fail)
```

## Resources

- Jest documentation: https://jestjs.io/
- Testing best practices: https://testingjavascript.com/
- E2E testing patterns: https://www.cypress.io/

## Questions?

Check the app.js console for debug logs. The code includes extensive logging:
- `🎯` - Setup phase logs
- `📌` - Button click handlers
- `🔄` - Loading operations
- `✅` - Success messages
- `❌` - Errors
