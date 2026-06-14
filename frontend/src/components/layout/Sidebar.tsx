import { motion } from 'framer-motion'
import { TerminalSquare, BarChart3, Leaf, Settings } from 'lucide-react'
import type { NavView } from '../../types/api'
import { cn } from '../../utils/helpers'

interface Props {
  active: NavView
  onChange: (v: NavView) => void
}

const NAV: { id: NavView; label: string; icon: React.ElementType }[] = [
  { id: 'query', label: 'Query', icon: TerminalSquare },
  { id: 'stats', label: 'Stats', icon: BarChart3 },
  { id: 'impact', label: 'Impact', icon: Leaf },
  { id: 'settings', label: 'Settings', icon: Settings },
]

export function Sidebar({ active, onChange }: Props) {
  return (
    <aside className="w-60 shrink-0 flex flex-col bg-slate-900 dark:bg-slate-950 border-r border-slate-800 min-h-screen">
      {/* Logo */}
      <div className="px-5 py-6 flex items-center gap-3">
        <div className="relative w-9 h-9">
          <div className="absolute inset-0 rounded-full bg-emerald-500 opacity-20 animate-pulse-slow" />
          <div className="absolute inset-1 rounded-full bg-emerald-500 opacity-40 animate-pulse-slow" style={{ animationDelay: '0.5s' }} />
          <div className="absolute inset-2 rounded-full bg-emerald-400 flex items-center justify-center">
            <Leaf className="w-3.5 h-3.5 text-slate-900" />
          </div>
        </div>
        <div>
          <div className="text-white font-semibold leading-tight">Green Cache</div>
          <div className="text-emerald-400 text-xs font-medium">Semantic LLM Cache</div>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-4 border-t border-slate-800 mb-2" />

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-1">
        {NAV.map(({ id, label, icon: Icon }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => onChange(id)}
              className={cn(
                'relative w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150',
                isActive
                  ? 'text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              )}
            >
              {isActive && (
                <motion.div
                  layoutId="nav-indicator"
                  className="absolute inset-0 rounded-lg bg-emerald-500/10 border border-emerald-500/20"
                  transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                />
              )}
              <Icon className={cn('w-4 h-4 relative z-10', isActive && 'text-emerald-400')} />
              <span className="relative z-10">{label}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400 relative z-10" />
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-800">
        <p className="text-slate-600 text-xs text-center">
          Saving the planet,<br />one cache hit at a time 🌱
        </p>
      </div>
    </aside>
  )
}
