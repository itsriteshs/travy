import { Link, useLocation } from 'react-router-dom'
import { User } from 'lucide-react'

const NAV_LINKS = [
  { path: '/', label: 'Home' },
  { path: '/groupy', label: 'Groupy' },
  { path: '/travison', label: 'Travison' },
  { path: '/planner', label: 'Planner' },
  { path: '/results', label: 'Results' },
]

export function Nav() {
  const { pathname } = useLocation()

  return (
    <nav className="border-b-[3px] border-black bg-[#FFFDF5]">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5 sm:px-6">
        <Link
          to="/"
          className="flex items-center gap-2 border-[2px] border-black bg-[var(--yellow)] px-3 py-1.5 text-sm font-black brutal-press"
        >
          <User size={15} />
          Travy
        </Link>
        <div className="flex items-center gap-1 flex-wrap">
          {NAV_LINKS.map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              className={`border-[2px] border-black px-3 py-1.5 text-[12px] font-black uppercase tracking-wide brutal-press ${
                pathname === path
                  ? 'bg-[var(--primary)] text-black'
                  : 'bg-white hover:bg-[var(--muted)]'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}
