"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, DatabaseZap, RefreshCw } from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoButton } from "@/components/ui/neo-button";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { BudgetMeter } from "@/components/travy/budget-meter";
import { ContextPriorityTable } from "@/components/travy/context-priority-table";
import { PipelineTrace } from "@/components/travy/pipeline-trace";
import { RoutingTable } from "@/components/travy/routing-table";
import { defaultBudgetState } from "@/lib/travy/demo-data";
import {
  budgetFromAnalysis,
  contextFromBackend,
  getIntegrationHealth,
  getLiveUsage,
  getRouterTrace,
  parsedFromBackend,
  routingRowsFromTrace
} from "@/lib/travy/backend-api";
import { getLatestAnalysis } from "@/lib/travy/storage";
import type { BackendAnalysis, BackendHealth, BackendTraceRow, BackendUsage } from "@/lib/travy/types";

export default function AiRouterPage() {
  const [analysis, setAnalysis] = useState<BackendAnalysis | null>(null);
  const [trace, setTrace] = useState<BackendTraceRow[]>([]);
  const [usage, setUsage] = useState<BackendUsage | null>(null);
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadBackendRouterState() {
    setLoading(true);
    setError("");
    const latest = getLatestAnalysis();
    setAnalysis(latest);
    try {
      const [nextUsage, nextHealth, nextTrace] = await Promise.all([
        getLiveUsage(),
        getIntegrationHealth(),
        latest ? getRouterTrace(latest.request_id) : Promise.resolve([])
      ]);
      setUsage(nextUsage);
      setHealth(nextHealth);
      setTrace(nextTrace);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Could not load backend router state.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadBackendRouterState();
  }, []);

  const parsed = useMemo(() => (analysis ? parsedFromBackend(analysis) : null), [analysis]);
  const budget = useMemo(() => (analysis ? budgetFromAnalysis(analysis) : defaultBudgetState), [analysis]);
  const context = useMemo(() => (analysis ? contextFromBackend(analysis) : { included: [], dropped: [], mode: "full_context" as const }), [analysis]);
  const rows = useMemo(() => routingRowsFromTrace(trace.length ? trace : analysis?.routing_trace || []), [analysis, trace]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-8 max-w-4xl">
        <NeoBadge tone="lavender">Backend Otari Transparency</NeoBadge>
        <h1 className="mt-3 text-5xl font-black leading-none md:text-6xl">
          AI Router: live route, cost, context, and health.
        </h1>
        <p className="mt-4 text-lg font-semibold leading-8 text-zinc-800">
          This page reads the latest FastAPI analysis and router trace. If it is empty,
          run a request through Planner first.
        </p>
        <NeoButton
          className="mt-4"
          onClick={loadBackendRouterState}
          leftIcon={<RefreshCw className="h-4 w-4" aria-hidden />}
        >
          {loading ? "Refreshing..." : "Refresh Backend State"}
        </NeoButton>
      </div>

      {error && (
        <NeoCard tone="danger" strong className="mb-6">
          <NeoCardTitle>Backend unavailable</NeoCardTitle>
          <p className="mt-2 font-bold">{error}</p>
        </NeoCard>
      )}

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="space-y-6">
          <BudgetMeter budget={budget} />
          <NeoCard tone="yellow" strong>
            <NeoCardTitle>Current Backend Request</NeoCardTitle>
            {analysis ? (
              <>
                <p className="mt-3 rounded-neo border-2 border-black bg-white p-4 font-bold leading-7">
                  {parsed?.city} | {parsed?.groupSize} traveler(s) | ₹{parsed?.budgetPerPerson}/person | {parsed?.timeWindow}
                </p>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {[
                    ["Selected Route", analysis.route_decision.route],
                    ["Model Tier", analysis.route_decision.model_tier],
                    ["Model ID", analysis.route_decision.model_id || "none"],
                    ["Estimated Cost", `$${analysis.route_decision.estimated_cost_usd.toFixed(3)}`],
                    ["Context Mode", analysis.context.mode],
                    ["Next Action", analysis.next_action]
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-neo border-2 border-black bg-white p-3">
                      <div className="text-xs font-black uppercase">{label}</div>
                      <div className="font-bold break-words">{value}</div>
                    </div>
                  ))}
                </div>
                <p className="mt-4 rounded-neo border-2 border-black bg-travySunwash p-3 text-sm font-bold">
                  {analysis.route_decision.reason}
                </p>
              </>
            ) : (
              <p className="mt-3 rounded-neo border-2 border-black bg-white p-4 font-bold">
                No backend analysis stored yet. Open Planner, analyze a request, then return here.
              </p>
            )}
          </NeoCard>
          <NeoCard tone="paper" strong>
            <NeoCardTitle>Model Selection Logic</NeoCardTitle>
            <pre className="mt-4 overflow-x-auto rounded-neo border-2 border-black bg-travyInk p-4 font-mono text-sm font-bold leading-7 text-white">
{`If prompt injection is detected:
    BLOCKED, no model call
If deterministic budget math:
    LOCAL_LOGIC
If fields are missing:
    CLARIFY_REQUIRED
If budget is critical:
    API_ONLY_FALLBACK
If complexity is high and budget is low:
    COMPRESSED_CHEAP_MODEL
If complexity is high and budget is healthy:
    STRONG_PLANNER_MODEL`}
            </pre>
          </NeoCard>
        </div>
        <div className="space-y-6">
          <PipelineTrace
            steps={[
              "Prompt",
              "Security",
              "Intent",
              "Parser",
              "Complexity",
              "Budget",
              "Context",
              "Router",
              "Generation"
            ]}
          />
          <RoutingTable title="Backend Routing Trace Table" rows={rows} />
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <NeoCard tone="blue" strong>
          <NeoCardTitle>Complexity Score</NeoCardTitle>
          <div className="mt-4 font-mono text-6xl font-black">{analysis?.complexity.score ?? 0}/100</div>
          <div className="mt-4 space-y-2">
            {(analysis?.complexity.breakdown || []).map((item) => (
              <div key={`${item.label || item.feature}-${item.points}`} className="rounded-neo border-2 border-black bg-white p-2 font-bold shadow-neoSm">
                {item.label || item.feature}: +{item.points} — {item.reason}
              </div>
            ))}
          </div>
          <NeoBadge className="mt-4" tone="yellow">
            {analysis?.route_decision.model_tier || "No model selected"}
          </NeoBadge>
        </NeoCard>
        <ContextPriorityTable context={context} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <NeoCard tone="mint" strong>
          <NeoCardTitle className="flex items-center gap-2">
            <Activity className="h-6 w-6" aria-hidden />
            Live Usage
          </NeoCardTitle>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {[
              ["Requests", String(usage?.total_requests ?? 0)],
              ["Used", `$${(usage?.total_cost_usd ?? 0).toFixed(3)}`],
              ["Remaining", `$${(usage?.budget_remaining_usd ?? 0).toFixed(3)}`]
            ].map(([label, value]) => (
              <div key={label} className="rounded-neo border-2 border-black bg-white p-3">
                <div className="text-xs font-black uppercase">{label}</div>
                <div className="font-mono text-2xl font-black">{value}</div>
              </div>
            ))}
          </div>
        </NeoCard>
        <NeoCard tone="paper" strong>
          <NeoCardTitle className="flex items-center gap-2">
            <DatabaseZap className="h-6 w-6" aria-hidden />
            Integration Health
          </NeoCardTitle>
          <div className="mt-4 flex flex-wrap gap-2">
            <NeoBadge tone={health?.overall_status === "healthy" ? "mint" : "orange"}>
              Overall: {health?.overall_status || "unknown"}
            </NeoBadge>
            {Object.entries(health?.services || {}).map(([service, value]) => (
              <NeoBadge key={service} tone={value.status === "healthy" || value.status === "ok" ? "mint" : "orange"}>
                {service}: {value.status || "unknown"}
              </NeoBadge>
            ))}
          </div>
        </NeoCard>
      </div>
    </div>
  );
}
