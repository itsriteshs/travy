import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'

export function RouterPage() {
  return <StubPage title="AI Router" description="View how the routing engine selects models based on complexity, budget, and security scores." color="bg-[var(--primary)]" />
}

export function SecurityPage() {
  return <StubPage title="Security" description="Prompt injection detection and risk scoring powered by the local Llamafile engine." color="bg-[#F9A8D4]" />
}

export function DemoPage() {
  return <StubPage title="Demo" description="Live demo of Travy with pre-loaded Delhi examples. Connect the backend to run it." color="bg-[#C4B5FD]" />
}

function StubPage({ title, description, color }) {
  return (
    <main className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className={`border-[3px] border-black p-8 shadow-[6px_6px_0_#000] ${color}`}>
        <div className="mb-2 inline-block border-[2px] border-black bg-white px-2 py-0.5 text-[10px] font-black uppercase tracking-widest">
          COMING SOON
        </div>
        <h1 className="mt-3 text-4xl font-black uppercase">{title}</h1>
        <p className="mt-3 max-w-lg text-sm leading-6">{description}</p>
        <div className="mt-6 flex gap-3">
          <Link to="/planner">
            <Button className="brutal-press">TRY THE PLANNER</Button>
          </Link>
          <Link to="/">
            <Button variant="secondary" className="brutal-press">BACK HOME</Button>
          </Link>
        </div>
      </div>
    </main>
  )
}
