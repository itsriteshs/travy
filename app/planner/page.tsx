"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, BrainCircuit, Users } from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoButton } from "@/components/ui/neo-button";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { NeoTextarea } from "@/components/ui/neo-textarea";
import { BudgetMeter } from "@/components/travy/budget-meter";
import { ContextPriorityTable } from "@/components/travy/context-priority-table";
import { RoutingTable } from "@/components/travy/routing-table";
import { defaultBudgetState, defaultPrompt, friendPreferences } from "@/lib/travy/demo-data";
import {
  calculateComplexity,
  parseTravelRequest,
  scanPromptInjection,
  selectContextByBudget,
  selectRoute
} from "@/lib/travy/demo-logic";
import { setBudgetState, setDemoRequest } from "@/lib/travy/storage";

const routingRows = [
  {
    task: "Prompt injection scan",
    route: "Local filter",
    cost: "$0.000",
    reason: "Security check before model"
  },
  {
    task: "Extract city/budget/time",
    route: "Cheap model/parser",
    cost: "$0.004",
    reason: "Simple structure extraction"
  },
  {
    task: "Fetch weather/place data",
    route: "API/seeded data",
    cost: "$0.000",
    reason: "Data lookup does not need AI"
  },
  {
    task: "Calculate budget",
    route: "Local logic",
    cost: "$0.000",
    reason: "Deterministic math"
  },
  {
    task: "Rank candidate places",
    route: "Local scoring",
    cost: "$0.000",
    reason: "Faster and cheaper"
  },
  {
    task: "Generate final itinerary explanation",
    route: "Strong planner model",
    cost: "$0.041",
    reason: "Multi-constraint reasoning"
  }
];

