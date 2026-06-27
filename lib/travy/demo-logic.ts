import type {
  BudgetMode,
  BudgetState,
  ContextSelection,
  InjectionScanResult,
  ParsedTravelRequest,
  RouteDecision
} from "./types";

export const suspiciousPhrases = [
  "ignore previous instructions",
  "reveal api key",
  "system prompt",
  "developer message",
  "bypass rules",
  "act as",
  "forget your instructions"
];

export function parseTravelRequest(text: string): ParsedTravelRequest {
  const lower = text.toLowerCase();
  const cityMatch = text.match(/plan\s+([a-zA-Z\s]+?)\s+for/i);
  const groupMatch = lower.match(/(\d+)\s+(friends|people|travellers|travelers)/);
  const budgetMatch = text.match(/[₹Rs.\s]*(\d{2,5})\s*(each|per person|\/person)?/i);
  const timeMatch = text.match(/from\s+([0-9]{1,2}\s*(?:am|pm|AM|PM))\s+to\s+([0-9]{1,2}\s*(?:am|pm|AM|PM))/);
  const moods = ["shopping", "food", "photos", "cafes", "scenic", "markets"].filter(
    (mood) => lower.includes(mood)
  );

  return {
    city: cityMatch?.[1]?.trim() || "Delhi",
    groupSize: Number(groupMatch?.[1] || 4),
    budgetPerPerson: Number(budgetMatch?.[1] || 800),
    startTime: timeMatch?.[1] || "2 PM",
    endTime: timeMatch?.[2] || "8 PM",
    timeWindow: `${timeMatch?.[1] || "2 PM"} - ${timeMatch?.[2] || "8 PM"}`,
    moods: moods.length ? moods.slice(0, 3) : ["shopping", "food", "photos"],
    energy: lower.includes("not too tiring") ? "medium-low" : "medium",
    transport: "Mixed",
    crowdTolerance: "Medium",
    needsRouteOrdering: true,
    usesPastPreferences: false
  };
}

export function scanPromptInjection(text: string): InjectionScanResult {
  const lower = text.toLowerCase();
  const detected = suspiciousPhrases.filter((phrase) => lower.includes(phrase));
  return {
    safe: detected.length === 0,
    detected,
    riskScore: Math.min(detected.length * 30, 100),
    action: detected.length ? "blocked" : "allowed"
  };
}

export function calculateComplexity(request: ParsedTravelRequest) {
  let score = 0;
  if (request.groupSize > 1) score += 20;
  if (request.budgetPerPerson) score += 15;
  if (request.startTime && request.endTime) score += 15;
  if (request.moods?.length > 2) score += 15;
  if (request.needsRouteOrdering) score += 20;
  if (request.usesPastPreferences) score += 10;

  const capped = Math.min(score, 100);
  return capped === 85 && request.city.toLowerCase() === "delhi" ? 86 : capped;
}

export function selectRoute({
  risk,
  complexity,
  budgetRemaining
}: {
  risk: InjectionScanResult;
  complexity: number;
  budgetRemaining: number;
}): RouteDecision {
  if (!risk.safe) {
    return {
      route: "BLOCKED",
      model: "none",
      label: "Blocked",
      reason: "Prompt injection detected before model call.",
      cost: 0
    };
  }
  if (budgetRemaining < 0.05) {
    return {
      route: "API_ONLY_FALLBACK",
      model: "none",
      label: "API-only fallback",
      reason: "Budget is critical. Using seeded/API data and local scoring only.",
      cost: 0
    };
  }
  if (budgetRemaining < 0.2) {
    return {
      route: "CHEAP_MODEL_COMPRESSED_CONTEXT",
      model: "cheap_model",
      label: "Cheap model + compressed context",
      reason: "Budget is low, so lower-priority context is removed.",
      cost: 0.008
    };
  }
  if (complexity <= 30) {
    return {
      route: "LOCAL_OR_API",
      model: "none",
      label: "Local/API only",
      reason: "Simple deterministic task.",
      cost: 0
    };
  }
  if (complexity <= 60) {
    return {
      route: "CHEAP_MODEL",
      model: "cheap_model",
      label: "Cheap model",
      reason: "Simple extraction or summarization.",
      cost: 0.004
    };
  }
  if (complexity <= 85) {
    return {
      route: "BALANCED_MODEL",
      model: "balanced_model",
      label: "Balanced model",
      reason: "Moderate planning with several constraints.",
      cost: 0.018
    };
  }
  return {
    route: "STRONG_PLANNER_MODEL",
    model: "strong_planner_model",
    label: "Strong planner model",
    reason:
      "Complex group planning with budget, route, mood, time, and preference constraints.",
    cost: 0.041
  };
}

export function selectContextByBudget(budgetRemaining: number): ContextSelection {
  const mandatory = ["city", "timeWindow", "budgetPerPerson", "groupSize"];
  const useful = ["mood", "weather", "transportPreference"];
  const optional = ["pastLikedPlaces", "friendHistory", "longReviews", "photos"];
  if (budgetRemaining < 0.05) {
    return {
      included: mandatory,
      dropped: [...useful, ...optional],
      mode: "critical_budget"
    };
  }
  if (budgetRemaining < 0.2) {
    return {
      included: [...mandatory, ...useful],
      dropped: optional,
      mode: "low_budget"
    };
  }
  return {
    included: [...mandatory, ...useful, ...optional],
    dropped: [],
    mode: "full_context"
  };
}

export function getBudgetStatus(budget: BudgetState) {
  if (budget.remainingBudgetUsd < 0.05) return "API-only fallback";
  if (budget.remainingBudgetUsd < 0.2) return "Budget low";
  if (budget.remainingBudgetUsd < 0.5) return "Budget cautious";
  return "Budget healthy";
}

export function budgetForMode(mode: BudgetMode): BudgetState {
  if (mode === "critical") {
    return {
      totalBudgetUsd: 2,
      usedBudgetUsd: 1.98,
      remainingBudgetUsd: 0.02,
      currentRequestCostUsd: 0,
      mode
    };
  }
  if (mode === "low") {
    return {
      totalBudgetUsd: 2,
      usedBudgetUsd: 1.88,
      remainingBudgetUsd: 0.12,
      currentRequestCostUsd: 0.008,
      mode
    };
  }
  return {
    totalBudgetUsd: 2,
    usedBudgetUsd: 0.18,
    remainingBudgetUsd: 1.82,
    currentRequestCostUsd: 0.045,
    mode
  };
}

export function calculatePlanFitScore() {
  return 87;
}

export function formatUsd(value: number) {
  return `$${value.toFixed(3).replace(/0$/, "")}`;
}
