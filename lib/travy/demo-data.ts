import type {
  BudgetBreakdown,
  BudgetState,
  DemoRequestState,
  FriendPreference,
  GuardianRoute,
  ItineraryStop
} from "./types";

export const defaultPrompt =
  "Plan Delhi for 4 friends from 2 PM to 8 PM. Budget is ₹800 each. We want shopping, food, and photos, not too tiring.";

export const defaultBudgetState: BudgetState = {
  totalBudgetUsd: 2,
  usedBudgetUsd: 0.18,
  remainingBudgetUsd: 1.82,
  currentRequestCostUsd: 0.045,
  mode: "healthy"
};

export const lowBudgetState: BudgetState = {
  totalBudgetUsd: 2,
  usedBudgetUsd: 1.88,
  remainingBudgetUsd: 0.12,
  currentRequestCostUsd: 0.008,
  mode: "low"
};

export const criticalBudgetState: BudgetState = {
  totalBudgetUsd: 2,
  usedBudgetUsd: 1.98,
  remainingBudgetUsd: 0.02,
  currentRequestCostUsd: 0,
  mode: "critical"
};

export const resetBudgetState: BudgetState = {
  totalBudgetUsd: 2,
  usedBudgetUsd: 0,
  remainingBudgetUsd: 2,
  currentRequestCostUsd: 0,
  mode: "healthy"
};

export const defaultRequestState: DemoRequestState = {
  city: "Delhi",
  groupSize: 4,
  budgetPerPerson: 800,
  timeWindow: "2 PM - 8 PM",
  mood: ["shopping", "food", "photos"],
  energy: "medium-low",
  budgetRemainingUsd: 1.82,
  selectedRoute: "strong_planner_model"
};

export const friendPreferences: FriendPreference[] = [
  {
    name: "Aarav",
    likes: ["Food", "Budget-friendly places"],
    avoids: ["Long travel"]
  },
  {
    name: "Maya",
    likes: ["Shopping", "Photos"],
    avoids: ["Boring food places"]
  },
  {
    name: "Ritesh",
    likes: ["Scenic spots", "Chill places"],
    avoids: ["Too much walking"]
  },
  {
    name: "Gowri",
    likes: ["Street markets", "Cafes"],
    avoids: ["Overcrowded areas"]
  }
];

export const itineraryStops: ItineraryStop[] = [
  {
    time: "2:00 PM - 3:15 PM",
    place: "Janpath Market",
    estimatedCost: "₹150-₹250/person",
    fitScore: 91,
    whySelected:
      "Cheap shopping, photo-friendly streets, central location, and easy access from CP.",
    breakdown: {
      budgetFit: 95,
      moodFit: 92,
      groupFit: 88,
      distanceFit: 84,
      fatigueScore: "Low"
    }
  },
  {
    time: "3:30 PM - 4:30 PM",
    place: "Connaught Place Food Stop",
    estimatedCost: "₹250-₹350/person",
    fitScore: 86,
    whySelected:
      "Food variety, central location, and works well for mixed preferences.",
    breakdown: {
      budgetFit: 82,
      moodFit: 88,
      groupFit: 90,
      distanceFit: 86,
      fatigueScore: "Low"
    }
  },
  {
    time: "5:00 PM - 6:15 PM",
    place: "India Gate / Kartavya Path",
    estimatedCost: "₹0/person",
    fitScore: 89,
    whySelected:
      "Free, photo-friendly, open public area, good for sunset, and balances the shopping/food-heavy plan.",
    breakdown: {
      budgetFit: 100,
      moodFit: 86,
      groupFit: 84,
      distanceFit: 78,
      fatigueScore: "Medium"
    }
  },
  {
    time: "6:30 PM - 8:00 PM",
    place: "Cafe / Dessert Stop near CP",
    estimatedCost: "₹200-₹300/person",
    fitScore: 82,
    whySelected:
      "Comfortable ending point, flexible food options, and avoids adding too much late travel.",
    breakdown: {
      budgetFit: 78,
      moodFit: 84,
      groupFit: 83,
      distanceFit: 80,
      fatigueScore: "Low"
    }
  }
];

export const budgetBreakdown: BudgetBreakdown = {
  budgetPerPerson: 800,
  food: 300,
  travel: 200,
  shoppingBuffer: 250,
  misc: 50,
  estimatedTotal: 750,
  budgetLeft: 50
};

export const guardianRoute: GuardianRoute = {
  fastestRoute: {
    time: "18 minutes",
    note: "More direct but includes less active stretches."
  },
  guardianRoute: {
    time: "22 minutes",
    note:
      "Recommended because it stays closer to active streets, open places, pickup points, and public areas."
  },
  disclaimer: "Guardian Route uses proxy signals, not live crime or traffic data.",
  signals: [
    "Open places nearby",
    "Public pickup points",
    "Walking distance",
    "Time of day",
    "Route simplicity",
    "Active area density"
  ]
};

export const routingTraceRows = [
  {
    step: 1,
    task: "Prompt injection scan",
    route: "Local filter",
    cost: "$0.000",
    reason: "Never send unsafe text to model"
  },
  {
    step: 2,
    task: "Intent extraction",
    route: "Cheap model/parser",
    cost: "$0.004",
    reason: "Simple structured extraction"
  },
  {
    step: 3,
    task: "Weather/place lookup",
    route: "API/seeded data",
    cost: "$0.000",
    reason: "Data lookup does not require AI"
  },
  {
    step: 4,
    task: "Context prioritization",
    route: "Local logic",
    cost: "$0.000",
    reason: "Rank mandatory vs optional context"
  },
  {
    step: 5,
    task: "Candidate ranking",
    route: "Local scoring",
    cost: "$0.000",
    reason: "Budget/time/mood scoring is deterministic"
  },
  {
    step: 6,
    task: "Final explanation",
    route: "Strong planner model",
    cost: "$0.041",
    reason: "Multi-step group reasoning"
  },
  {
    step: 7,
    task: "Budget update",
    route: "Local logic",
    cost: "$0.000",
    reason: "Subtract request cost from $2"
  }
];

export const featureCards = [
  {
    title: "Intent-to-Plan",
    description:
      "Describe your plan in normal language. Travy extracts city, time, budget, group size, and mood."
  },
  {
    title: "Group Blend Mode",
    description:
      "Balances different friend preferences like shopping, food, photos, low crowd, and low fatigue."
  },
  {
    title: "Plan Fit Score",
    description:
      "Ranks places by budget, mood, time, distance, group match, weather, and fatigue."
  },
  {
    title: "Guardian Route",
    description:
      "Suggests a comfortable route using proxy signals like active areas, open places, and walking effort."
  },
  {
    title: "Cost-Aware AI Routing",
    description:
      "Uses local logic, APIs, cheap models, or stronger models depending on task complexity and budget."
  },
  {
    title: "Prompt Injection Protection",
    description:
      "Blocks suspicious event/review/offer text before it reaches the AI model."
  }
];
