import { Link } from 'react-router-dom'
import { ArrowRight, Map } from 'lucide-react'
import { Button } from '../components/ui/button'

const DEMO_STOPS = ['1. Janpath', '2. CP Food', '3. India Gate', '4. Dessert']

export function Home() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Hero */}
      <div className="grid gap-10 lg:grid-cols-2 lg:items-start">
        <div>
          <div className="inline-block border-[2px] border-black bg-[var(--yellow)] px-3 py-1 text-[11px] font-black uppercase tracking-[0.18em]">
            WHAT SHOULD WE ACTUALLY DO TODAY?
          </div>
          <h1 className="mt-4 text-7xl font-black uppercase leading-none tracking-tighter text-black sm:text-8xl">
            Travy
          </h1>
          <p className="mt-4 text-xl font-black leading-tight text-black">
            Cost-aware social travel assistant for real-world group plans.
          </p>
          <p className="mt-3 max-w-md text-sm leading-6 text-[var(--muted-foreground)]">
            Tell Travy your city, budget, group, time, and mood. It builds a practical
            plan while showing which model was used, why it was selected, and how much it cost.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link to="/planner">
              <Button className="brutal-press">
                START PLANNING <ArrowRight size={15} className="ml-2" />
              </Button>
            </Link>
            <Link to="/demo">
              <Button variant="secondary" className="brutal-press bg-[var(--primary)] text-black">
                VIEW ROUTING DEMO
              </Button>
            </Link>
            <Link to="/planner?inject=1">
              <Button variant="secondary" className="brutal-press">
                PROMPT INJECTION DEMO
              </Button>
            </Link>
          </div>
        </div>

        {/* Live Demo Preview */}
        <div className="border-[3px] border-black shadow-[6px_6px_0_#000]">
          <div className="flex items-center justify-between border-b-[3px] border-black bg-[var(--primary)] px-4 py-3">
            <span className="text-sm font-black uppercase tracking-widest">Live Demo Preview</span>
            <span className="border-[2px] border-black bg-[var(--yellow)] px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
              BUDGET SAFE
            </span>
          </div>
          <div className="space-y-3 bg-white p-4">
            <div className="border-[2px] border-black bg-[var(--yellow)] p-3">
              <div className="mb-1 text-[10px] font-black uppercase tracking-widest text-black/50">
                SELECTED PLAN
              </div>
              <div className="text-sm font-black">Delhi hangout: shopping + food + photos</div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {[
                { label: 'ROUTE', value: 'STRONG PLANNER', bg: 'bg-[var(--yellow)]' },
                { label: 'COST', value: '$0.045', bg: 'bg-[#bbf7d0]' },
                { label: 'FIT', value: '87/100', bg: 'bg-[var(--yellow)]' },
              ].map(({ label, value, bg }) => (
                <div key={label} className="border-[2px] border-black p-2">
                  <div className="text-[9px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                    {label}
                  </div>
                  <div className={`mt-1 border-[2px] border-black px-1.5 py-0.5 text-[10px] font-black text-center ${bg}`}>
                    {value}
                  </div>
                </div>
              ))}
            </div>
            <div className="border-[2px] border-black p-3">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                <Map size={11} />
                Map preview without real map calls
              </div>
              <div className="grid grid-cols-2 gap-1.5">
                {DEMO_STOPS.map((stop) => (
                  <div
                    key={stop}
                    className="border-[2px] border-black bg-[var(--muted)] px-2 py-1.5 text-[11px] font-bold"
                  >
                    {stop}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="my-16 border-t-[3px] border-black" />

      {/* Feature cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="border-[3px] border-black bg-[#FDBA74] p-5 shadow-[4px_4px_0_#000]">
          <h3 className="text-lg font-black">Too many tabs</h3>
          <p className="mt-2 text-sm leading-6">
            Groups bounce between maps, reviews, reels, budgets, and chats.
          </p>
        </div>
        <div className="border-[3px] border-black bg-[#F9A8D4] p-5 shadow-[4px_4px_0_#000]">
          <h3 className="text-lg font-black">Different priorities</h3>
          <p className="mt-2 text-sm leading-6">
            One friend wants food, one wants photos, one wants low walking.
          </p>
        </div>
        <div className="border-[3px] border-black bg-[#C4B5FD] p-5 shadow-[4px_4px_0_#000]">
          <h3 className="text-lg font-black">AI cost matters</h3>
          <p className="mt-2 text-sm leading-6">
            Complex planning needs reasoning, but every model call eats budget.
          </p>
        </div>
      </div>
    </main>
  )
}
