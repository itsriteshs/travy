import { useEffect, useMemo, useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  MapPinned,
  ShieldCheck,
  Sparkles,
  Wallet,
} from 'lucide-react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Progress } from './components/ui/progress'
import { Textarea } from './components/ui/textarea'
import { fetchBudgetSnapshot, formatCurrency, formatRatio, parseItineraryResponse, submitTravelPrompt } from './lib/travy'

const emptyBudget = {
  totalBudget: 2,
  currentSpend: 0,
  remainingBudget: 2,
}

function App() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [budgetSnapshot, setBudgetSnapshot] = useState(emptyBudget)

  useEffect(() => {
    let isMounted = true

    async function loadBudget() {
      try {
        const snapshot = await fetchBudgetSnapshot()
        if (isMounted) {
          setBudgetSnapshot(snapshot)
        }
      } catch {
        if (isMounted) {
          setBudgetSnapshot(emptyBudget)
        }
      }
    }

    loadBudget()

    return () => {
      isMounted = false
    }
  }, [])

  const budgetPercent = useMemo(() => {
    const totalBudget = result?.budget?.total_budget ?? budgetSnapshot.totalBudget
    const remainingBudget = result?.budget?.remaining_budget ?? budgetSnapshot.remainingBudget
    if (!totalBudget) return 0
    return Math.max(0, Math.min(100, (remainingBudget / totalBudget) * 100))
  }, [budgetSnapshot.remainingBudget, budgetSnapshot.totalBudget, result])

  const itinerary = useMemo(() => {
    if (!result?.response) return null
    return parseItineraryResponse(result.response)
  }, [result])

  async function onSubmit(e) {
    e.preventDefault()
    if (!prompt.trim()) return

    setLoading(true)
    setError('')

    try {
      const data = await submitTravelPrompt(prompt.trim())
      setResult(data)
      setBudgetSnapshot({
        totalBudget: Number(data.budget?.total_budget ?? budgetSnapshot.totalBudget),
        currentSpend: Number(data.budget?.total_spend ?? budgetSnapshot.currentSpend),
        remainingBudget: Number(data.budget?.remaining_budget ?? budgetSnapshot.remainingBudget),
      })
    } catch (err) {
      setError(err.message || 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  const runtimeStatus = result?.transparency?.security_status || 'Awaiting request'
  const selectedModel = result?.transparency?.selected_model || '—'
  const complexityScore = result?.transparency?.complexity_score ?? '—'
  const estimatedCost = result?.transparency?.estimated_cost ?? 0
  const requestCost = result?.budget?.current_request_cost ?? 0
  const currentSpend = result?.budget?.total_spend ?? budgetSnapshot.currentSpend
  const remainingBudget = result?.budget?.remaining_budget ?? budgetSnapshot.remainingBudget
  const totalBudget = result?.budget?.total_budget ?? budgetSnapshot.totalBudget

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Top bar */}
      <header className="border-b-[3px] border-black bg-[var(--primary)] px-5 py-3">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <MapPinned size={22} className="text-black" />
            <span className="text-xl font-black uppercase tracking-widest text-black">Travy</span>
          </div>
          <div className="flex items-center gap-2">
            {['Chat', 'Routing', 'Budget', 'Itinerary'].map((tag) => (
              <span key={tag} className="hidden border-[2px] border-black bg-white px-2 py-0.5 text-[11px] font-black uppercase tracking-widest sm:inline-block">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Hero + Input */}
        <section className="mb-8 grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="border-[3px] border-black bg-[var(--yellow)] p-6 shadow-[6px_6px_0_#000] lg:p-8">
            <div className="mb-3 inline-flex items-center gap-2 border-[2px] border-black bg-white px-3 py-1 text-[11px] font-black uppercase tracking-[0.2em]">
              <Sparkles size={13} /> Live MVP
            </div>
            <h1 className="text-5xl font-black uppercase leading-none tracking-tight text-black sm:text-6xl lg:text-7xl">
              Plan<br />Your<br />Trip.
            </h1>
            <p className="mt-4 max-w-md text-sm font-medium leading-6 text-black/70">
              Cost-aware travel planning with live local routing, budget enforcement, and Otari itinerary generation.
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Planner Input</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={onSubmit} className="space-y-4">
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe city, budget, group size, timing, and what the trip needs to include."
                />
                <div className="flex flex-wrap items-center gap-3">
                  <Button type="submit" disabled={loading} className="brutal-press">
                    {loading ? 'Analyzing...' : 'Send to /api/chat'}
                  </Button>
                  <span className="text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                    Backend-driven only
                  </span>
                </div>
              </form>
              {error ? (
                <div className="mt-4 flex items-center gap-2 border-[3px] border-black bg-red-100 px-3 py-2 text-sm font-bold text-red-800">
                  <AlertTriangle size={16} />
                  {error}
                </div>
              ) : null}
            </CardContent>
          </Card>
        </section>

        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          {/* Itinerary */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Itinerary</CardTitle>
              </CardHeader>
              <CardContent>
                {!result ? (
                  <div className="border-[3px] border-dashed border-black bg-[var(--muted)] p-6 text-sm font-medium leading-7 text-[var(--muted-foreground)]">
                    Send a travel request to render the live itinerary from the backend response.
                  </div>
                ) : itinerary ? (
                  <div className="space-y-5">
                    <div className="border-[3px] border-black bg-[var(--muted)] p-4 shadow-[4px_4px_0_#000]">
                      <div className="flex flex-wrap items-center gap-2 text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                        <MapPinned size={13} />
                        Travel Response
                      </div>
                      <h2 className="mt-2 text-2xl font-black uppercase tracking-tight">{itinerary.title}</h2>
                      <p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-[var(--foreground)]">
                        {itinerary.summary || itinerary.rawText}
                      </p>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
                        <div className="mb-3 text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                          Travel Order
                        </div>
                        {itinerary.travelOrder.length ? (
                          <ol className="space-y-2 text-sm leading-6">
                            {itinerary.travelOrder.map((step, index) => (
                              <li key={`${step}-${index}`} className="flex gap-2">
                                <span className="font-black text-[var(--primary)]">{index + 1}.</span>
                                <span>{step}</span>
                              </li>
                            ))}
                          </ol>
                        ) : (
                          <p className="text-sm text-[var(--muted-foreground)]">Travel order will appear here when the model returns it.</p>
                        )}
                      </div>

                      <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
                        <div className="mb-3 text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                          Estimated Spending
                        </div>
                        {itinerary.spending.length ? (
                          <ul className="space-y-2 text-sm leading-6">
                            {itinerary.spending.map((item, index) => (
                              <li key={`${item}-${index}`} className="flex gap-2">
                                <ArrowRight size={16} className="mt-1 shrink-0 text-[var(--accent)]" />
                                <span>{item}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-[var(--muted-foreground)]">Estimated spend breakdown will come from the backend response.</p>
                        )}
                      </div>
                    </div>

                    <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
                      <div className="mb-3 text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                        Timeline
                      </div>
                      {itinerary.timeline.length ? (
                        <div className="space-y-3">
                          {itinerary.timeline.map((item, index) => (
                            <div key={`${item.time}-${item.title}-${index}`} className="border-[2px] border-black bg-[var(--muted)] p-4">
                              <div className="flex flex-wrap items-center gap-2 text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                                <span className="border-[2px] border-black bg-[var(--yellow)] px-2 py-0.5 text-[10px] font-black tracking-widest text-black">
                                  {item.time}
                                </span>
                                <span>{item.title}</span>
                              </div>
                              <p className="mt-2 text-sm leading-6 text-[var(--foreground)]">{item.detail}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-[var(--muted-foreground)]">Timeline entries are extracted from the Otari response.</p>
                      )}
                    </div>

                    <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
                      <div className="mb-3 text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                        Places
                      </div>
                      {itinerary.places.length ? (
                        <div className="flex flex-wrap gap-2">
                          {itinerary.places.map((place, index) => (
                            <span key={`${place}-${index}`} className="border-[2px] border-black bg-[var(--yellow)] px-3 py-1 text-sm font-bold">
                              {place}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-[var(--muted-foreground)]">Places mentioned in the itinerary will appear here.</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <pre className="m-0 whitespace-pre-wrap text-sm leading-7 text-[var(--foreground)]">{result.response}</pre>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right column */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Transparency Panel</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 text-sm">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <Metric label="Selected Model" value={selectedModel} />
                    <Metric label="Complexity Score" value={complexityScore} />
                    <Metric label="Estimated Cost" value={formatCurrency(estimatedCost)} />
                    <Metric label="Security Status" value={runtimeStatus} icon={<ShieldCheck size={15} />} />
                  </div>

                  <div className="border-[3px] border-black bg-[var(--muted)] p-4">
                    <div className="text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                      Routing Reason
                    </div>
                    <p className="mt-2 leading-6 text-[var(--foreground)]">
                      {result?.transparency?.routing_reason || 'Routing details will appear after the first request.'}
                    </p>
                  </div>

                  <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
                    <div className="mb-3 flex items-center justify-between text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                      <span className="flex items-center gap-2"><Wallet size={14} /> Budget Meter</span>
                      <span className="border-[2px] border-black bg-[var(--yellow)] px-2 py-0.5 text-black">{formatCurrency(remainingBudget)} left</span>
                    </div>
                    <Progress value={budgetPercent} />
                    <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                      <RuntimeTile label="Current Spend" value={formatCurrency(currentSpend)} />
                      <RuntimeTile label="Remaining" value={formatCurrency(remainingBudget)} />
                      <RuntimeTile label="Request Cost" value={formatCurrency(requestCost)} />
                      <RuntimeTile label="Total Budget" value={formatCurrency(totalBudget)} />
                    </div>
                  </div>

                  <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
                    <div className="text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                      Budget Progress
                    </div>
                    <div className="mt-2 flex items-center justify-between text-sm font-bold">
                      <span>{formatRatio(((totalBudget - remainingBudget) / (totalBudget || 1)) * 100)} used</span>
                      <span>{formatRatio((remainingBudget / (totalBudget || 1)) * 100)} remaining</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Runtime State</CardTitle>
              </CardHeader>
              <CardContent>
                {!result ? (
                  <p className="text-sm leading-7 text-[var(--muted-foreground)]">
                    No request has been sent yet. Panel is bound to live backend budget data.
                  </p>
                ) : (
                  <div className="space-y-0 text-sm">
                    {[
                      ['Intent', result.transparency.intent],
                      ['Category', result.transparency.category],
                      ['Cache Hit', result.transparency.cache_hit ? 'Yes' : 'No'],
                      ['Budget Exhausted', result.budget.exhausted ? 'Yes' : 'No'],
                      ['Downgraded', result.budget.downgraded ? 'Yes' : 'No'],
                    ].map(([label, val], i) => (
                      <div key={label} className={`flex items-center justify-between gap-3 border-[2px] border-black px-3 py-2 font-medium ${i % 2 === 0 ? 'bg-[var(--muted)]' : 'bg-white'}`}>
                        <span className="text-[11px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">{label}</span>
                        <strong className="text-right">{val}</strong>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}

function Metric({ label, value, icon }) {
  return (
    <div className="border-[3px] border-black bg-[var(--muted)] p-3 shadow-[3px_3px_0_#000]">
      <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
        {icon}
        {label}
      </div>
      <div className="mt-2 break-words text-base font-black text-[var(--foreground)]">{value}</div>
    </div>
  )
}

function RuntimeTile({ label, value }) {
  return (
    <div className="border-[2px] border-black bg-[var(--muted)] p-3">
      <div className="text-[10px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">{label}</div>
      <div className="mt-1 text-sm font-black text-[var(--foreground)]">{value}</div>
    </div>
  )
}

export default App
