---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# TypeScript/JavaScript Testing

## E2E Testing

Use **Playwright** as the E2E testing framework for critical user flows.

## Test Doubles

Prefer FAKE implementations over mocks. A fake behaves like the real thing;
a mock only asserts that a call happened.

## Coverage

Cover behavior, not lines. Every bug fix gets a regression test that fails
before the fix and passes after.
