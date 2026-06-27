export type BudgetMode = "healthy" | "low" | "critical";

export type ParsedTravelRequest = {
  city: string;
  groupSize: number;
  budgetPerPerson: number;
  startTime: string;
  endTime: string;
  timeWindow: string;
  moods: string[];
  energy: string;
  transport: string;
  crowdTolerance: string;
  needsRouteOrdering: boolean;
  usesPastPreferences: boolean;
};

export type InjectionScanResult = {
  safe: boolean;
  detected: string[];
  riskScore: number;
  action: "allowed" | "blocked";
};

export type RouteDecision = {
  route:
    | "BLOCKED"
    | "API_ONLY_FALLBACK"
    | "CHEAP_MODEL_COMPRESSED_CONTEXT"
    | "LOCAL_OR_API"
    | "CHEAP_MODEL"
    | "BALANCED_MODEL"
    | "STRONG_PLANNER_MODEL";
  model: "none" | "cheap_model" | "balanced_model" | "strong_planner_model";
  label: string;
  reason: string;
  cost: number;
};

export type BudgetState = {
  totalBudgetUsd: number;
  usedBudgetUsd: number;
  remainingBudgetUsd: number;
  currentRequestCostUsd: number;
  mode: BudgetMode;
};

export type DemoRequestState = {
  city: string;
  groupSize: number;
  budgetPerPerson: number;
  timeWindow: string;
  mood: string[];
  energy: string;
  budgetRemainingUsd: number;
  selectedRoute: string;
};

export type FriendPreference = {
  name: string;
  likes: string[];
  avoids: string[];
};

export type ItineraryStop = {
  time: string;
  place: string;
  estimatedCost: string;
  fitScore: number;
  whySelected: string;
  breakdown: {
    budgetFit: number;
    moodFit: number;
    groupFit: number;
    distanceFit: number;
    fatigueScore: "Low" | "Medium" | "High";
  };
};

export type GuardianRoute = {
  fastestRoute: {
    time: string;
    note: string;
  };
  guardianRoute: {
    time: string;
    note: string;
  };
  disclaimer: string;
  signals: string[];
};

export type BudgetBreakdown = {
  budgetPerPerson: number;
  food: number;
  travel: number;
  shoppingBuffer: number;
  misc: number;
  estimatedTotal: number;
  budgetLeft: number;
};

export type ContextSelection = {
  included: string[];
  dropped: string[];
  mode: "full_context" | "low_budget" | "critical_budget";
};
