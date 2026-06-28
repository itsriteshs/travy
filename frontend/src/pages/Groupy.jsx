import { useRef, useState } from 'react'
import { Plus, Trash2, Users, Sparkles } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Progress } from '../components/ui/progress'
import { AudioRecorder } from '../components/AudioRecorder'
import { buildGroupyPrompt, computeStructuredResult, formatCurrency, submitGroupyPrompt } from '../lib/travy'

const MAX_PEOPLE = 5

function createPerson(id) {
  return {
    id,
    notes: '',
  }
}

export function Groupy() {
  const nextPersonIdRef = useRef(2)
  const [people, setPeople] = useState([createPerson(1)])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  function addPerson() {
    setPeople((current) => {
      if (current.length >= MAX_PEOPLE) return current
      const nextPerson = createPerson(nextPersonIdRef.current)
      nextPersonIdRef.current += 1
      return [...current, nextPerson]
    })
  }

  function removePerson(id) {
    setPeople((current) => {
      if (current.length <= 1) return current
      return current.filter((person) => person.id !== id)
    })
  }

  function updateNotes(id, text) {
    setPeople((current) =>
      current.map((person) =>
        person.id === id
          ? {
              ...person,
              notes: person.notes ? `${person.notes}\n${text}` : text,
            }
          : person,
      ),
    )
  }

  async function generatePlan() {
    const prompt = buildGroupyPrompt(people)
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await submitGroupyPrompt(people)
      setResult(computeStructuredResult(response, prompt))
    } catch (err) {
      setError(err.message || 'Unable to send Groupy details to the AI agent.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-4 inline-flex items-center gap-2 border-[2px] border-black bg-[var(--yellow)] px-3 py-1 text-[11px] font-black uppercase tracking-[0.18em]">
        <Users size={14} />
        Groupy
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.35fr_0.65fr] lg:items-start">
        <section className="space-y-4">
          <div>
            <h1 className="text-4xl font-black uppercase leading-none tracking-tight sm:text-5xl">
              Collect each person&apos;s mood and wish separately.
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--muted-foreground)]">
              Add up to five people, then let each person record their own mood, wish to visit,
              or both. The transcription is kept inside that person&apos;s slot.
            </p>
          </div>

          <div className="space-y-3">
            {people.map((person, index) => (
              <article key={person.id} className="border-[3px] border-black bg-white p-4 shadow-[5px_5px_0_#000]">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                      Person {index + 1}
                    </div>
                    <div className="text-lg font-black">Mood + wish</div>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <AudioRecorder
                      onTranscribed={(text) => updateNotes(person.id, text)}
                      recordLabel="record"
                      showUpload={false}
                    />
                    <Button
                      type="button"
                      onClick={() => removePerson(person.id)}
                      disabled={people.length <= 1}
                      variant="secondary"
                      className="brutal-press gap-2 border-[2px] border-black bg-white text-black hover:bg-[var(--muted)] disabled:opacity-50"
                    >
                      <Trash2 size={14} />
                      Remove
                    </Button>
                  </div>
                </div>

                <textarea
                  value={person.notes}
                  onChange={(e) =>
                    setPeople((current) =>
                      current.map((slot) =>
                        slot.id === person.id ? { ...slot, notes: e.target.value } : slot,
                      ),
                    )
                  }
                  rows={4}
                  placeholder="Recorded mood, wish, or any extra note..."
                  className="mt-4 w-full border-[2px] border-black bg-[var(--muted)] px-3 py-2 text-sm font-medium outline-none"
                />
              </article>
            ))}
          </div>

          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              onClick={addPerson}
              disabled={people.length >= MAX_PEOPLE}
              className="brutal-press gap-2"
            >
              <Plus size={15} />
              Add person
            </Button>
            <Button
              type="button"
              onClick={generatePlan}
              disabled={loading}
              className="brutal-press gap-2 bg-black text-white hover:bg-black/90"
            >
              <Sparkles size={15} />
              {loading ? 'Sending to AI...' : 'Send to AI agent'}
            </Button>
            <div className="flex items-center border-[2px] border-black bg-[var(--muted)] px-3 py-2 text-[11px] font-black uppercase tracking-widest">
              {people.length} / {MAX_PEOPLE} people
            </div>
          </div>

          {error && (
            <div className="border-[3px] border-red-600 bg-red-50 px-4 py-3 text-sm font-bold text-red-800">
              {error}
            </div>
          )}
        </section>

        <aside className="border-[3px] border-black bg-[var(--primary)] p-5 shadow-[5px_5px_0_#000]">
          <div className="text-[10px] font-black uppercase tracking-widest text-black/60">
            How it works
          </div>
          <div className="mt-2 text-2xl font-black uppercase leading-tight">
            One slot per person.
          </div>
          <p className="mt-3 text-sm leading-6 text-black/80">
            Use Groupy when the trip depends on different moods or wishes from different people.
            Each recording stays separate so you can compare preferences before planning.
          </p>
        </aside>
      </div>

      {result && (
        <div className="mt-10 border-t-[3px] border-black pt-8">
          <div className="mb-4 text-[11px] font-black uppercase tracking-[0.18em] text-[var(--muted-foreground)]">
            Structured view generated from the AI response
          </div>
          <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <div>
              <div className="mb-5 flex items-center gap-2">
                <Users size={20} className="text-black" />
                <span className="text-xl font-black uppercase tracking-tight">
                  Groupy Itinerary Timeline
                </span>
              </div>
              <div className="space-y-4">
                {result.stops.length > 0 ? (
                  result.stops.map((stop, index) => <StopCard key={index} stop={stop} index={index + 1} />)
                ) : (
                  <div className="border-[3px] border-dashed border-black bg-[var(--muted)] p-6 text-sm font-bold text-[var(--muted-foreground)]">
                    No structured stops were parsed. The raw response is shown below.
                    <pre className="mt-4 whitespace-pre-wrap text-xs font-normal">{result.rawResponse}</pre>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-5">
              <Card>
                <CardHeader>
                  <CardTitle>Plan Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-3 text-xl font-black">{result.plan.title}</div>
                  <p className="text-sm leading-6 text-[var(--muted-foreground)]">
                    {result.plan.description}
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {result.tripTags.map((tag) => (
                      <span
                        key={tag}
                        className="border-[2px] border-black bg-[var(--yellow)] px-2 py-1 text-[10px] font-black uppercase tracking-widest"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Plan Fit Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-3 text-5xl font-black">
                    {result.planFit.score}
                    <span className="text-2xl text-[var(--muted-foreground)]">/100</span>
                  </div>
                  <Progress value={result.planFit.score} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Budget Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-3 text-xl font-black">
                    {result.budgetBreakdown.currencySymbol}
                    {Math.round(result.budgetBreakdown.estimatedTotal)} OF{' '}
                    {result.budgetBreakdown.currencySymbol}
                    {Math.round(result.budgetBreakdown.budgetPerPerson)}
                  </div>
                  <div className="space-y-0">
                    {[
                      [
                        'Budget per person',
                        `${result.budgetBreakdown.currencySymbol}${Math.round(result.budgetBreakdown.budgetPerPerson)}`,
                      ],
                      [
                        'Estimated total',
                        `${result.budgetBreakdown.currencySymbol}${Math.round(result.budgetBreakdown.estimatedTotal)}/person`,
                      ],
                      [
                        'Budget left',
                        `${result.budgetBreakdown.currencySymbol}${Math.max(0, Math.round(result.budgetBreakdown.budgetPerPerson - result.budgetBreakdown.estimatedTotal))}/person`,
                      ],
                      ['Budget status', result.budgetBreakdown.status],
                    ].map(([label, val], index) => (
                      <div
                        key={label}
                        className={`flex items-center justify-between border-[2px] border-black px-3 py-2 text-sm font-bold ${index % 2 === 0 ? 'bg-[var(--muted)]' : 'bg-white'}`}
                      >
                        <span className="font-medium text-[var(--muted-foreground)]">{label}</span>
                        <span>{val}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Transparency</CardTitle>
                </CardHeader>
                <CardContent>
                  <div>
                    {[
                      ['Model', result.transparency.selected_model],
                      ['Complexity', String(result.transparency.complexity_score)],
                      ['Intent', result.transparency.intent],
                      ['Security', result.transparency.security_status],
                      ['Cost', formatCurrency(result.budget.current_request_cost)],
                      ['Routing', (result.transparency.routing_reason || '—').split('.')[0]],
                    ].map(([label, val], index) => (
                      <div
                        key={label}
                        className={`flex items-start justify-between gap-3 border-[2px] border-black px-3 py-2 text-[11px] font-bold ${index % 2 === 0 ? 'bg-[var(--muted)]' : 'bg-white'}`}
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
            </div>
          </div>
          <div className="mt-4 border-[2px] border-black bg-[var(--muted)] p-3 text-[11px] text-[var(--muted-foreground)]">
            Generated from {people.length} group notes.
          </div>
        </div>
      )}
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
        <div className="flex w-14 shrink-0 items-center justify-center self-stretch border-r-[3px] border-black bg-[var(--yellow)]">
          <span className="text-2xl font-black">{index}</span>
        </div>
        <div className="flex-1 p-4">
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

          <div className="mt-3 grid grid-cols-2 gap-x-5 gap-y-2">
            <FitBar label={`BUDGET FIT ${stop.budget_fit}`} value={stop.budget_fit} color="#86efac" />
            <FitBar label={`MOOD FIT ${stop.mood_fit}`} value={stop.mood_fit} color="#f9a8d4" />
            <FitBar label={`GROUP FIT ${stop.group_fit}`} value={stop.group_fit} color="#a78bfa" />
            <FitBar label={`DISTANCE FIT ${stop.distance_fit}`} value={stop.distance_fit} color="#93c5fd" />
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