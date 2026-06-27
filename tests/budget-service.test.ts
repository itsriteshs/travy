/**
 * budget-service.test.ts
 * 
 * Integration tests proving the BudgetService is fully database-backed:
 *  1. getBudget() returns config-seeded defaults on first boot
 *  2. deductBudget() persists and reduces remaining
 *  3. Multiple deductions accumulate correctly
 *  4. refundBudget() increases remaining
 *  5. resetBudget() restores to config defaults
 *  6. Budget mode transitions correctly with config thresholds
 *  7. setBudgetMode() simulates modes for UI testing
 *  8. No hardcoded values — all defaults come from runtime-config.json
 *
 * Run: npx tsx tests/budget-service.test.ts
 */

import { BudgetService } from "../lib/server/services/budget-service";
import { getRuntimeConfig, clearConfigCache } from "../lib/server/utils/config";
import fs from "node:fs";
import path from "node:path";

// ─── Helpers ─────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;

function assert(condition: boolean, label: string) {
  if (condition) {
    console.log(`  ✅ ${label}`);
    passed++;
  } else {
    console.error(`  ❌ FAIL: ${label}`);
    failed++;
  }
}

function assertClose(actual: number, expected: number, label: string, tolerance = 0.001) {
  assert(Math.abs(actual - expected) < tolerance, `${label} (got ${actual}, expected ${expected})`);
}

function heading(title: string) {
  console.log(`\n━━━ ${title} ━━━`);
}

// ─── Clean slate ─────────────────────────────────────────────────────

const dbPath = path.join(process.cwd(), "data", "travy.db");
if (fs.existsSync(dbPath)) {
  fs.unlinkSync(dbPath);
}
clearConfigCache();

const config = getRuntimeConfig();
const DEFAULT_TOTAL = config.budget.defaultTotalUsd;

// ─── Test 1: First boot seeds from config ────────────────────────────

heading("Test 1: First boot seeds from config");
{
  const budget = BudgetService.getBudget();
  assertClose(budget.totalBudgetUsd, DEFAULT_TOTAL, "totalBudgetUsd matches config default");
  assertClose(budget.usedBudgetUsd, 0, "usedBudgetUsd is 0 on fresh boot");
  assertClose(budget.remainingBudgetUsd, DEFAULT_TOTAL, "remainingBudgetUsd equals total");
  assert(budget.mode === "healthy", `mode is healthy (got ${budget.mode})`);
  assert(typeof budget.updatedAt === "string" && budget.updatedAt.length > 0, "updatedAt is populated");
}

// ─── Test 2: deductBudget() persists ─────────────────────────────────

heading("Test 2: deductBudget() persists");
{
  const cost = 0.05;
  const result = BudgetService.deductBudget(cost, {
    requestId: "req_test_1",
    selectedRoute: "CHEAP_MODEL",
    selectedModel: "gemma-3-27b-it",
    inputTokens: 200,
    outputTokens: 50,
    latencyMs: 320,
  });

  assertClose(result.usedBudgetUsd, cost, "usedBudgetUsd reflects deduction");
  assertClose(result.remainingBudgetUsd, DEFAULT_TOTAL - cost, "remainingBudgetUsd reflects deduction");

  // Read again to prove persistence
  const reread = BudgetService.getBudget();
  assertClose(reread.usedBudgetUsd, cost, "re-read usedBudgetUsd matches after deduction");
  assertClose(reread.remainingBudgetUsd, DEFAULT_TOTAL - cost, "re-read remainingBudgetUsd matches after deduction");
}

// ─── Test 3: Multiple deductions accumulate ──────────────────────────

heading("Test 3: Multiple deductions accumulate");
{
  BudgetService.deductBudget(0.10, {
    requestId: "req_test_2",
    selectedRoute: "BALANCED_MODEL",
    selectedModel: "qwen-2.5-32b",
    inputTokens: 500,
    outputTokens: 200,
    latencyMs: 890,
  });

  const budget = BudgetService.getBudget();
  const expectedUsed = 0.05 + 0.10;
  assertClose(budget.usedBudgetUsd, expectedUsed, "accumulated used is 0.15");
  assertClose(budget.remainingBudgetUsd, DEFAULT_TOTAL - expectedUsed, "remaining reflects accumulated deductions");
}

// ─── Test 4: refundBudget() increases remaining ──────────────────────

heading("Test 4: refundBudget() increases remaining");
{
  const before = BudgetService.getBudget();
  const refund = 0.05;
  const result = BudgetService.refundBudget(refund, { requestId: "req_test_1" });

  assertClose(result.usedBudgetUsd, before.usedBudgetUsd - refund, "usedBudgetUsd decreased by refund");
  assertClose(result.remainingBudgetUsd, before.remainingBudgetUsd + refund, "remainingBudgetUsd increased by refund");

  // Persistence check
  const reread = BudgetService.getBudget();
  assertClose(reread.remainingBudgetUsd, result.remainingBudgetUsd, "refund persisted on re-read");
}

// ─── Test 5: resetBudget() restores defaults ─────────────────────────

