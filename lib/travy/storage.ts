"use client";

import {
  defaultBudgetState,
  defaultRequestState
} from "./demo-data";
import type { BackendAnalysis, BackendGeneration, BudgetMode, BudgetState, DemoRequestState } from "./types";

export const storageKeys = {
  request: "travy-demo-request",
  budget: "travy-budget-state",
  budgetMode: "travy-budget-mode",
  routeHighlight: "travy-route-highlight",
  securityDemo: "travy-security-demo",
  latestAnalysis: "travy-latest-backend-analysis",
  latestGeneration: "travy-latest-backend-generation",
  backendError: "travy-backend-error"
} as const;

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  const raw = window.localStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson<T>(key: string, value: T) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

export function getDemoRequest() {
  return readJson<DemoRequestState>(storageKeys.request, defaultRequestState);
}

export function setDemoRequest(request: DemoRequestState) {
  writeJson(storageKeys.request, request);
}

export function getBudgetState() {
  return readJson<BudgetState>(storageKeys.budget, defaultBudgetState);
}

export function setBudgetState(budget: BudgetState) {
  writeJson(storageKeys.budget, budget);
  window.localStorage.setItem(storageKeys.budgetMode, budget.mode);
}

export function getBudgetMode() {
  if (typeof window === "undefined") return "healthy" as BudgetMode;
  return (window.localStorage.getItem(storageKeys.budgetMode) || "healthy") as BudgetMode;
}

export function setRouteHighlight(value: boolean) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(storageKeys.routeHighlight, String(value));
}

export function getRouteHighlight() {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(storageKeys.routeHighlight) === "true";
}

export function setSecurityDemo(value: boolean) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(storageKeys.securityDemo, String(value));
}

export function getLatestAnalysis() {
  return readJson<BackendAnalysis | null>(storageKeys.latestAnalysis, null);
}

export function setLatestAnalysis(analysis: BackendAnalysis) {
  writeJson(storageKeys.latestAnalysis, analysis);
}

export function getLatestGeneration() {
  return readJson<BackendGeneration | null>(storageKeys.latestGeneration, null);
}

export function setLatestGeneration(generation: BackendGeneration) {
  writeJson(storageKeys.latestGeneration, generation);
}

export function clearLatestBackendRun() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(storageKeys.latestAnalysis);
  window.localStorage.removeItem(storageKeys.latestGeneration);
  window.localStorage.removeItem(storageKeys.backendError);
}

export function setBackendError(message: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(storageKeys.backendError, message);
}

export function getBackendError() {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(storageKeys.backendError) || "";
}

export function resetDemoState() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(storageKeys.routeHighlight);
  window.localStorage.removeItem(storageKeys.securityDemo);
  clearLatestBackendRun();
  setDemoRequest(defaultRequestState);
  setBudgetState({
    totalBudgetUsd: 2,
    usedBudgetUsd: 0,
    remainingBudgetUsd: 2,
    currentRequestCostUsd: 0,
    mode: "healthy"
  });
}
