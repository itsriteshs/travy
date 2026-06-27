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

export type BackendField<T> = {
  value: T;
  confidence?: number;
  source?: string;
};

export type BackendTraceRow = {
  step: number;
  task: string;
  route: string;
  status?: string;
  cost_usd: number;
  reason: string;
};

export type BackendAnalysis = {
  request_id: string;
  next_action: "generate" | "clarify" | "block" | "fallback" | "out_of_scope";
  security: {
    safe: boolean;
    risk_score: number;
    detected: string[];
    action: string;
    model_call_allowed?: boolean;
  };
  intent: {
    type: string;
    reason: string;
  };
  parsed: {
    city: BackendField<string>;
    group_size: BackendField<number>;
    budget_per_person_inr: BackendField<number>;
    start_time: BackendField<string>;
    end_time: BackendField<string>;
    moods: BackendField<string[]>;
    energy: BackendField<string>;
    transport: BackendField<string>;
    crowd_tolerance: BackendField<string>;
  };
  missing_fields: string[];
  parser: {
    overall_confidence: number;
    used_otari_extractor: boolean;
    otari_success: boolean;
    reason: string;
  };
  complexity: {
    score: number;
    breakdown?: Array<{ label?: string; feature?: string; points: number; reason: string }>;
  };
  budget: {
    mode: BudgetMode | "auto";
    limit_usd?: number;
    remaining_usd?: number;
    actual_used_usd?: number;
    estimated_request_cost_usd?: number;
  };
  context: {
    mode: "full_context" | "low_budget" | "api_only_fallback" | "critical_budget";
    included?: string[];
    dropped?: string[];
    included_context?: string[];
    dropped_context?: string[];
  };
  route_decision: {
    route: string;
    model_tier: string;
    model_id: string;
    model_configured?: boolean;
    estimated_cost_usd: number;
    reason: string;
  };
  routing_trace: BackendTraceRow[];
};

export type BackendGeneration = {
  request_id: string;
  status: "success" | "blocked" | "clarify" | "out_of_scope" | "error";
  result_id?: string;
  generated_at?: string;
  message?: string;
  source?: {
    analysis_request_id?: string;
    generation_method?: string;
    fallback_used?: boolean;
  };
  api_evidence?: Record<string, Record<string, string | number | boolean | null>>;
  itinerary?: {
    title?: string;
    summary?: string;
    stops?: Array<{
      stop_number?: number;
      place_id?: string;
      name?: string;
      category?: string;
      start_time?: string;
      end_time?: string;
      estimated_cost_per_person_inr?: number;
      why_selected?: string[];
      source_provider?: string;
      confidence?: number;
      total_score?: number;
      score_breakdown?: Array<{ feature: string; points: number; reason: string }>;
    }>;
    total_estimated_cost_per_person_inr?: number;
    budget_status?: string;
    total_travel_time_minutes?: number;
  };
  guardian_route?: {
    enabled: boolean;
    label: string;
    confidence: number;
    fastest_route_minutes: number;
    guardian_route_minutes: number;
    tradeoff_minutes: number;
    reasons: string[];
    data_used: string[];
    data_not_used: string[];
  };
  validation?: {
    passed: boolean;
    checks: string[];
    warnings: string[];
    fallback_used: boolean;
  };
  budget_breakdown?: {
    budget_per_person_inr?: number;
    estimated_total?: number;
    budget_left?: number;
    budget_status?: string;
    [key: string]: string | number | boolean | undefined;
  };
  routing_trace?: BackendTraceRow[];
};

export type BackendHealth = {
  overall_status?: string;
  services?: Record<string, { status?: string; latency_ms?: number; details?: unknown }>;
};

export type BackendUsage = {
  total_requests?: number;
  budget_remaining_usd?: number;
  total_cost_usd?: number;
};

export type SecurityScanResult = {
  safe: boolean;
  risk_score: number;
  detected: string[];
  action: string;
  model_call_allowed?: boolean;
};
