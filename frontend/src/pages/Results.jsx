import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, BarChart2 } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Progress } from '../components/ui/progress'
import { formatCurrency, computeStructuredResult } from '../lib/travy'

export function Results() {
  const [data, setData] = useState(null)
  const [travisonMeta, setTravisonMeta] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const stored = sessionStorage.getItem('travy_result')
    if (!stored) return
    try {
      const { result, prompt, travison } = JSON.parse(stored)
      setData(computeStructuredResult(result, prompt))
      setTravisonMeta(travison || null)
    } catch {
      navigate('/planner')
    }
  }, [navigate])

  if (!data) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 text-center">
        <div className="text-2xl font-black uppercase mb-2">No results yet.</div>
        <p className="mb-6 text-sm text-[var(--muted-foreground)]">
          Submit a travel request from the Planner first.
        </p>
        <Link to="/planner">
          <Button className="brutal-press">
            <ArrowLeft size={15} className="mr-2" /> GO TO PLANNER
          </Button>
        </Link>
      </main>
    )
  }

  const { plan, stops, planFit, budgetBreakdown, transparency, budget, tripTags, statusBadges } =
    data

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Hero card */}
      <div className="mb-8 border-[3px] border-black bg-[var(--yellow)] p-6 shadow-[6px_6px_0_#000]">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <span className="border-[2px] border-black bg-white px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
            OTARI_PLANNER
          </span>
          {statusBadges.map((badge) => (
            <span
              key={badge}
              className="border-[2px] border-black bg-[var(--primary)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest"
            >
              {badge}
            </span>
          ))}
        </div>
        <h1 className="text-4xl font-black uppercase leading-none tracking-tight text-black sm:text-5xl">
          {plan.title}
        </h1>
        <p className="mt-2 max-w-2xl text-sm font-medium leading-6 text-black/70">
          {plan.description}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {tripTags.map((tag) => (
            <span
              key={tag}
              className="border-[2px] border-black bg-white px-2 py-1 text-[10px] font-black uppercase tracking-widest"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        {/* Timeline */}
        <div>
          <div className="mb-5 flex items-center gap-2">
            <BarChart2 size={20} className="text-black" />
            <span className="text-xl font-black uppercase tracking-tight">
              Backend Itinerary Timeline
            </span>
          </div>
          <div className="space-y-4">
            {stops.length > 0 ? (
              stops.map((stop, i) => <StopCard key={i} stop={stop} index={i + 1} />)
            ) : (
              <div className="border-[3px] border-dashed border-black bg-[var(--muted)] p-6 text-sm font-bold text-[var(--muted-foreground)]">
                No structured stops were parsed. The raw response is shown below.
                <pre className="mt-4 whitespace-pre-wrap text-xs font-normal">
                  {data.rawResponse}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-5">
          {/* Budget Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Budget Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-3 text-xl font-black">
                {budgetBreakdown.currencySymbol}
                {Math.round(budgetBreakdown.estimatedTotal)} OF{' '}
                {budgetBreakdown.currencySymbol}
                {Math.round(budgetBreakdown.budgetPerPerson)}
              </div>
              {budgetBreakdown.budgetPerPerson > 0 && (
                <Progress
                  value={Math.min(
                    100,
                    (budgetBreakdown.estimatedTotal / budgetBreakdown.budgetPerPerson) * 100,
                  )}
                  className="mb-4"
                />
              )}
              <div className="space-y-0">
                {[
                  [
                    'Budget per person',
                    `${budgetBreakdown.currencySymbol}${Math.round(budgetBreakdown.budgetPerPerson)}`,
                  ],
                  [
                    'Estimated total',
                    `${budgetBreakdown.currencySymbol}${Math.round(budgetBreakdown.estimatedTotal)}/person`,
                  ],
                  [
                    'Budget left',
                    `${budgetBreakdown.currencySymbol}${Math.max(0, Math.round(budgetBreakdown.budgetPerPerson - budgetBreakdown.estimatedTotal))}/person`,
                  ],
                  ['Budget status', budgetBreakdown.status],
                ].map(([label, val], i) => (
                  <div
                    key={label}
                    className={`flex items-center justify-between border-[2px] border-black px-3 py-2 text-sm font-bold ${i % 2 === 0 ? 'bg-[var(--muted)]' : 'bg-white'}`}
                  >
                    <span className="font-medium text-[var(--muted-foreground)]">{label}</span>
                    <span>{val}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Plan Fit Score */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Plan Fit Score</CardTitle>
                <span className="border-[2px] border-black bg-[var(--yellow)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
                  FORMULA
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-[11px] font-medium leading-5 text-[var(--muted-foreground)]">
                Budget Fit + Mood Match + Distance Fit + Group Match + Time Fit - Fatigue Penalty
              </p>
              <div className="mb-3 text-5xl font-black">
                {planFit.score}
                <span className="text-2xl text-[var(--muted-foreground)]">/100</span>
              </div>
              <div className="mb-2 text-[10px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                OVERALL PLAN FIT
              </div>
              <Progress value={planFit.score} />
              <p className="mt-3 text-[11px] leading-5 text-[var(--muted-foreground)]">
                Travy scores the plan using distance, budget, time, group preference match,
                weather, safety, food nearby, and travel fatigue.
              </p>
            </CardContent>
          </Card>

          {/* Transparency */}
          <Card>
            <CardHeader>
              <CardTitle>Transparency</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                {[
                  ['Model', transparency.selected_model],
                  ['Complexity', String(transparency.complexity_score)],
                  ['Intent', transparency.intent],
                  ['Security', transparency.security_status],
                  ['Cost', formatCurrency(budget.current_request_cost)],
                  ['Routing', (transparency.routing_reason || '—').split('.')[0]],
                ].map(([label, val], i) => (
                  <div
                    key={label}
                    className={`flex items-start justify-between gap-3 border-[2px] border-black px-3 py-2 text-[11px] font-bold ${i % 2 === 0 ? 'bg-[var(--muted)]' : 'bg-white'}`}
                  >
                    <span className="shrink-0 font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                      {label}
                    </span>
                    <span className="text-right">{val}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {travisonMeta && (
            <Card>
              <CardHeader>
                <CardTitle>Gemini Vision Output</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-2 flex flex-wrap gap-2">
                  <span className="border-[2px] border-black bg-[var(--yellow)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
                    MODE: {travisonMeta.vision_mode || 'unknown'}
                  </span>
                  <span className="border-[2px] border-black bg-[var(--muted)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
                    SUBJECT: {travisonMeta.vision?.primary_subject || 'n/a'}
                  </span>
                </div>
                <pre className="overflow-x-auto whitespace-pre-wrap border-[2px] border-black bg-white p-3 text-xs leading-5">
                  {travisonMeta.gemini_raw_output || 'No raw vision text returned.'}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </main>
  )
}

function FitBar({ label, value, color }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[10px] font-black uppercase tracking-widest">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="h-3 overflow-hidden border-[2px] border-black bg-white">
        <div
          className="h-full transition-all"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

function StopCard({ stop, index }) {
  return (
    <div className="overflow-hidden border-[3px] border-black bg-white shadow-[4px_4px_0_#000]">
      <div className="flex">
        {/* Index badge */}
        <div className="flex w-14 shrink-0 items-center justify-center self-stretch border-r-[3px] border-black bg-[var(--yellow)]">
          <span className="text-2xl font-black">{index}</span>
        </div>
        <div className="flex-1 p-4">
          {/* Badges row */}
          <div className="mb-2 flex flex-wrap items-center gap-1.5">
            {stop.time_range && (
              <span className="border-[2px] border-black bg-[var(--muted)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
                {stop.time_range}
              </span>
            )}
            {stop.cost_per_person && (
              <span className="border-[2px] border-black bg-[var(--muted)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
                {stop.cost_per_person}
              </span>
            )}
            <span className="border-[2px] border-black bg-[var(--yellow)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
              FIT {stop.fit_score}/100
            </span>
          </div>

          <h3 className="text-lg font-black uppercase leading-tight">{stop.name}</h3>
          <p className="mt-1 text-[11px] leading-5 text-[var(--muted-foreground)]">
            {stop.description}
          </p>

          {/* Fit bars */}
          <div className="mt-3 grid grid-cols-2 gap-x-5 gap-y-2">
            <FitBar label={`BUDGET FIT ${stop.budget_fit}`} value={stop.budget_fit} color="#86efac" />
            <FitBar label={`MOOD FIT ${stop.mood_fit}`} value={stop.mood_fit} color="#f9a8d4" />
            <FitBar label={`GROUP FIT ${stop.group_fit}`} value={stop.group_fit} color="#a78bfa" />
            <FitBar
              label={`DISTANCE FIT ${stop.distance_fit}`}
              value={stop.distance_fit}
              color="#93c5fd"
            />
          </div>

          <div className="mt-3">
            <span className="border-[2px] border-black bg-[var(--muted)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
              FATIGUE: {stop.fatigue}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