export default function PlannerPage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState(defaultPrompt);
  const [analyzed, setAnalyzed] = useState(false);
  const parsed = useMemo(() => parseTravelRequest(prompt), [prompt]);
  const scan = useMemo(() => scanPromptInjection(prompt), [prompt]);
  const complexity = useMemo(() => calculateComplexity(parsed), [parsed]);
  const context = useMemo(
    () => selectContextByBudget(defaultBudgetState.remainingBudgetUsd),
    []
  );
  const route = useMemo(
    () =>
      selectRoute({
        risk: scan,
        complexity,
        budgetRemaining: defaultBudgetState.remainingBudgetUsd
      }),
    [scan, complexity]
  );

  function generatePlan() {
    setDemoRequest({
      city: parsed.city,
      groupSize: parsed.groupSize,
      budgetPerPerson: parsed.budgetPerPerson,
      timeWindow: parsed.timeWindow,
      mood: parsed.moods,
      energy: parsed.energy,
      budgetRemainingUsd: defaultBudgetState.remainingBudgetUsd,
      selectedRoute: route.model
    });
    setBudgetState(defaultBudgetState);
    router.push("/results");
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-8 max-w-4xl">
        <NeoBadge tone="yellow">Planner</NeoBadge>
        <h1 className="mt-3 text-5xl font-black leading-none md:text-6xl">
          Natural language planning, routed by budget.
        </h1>
        <p className="mt-4 text-lg font-semibold leading-8 text-zinc-800">
          Type a messy group request. Travy parses it, scans for risk, prioritizes
          context, picks a route, and shows the model-cost tradeoff before results.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <div className="space-y-6">
          <NeoCard tone="paper" strong>
            <NeoTextarea
              label="Assistant-style travel request"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Example: Plan Delhi for 4 friends from 2 PM to 8 PM. Budget is ₹800 each. We want shopping, food, and photos, not too tiring."
              helperText="No backend or AI call is made here. This runs local frontend logic."
            />
            <div className="mt-4 flex flex-wrap gap-3">
              <NeoButton onClick={() => setAnalyzed(true)} leftIcon={<BrainCircuit className="h-4 w-4" aria-hidden />}>
                Analyze & Route Request
              </NeoButton>
              <NeoBadge tone={scan.safe ? "mint" : "danger"}>
                Scan: {scan.safe ? "Safe" : "Blocked"}
              </NeoBadge>
            </div>
          </NeoCard>

          {analyzed ? (
            <>
              <NeoCard tone="yellow" strong>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <NeoCardTitle>Extracted Trip Fields</NeoCardTitle>
                    <p className="mt-1 text-sm font-bold">
                      Travy converted the natural request into structured planning constraints.
                    </p>
                  </div>
                  <NeoBadge tone="mint">Editable-looking demo fields</NeoBadge>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {[
                    ["City", parsed.city],
                    ["Group size", String(parsed.groupSize)],
                    ["Budget/person", `₹${parsed.budgetPerPerson}`],
                    ["Time window", parsed.timeWindow],
                    ["Mood", parsed.moods.join(", ")],
                    ["Energy", parsed.energy],
                    ["Transport", parsed.transport],
                    ["Crowd tolerance", parsed.crowdTolerance]
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-neo border-2 border-black bg-white p-3 shadow-neoSm">
                      <div className="text-xs font-black uppercase">{label}</div>
                      <div className="font-bold capitalize">{value}</div>
                    </div>
                  ))}
                </div>
              </NeoCard>

              <NeoCard tone="pink" strong>
                <div className="mb-4 flex items-center gap-2">
                  <Users className="h-6 w-6" aria-hidden />
                  <NeoCardTitle>Group Blend Mode</NeoCardTitle>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {friendPreferences.map((friend) => (
                    <div key={friend.name} className="rounded-neo border-2 border-black bg-white p-3 shadow-neoSm">
                      <div className="text-lg font-black">{friend.name}</div>
                      <p className="text-sm font-bold">Likes: {friend.likes.join(", ")}</p>
                      <p className="text-sm font-bold">Avoids: {friend.avoids.join(", ")}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-4 rounded-neo border-2 border-black bg-travySunwash p-4">
                  <div className="text-xs font-black uppercase">Group Blend Result</div>
                  <p className="text-xl font-black">
                    Shopping + food + photos with medium walking and low cost.
                  </p>
                  <p className="mt-1 text-sm font-bold">
                    The hard part of group travel is not finding places. It is getting everyone to agree.
                  </p>
                </div>
              </NeoCard>
            </>
          ) : (
            <NeoCard tone="lavender" strong>
              <NeoCardTitle>Ready when you are</NeoCardTitle>
              <p className="mt-2 font-bold">
                Click Analyze & Route Request to reveal extracted fields, group blend,
                context priority, and routing preview.
              </p>
            </NeoCard>
          )}
        </div>

        <div className="space-y-6">
          <BudgetMeter budget={defaultBudgetState} />
          {analyzed && (
            <>
              <ContextPriorityTable context={context} />
              <NeoCard tone="blue" strong>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <NeoCardTitle>Routing Preview</NeoCardTitle>
                    <p className="mt-1 text-sm font-bold">
                      This request has multiple people, budget limits, route ordering,
                      mood matching, and time constraints.
                    </p>
                  </div>
                  <NeoBadge tone="yellow">{route.label}</NeoBadge>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {[
                    ["Task Type", "Group Travel Planning"],
                    ["Complexity Score", `${complexity}/100`],
                    ["Risk Score", scan.safe ? "Low" : `${scan.riskScore}/100`],
                    ["Budget Remaining", "$1.82 / $2.00"],
                    ["Selected Route", route.label],
                    ["Estimated Cost", `$${route.cost.toFixed(3)}`]
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-neo border-2 border-black bg-white p-3 shadow-neoSm">
                      <div className="text-xs font-black uppercase">{label}</div>
                      <div className="font-bold">{value}</div>
                    </div>
                  ))}
                </div>
                <p className="mt-4 rounded-neo border-2 border-black bg-travySunwash p-3 text-sm font-bold">
                  Travy will use local/API logic for deterministic steps and a stronger model only for final itinerary reasoning.
                </p>
              </NeoCard>
              <RoutingTable rows={routingRows} />
              <NeoButton
                size="lg"
                className="w-full"
                onClick={generatePlan}
                disabled={!scan.safe}
                rightIcon={<ArrowRight className="h-5 w-5" aria-hidden />}
              >
                Generate Smart Plan
              </NeoButton>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