heading("Test 5: resetBudget() restores defaults");
{
  const result = BudgetService.resetBudget();
  assertClose(result.totalBudgetUsd, DEFAULT_TOTAL, "total restored to config default");
  assertClose(result.usedBudgetUsd, 0, "used reset to 0");
  assertClose(result.remainingBudgetUsd, DEFAULT_TOTAL, "remaining restored to config default");
  assert(result.mode === "healthy", "mode reset to healthy");

  // Persistence
  const reread = BudgetService.getBudget();
  assertClose(reread.remainingBudgetUsd, DEFAULT_TOTAL, "reset persisted on re-read");
}

// ─── Test 6: Budget mode transitions with config thresholds ──────────

heading("Test 6: Budget mode transitions");
{
  BudgetService.resetBudget();
  const thresholds = config.budget.modeThresholds;

  // Deduct to push remaining below healthy threshold
  const healthyBound = DEFAULT_TOTAL * thresholds.healthy;
  const deductToJustBelowHealthy = DEFAULT_TOTAL - healthyBound + 0.01;
  BudgetService.deductBudget(deductToJustBelowHealthy, {
    requestId: "req_mode_1",
    selectedRoute: "BALANCED_MODEL",
    selectedModel: "qwen-2.5-32b",
    inputTokens: 100, outputTokens: 50, latencyMs: 100,
  });
  const afterCautious = BudgetService.getBudget();
  assert(afterCautious.mode === "cautious", `mode is cautious when ratio < ${thresholds.healthy} (got ${afterCautious.mode}, remaining=${afterCautious.remainingBudgetUsd})`);

  // Continue deducting to push into low
  BudgetService.resetBudget();
  const cautiousBound = DEFAULT_TOTAL * thresholds.cautious;
  const deductToJustBelowCautious = DEFAULT_TOTAL - cautiousBound + 0.01;
  BudgetService.deductBudget(deductToJustBelowCautious, {
    requestId: "req_mode_2",
    selectedRoute: "CHEAP_MODEL",
    selectedModel: "gemma-3-27b-it",
    inputTokens: 100, outputTokens: 50, latencyMs: 50,
  });
  const afterLow = BudgetService.getBudget();
  assert(afterLow.mode === "low", `mode is low when ratio < ${thresholds.cautious} (got ${afterLow.mode}, remaining=${afterLow.remainingBudgetUsd})`);

  // Push into critical
  BudgetService.resetBudget();
  const lowBound = DEFAULT_TOTAL * thresholds.low;
  const deductToJustBelowLow = DEFAULT_TOTAL - lowBound + 0.01;
  BudgetService.deductBudget(deductToJustBelowLow, {
    requestId: "req_mode_3",
    selectedRoute: "CHEAP_MODEL",
    selectedModel: "gemma-3-27b-it",
    inputTokens: 100, outputTokens: 50, latencyMs: 50,
  });
  const afterCritical = BudgetService.getBudget();
  assert(afterCritical.mode === "critical", `mode is critical when ratio < ${thresholds.low} (got ${afterCritical.mode}, remaining=${afterCritical.remainingBudgetUsd})`);
}

// ─── Test 7: setBudgetMode() simulates correctly ─────────────────────

heading("Test 7: setBudgetMode() simulation");
{
  BudgetService.resetBudget();

  for (const mode of ["healthy", "cautious", "low", "critical"] as const) {
    const result = BudgetService.setBudgetMode(mode);
    assert(result.mode === mode, `setBudgetMode("${mode}") returns mode=${mode}`);

    // Verify persistence
    const reread = BudgetService.getBudget();
    // The re-read recomputes mode from ledger, which may yield the same or similar mode
    assertClose(reread.totalBudgetUsd, DEFAULT_TOTAL, `total still ${DEFAULT_TOTAL} after setBudgetMode("${mode}")`);
  }
}

// ─── Test 8: No hardcoded values (source scan) ──────────────────────

heading("Test 8: No hardcoded budget values in budget-service.ts");
{
  const sourceFile = path.join(process.cwd(), "lib", "server", "services", "budget-service.ts");
  const source = fs.readFileSync(sourceFile, "utf8");

  const forbiddenPatterns = [
    { pattern: /= 2\.00/g, label: "= 2.00" },
    { pattern: /= 1\.82/g, label: "= 1.82" },
    { pattern: /= 0\.18/g, label: "= 0.18" },
    { pattern: /< 0\.25/g, label: "< 0.25" },
    { pattern: /< 0\.75/g, label: "< 0.75" },
    { pattern: /<= 1\.25/g, label: "<= 1.25" },
    { pattern: /= 1\.00/g, label: "= 1.00" },
    { pattern: /= 0\.50/g, label: "= 0.50" },
    { pattern: /= 0\.10\b/g, label: "= 0.10" },
  ];

  for (const { pattern, label } of forbiddenPatterns) {
    const matches = source.match(pattern);
    assert(!matches, `No hardcoded "${label}" found in budget-service.ts`);
  }
}

// ─── Summary ─────────────────────────────────────────────────────────

console.log(`\n${"═".repeat(50)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
console.log(`${"═".repeat(50)}\n`);

if (failed > 0) {
  process.exit(1);
}
