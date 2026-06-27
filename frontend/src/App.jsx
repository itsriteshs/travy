import { useMemo, useState } from 'react'
import { AlertTriangle, ShieldCheck, Wallet } from 'lucide-react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Progress } from './components/ui/progress'
import { Textarea } from './components/ui/textarea'

function App() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const budgetPercent = useMemo(() => {
    if (!result?.budget) return 100
    return Math.max(0, Math.min(100, (result.budget.remaining_budget / 2) * 100))
  }, [result])

  async function onSubmit(e) {
    e.preventDefault()
    if (!prompt.trim()) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim() }),
      })

      if (!response.ok) {
        throw new Error('Backend error while generating itinerary')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-6xl p-4 sm:p-8">
      <header className="mb-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
        <h1 className="m-0 text-3xl font-extrabold tracking-tight">Travy</h1>
        <p className="mt-2 text-sm text-[var(--muted-foreground)]">
          Mozilla.ai Cost-Aware AI Travel Assistant
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Travel Chat</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="space-y-3">
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Plan a 5 hour hangout in Delhi for 4 friends under ₹800 each with food and shopping."
              />
              <Button type="submit" disabled={loading}>
                {loading ? 'Analyzing...' : 'Send'}
              </Button>
            </form>

            {error ? (
              <p className="mt-3 flex items-center gap-2 text-sm text-red-700">
                <AlertTriangle size={16} />
                {error}
              </p>
            ) : null}

            {result ? (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle>Itinerary Response</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="m-0 whitespace-pre-wrap text-sm leading-relaxed">{result.response}</pre>
                </CardContent>
              </Card>
            ) : null}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Transparency Panel</CardTitle>
          </CardHeader>
          <CardContent>
            {!result ? (
              <p className="text-sm text-[var(--muted-foreground)]">
                Run a prompt to view model routing, security, and budget details.
              </p>
            ) : (
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span>Selected Model</span>
                  <strong>{result.transparency.selected_model}</strong>
                </div>
                <div className="flex items-center justify-between">
                  <span>Complexity</span>
                  <strong>{result.transparency.complexity_score}</strong>
                </div>
                <div className="flex items-center justify-between">
                  <span>Estimated Cost</span>
                  <strong>${result.transparency.estimated_cost}</strong>
                </div>
                <div className="flex items-center justify-between">
                  <span>Security</span>
                  <strong className="flex items-center gap-1">
                    <ShieldCheck size={16} />
                    {result.transparency.security_status}
                  </strong>
                </div>
                <div>
                  <span className="text-xs uppercase tracking-wide text-[var(--muted-foreground)]">
                    Routing Reason
                  </span>
                  <p className="mt-1">{result.transparency.routing_reason}</p>
                </div>

                <div className="rounded-lg border border-[var(--border)] bg-[var(--muted)] p-3">
                  <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase">
                    <span className="flex items-center gap-1">
                      <Wallet size={14} /> Budget Remaining
                    </span>
                    <span>${result.budget.remaining_budget}</span>
                  </div>
                  <Progress value={budgetPercent} />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  )
}

export default App
