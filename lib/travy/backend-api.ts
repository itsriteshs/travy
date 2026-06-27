import type {
  BackendAnalysis,
  BackendGeneration,
  BackendHealth,
  BackendTraceRow,
  BackendUsage,
  BudgetState,
  ContextSelection,
  GuardianRoute,
  ItineraryStop,
  ParsedTravelRequest,
  SecurityScanResult
} from "./types";

const DEFAULT_BACKEND_URL = "http://localhost:8080";

export function getBackendUrl() {
  return (process.env.NEXT_PUBLIC_BACKEND_URL || DEFAULT_BACKEND_URL).replace(/\/$/, "");
}

async function backendFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${getBackendUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    }
  });

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const message = data?.detail || data?.message || `Backend request failed: ${res.status}`;
    throw new Error(message);
  }
  return data as T;
}

export function analyzePlanner(prompt: string, budgetMode: string, sessionId = "demo") {
  return backendFetch<BackendAnalysis>("/api/planner/analyze", {
    method: "POST",
    body: JSON.stringify({ prompt, budget_mode: budgetMode, session_id: sessionId })
  });
}

export function generatePlanner(requestId: string, sessionId = "demo") {
  return backendFetch<BackendGeneration>("/api/planner/generate", {
    method: "POST",
    body: JSON.stringify({ request_id: requestId, session_id: sessionId })
  });
}

export function scanSecurityText(text: string) {
  return backendFetch<SecurityScanResult>("/api/security/scan", {
    method: "POST",
    body: JSON.stringify({ text })
  });
}

export function getRouterTrace(requestId: string) {
  return backendFetch<BackendTraceRow[]>(`/api/router/trace/${requestId}`);
}

export function getLiveUsage() {
  return backendFetch<BackendUsage>("/api/router/live-usage");
}

export function getIntegrationHealth() {
  return backendFetch<BackendHealth>("/api/integrations/health");
}

export function runDemoScenario(scenario: string, sessionId = "demo") {
  return backendFetch<{
    status: string;
    scenario: string;
    request_id: string;
    next_action: BackendAnalysis["next_action"];
    analysis: BackendAnalysis;
    generation: BackendGeneration | null;
  }>("/api/demo/run-scenario", {
    method: "POST",
    body: JSON.stringify({ scenario, session_id: sessionId })
  });
}

export function parsedFromBackend(analysis: BackendAnalysis): ParsedTravelRequest {
  const startTime = analysis.parsed.start_time.value || "";
  const endTime = analysis.parsed.end_time.value || "";
  return {
    city: analysis.parsed.city.value || "Unknown city",
    groupSize: analysis.parsed.group_size.value || 1,
    budgetPerPerson: analysis.parsed.budget_per_person_inr.value || 0,
    startTime,
    endTime,
    timeWindow: startTime && endTime ? `${startTime} - ${endTime}` : "Flexible",
    moods: analysis.parsed.moods.value || [],
    energy: analysis.parsed.energy.value || "medium",
    transport: analysis.parsed.transport.value || "Flexible",
    crowdTolerance: analysis.parsed.crowd_tolerance.value || "Medium",
    needsRouteOrdering: analysis.route_decision.route !== "LOCAL_LOGIC",
    usesPastPreferences: false
  };
}

export function budgetFromAnalysis(analysis: BackendAnalysis): BudgetState {
  const total = analysis.budget.limit_usd ?? 2;
  const used = analysis.budget.actual_used_usd ?? Math.max(total - (analysis.budget.remaining_usd ?? total), 0);
  const remaining = analysis.budget.remaining_usd ?? Math.max(total - used, 0);
  const mode = analysis.budget.mode === "auto" ? "healthy" : analysis.budget.mode;
  return {
    totalBudgetUsd: total,
    usedBudgetUsd: used,
    remainingBudgetUsd: remaining,
    currentRequestCostUsd: analysis.route_decision.estimated_cost_usd || analysis.budget.estimated_request_cost_usd || 0,
    mode
  };
}

export function contextFromBackend(analysis: BackendAnalysis): ContextSelection {
  const mode = analysis.context.mode === "api_only_fallback" ? "critical_budget" : analysis.context.mode;
  return {
    mode,
    included: analysis.context.included || analysis.context.included_context || [],
    dropped: analysis.context.dropped || analysis.context.dropped_context || []
  };
}

export function routingRowsFromTrace(trace: BackendTraceRow[]) {
  return trace.map((row) => ({
    step: row.step,
    task: row.task,
    route: row.route,
    cost: `$${row.cost_usd.toFixed(3)}`,
    reason: row.reason
  }));
}

function scoreFromBreakdown(stop: BackendGeneration["itinerary"] extends infer I
  ? I extends { stops?: Array<infer S> }
    ? S
    : never
  : never) {
  const breakdown = Array.isArray(stop?.score_breakdown) ? stop.score_breakdown : [];
  const total = typeof stop?.total_score === "number" ? stop.total_score : breakdown.reduce((sum, item) => sum + (item.points || 0), 0);
  return Math.max(60, Math.min(100, Math.round(total || 82)));
}

function breakdownPoint(stop: BackendGeneration["itinerary"] extends infer I
  ? I extends { stops?: Array<infer S> }
    ? S
    : never
  : never, feature: string, fallback: number) {
  const item = stop?.score_breakdown?.find((entry) => entry.feature === feature);
  return Math.max(0, Math.min(100, Math.round(((item?.points || fallback) / 30) * 100)));
}

export function stopsFromGeneration(generation: BackendGeneration): ItineraryStop[] {
  return (generation.itinerary?.stops || []).map((stop, index) => {
    const start = stop.start_time || "Flexible";
    const end = stop.end_time ? ` - ${stop.end_time}` : "";
    const why = Array.isArray(stop.why_selected) ? stop.why_selected.join(" ") : "Selected by backend plan ranking.";
    return {
      time: `${start}${end}`,
      place: stop.name || `Stop ${index + 1}`,
      estimatedCost: `₹${stop.estimated_cost_per_person_inr ?? 0}/person`,
      fitScore: scoreFromBreakdown(stop),
      whySelected: `${why} Source: ${stop.source_provider || "backend"}.`,
      breakdown: {
        budgetFit: breakdownPoint(stop, "budget_fit", 20),
        moodFit: breakdownPoint(stop, "mood_match", 20),
        groupFit: breakdownPoint(stop, "provider_confidence", 4),
        distanceFit: breakdownPoint(stop, "distance_efficiency", 12),
        fatigueScore: scoreFromBreakdown(stop) > 85 ? "Low" : "Medium"
      }
    };
  });
}

export function guardianFromGeneration(generation: BackendGeneration): GuardianRoute | undefined {
  const route = generation.guardian_route;
  if (!route) return undefined;
  return {
    fastestRoute: {
      time: `${route.fastest_route_minutes} min`,
      note: "Shortest route from backend distance optimizer."
    },
    guardianRoute: {
      time: `${route.guardian_route_minutes} min`,
      note: `${route.label}: +${route.tradeoff_minutes} min for comfort-aware routing.`
    },
    disclaimer: `Uses ${route.data_used.join(", ")}. Does not use ${route.data_not_used.join(", ")}.`,
    signals: route.reasons
  };
}

export function planFitScore(generation: BackendGeneration) {
  const stops = stopsFromGeneration(generation);
  if (!stops.length) return 0;
  return Math.round(stops.reduce((sum, stop) => sum + stop.fitScore, 0) / stops.length);
}
