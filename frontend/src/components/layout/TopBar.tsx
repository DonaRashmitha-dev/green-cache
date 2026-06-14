import { RefreshCw } from 'lucide-react'
import { useHealth } from '../../hooks/useHealth'
import { cn } from '../../utils/helpers'

export function TopBar() {
  const { data: health, isError, isFetching } = useHealth()

  const isHealthy = !isError && health?.status === 'healthy'

  return (
    <header className="h-14 shrink-0 flex items-center justify-between px-6 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
      {/* Left: empty for now, can add breadcrumbs */}
      <div />

      {/* Right: status indicators */}
      <div className="flex items-center gap-3">
        {isFetching && (
          <RefreshCw className="w-3.5 h-3.5 text-slate-400 animate-spin" />
        )}

        {health?.backend && (
          <span className="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-medium border border-slate-200 dark:border-slate-700">
            {health.backend}
          </span>
        )}

        <div className="flex items-center gap-1.5">
          <div className={cn(
            'w-2 h-2 rounded-full',
            isHealthy ? 'bg-emerald-400 shadow-[0_0_6px_#34d399]' : 'bg-red-400'
          )} />
          <span className={cn(
            'text-xs font-medium',
            isHealthy ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500'
          )}>
            {isHealthy ? 'Connected' : 'Offline'}
          </span>
        </div>
      </div>
    </header>
  )
}
