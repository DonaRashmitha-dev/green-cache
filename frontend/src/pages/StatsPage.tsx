import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  LineChart,
  Line,
  Legend,
} from 'recharts'
import { Database, TrendingUp, TrendingDown, Trash2, X, AlertTriangle } from 'lucide-react'
import { useStats, useClearCache } from '../hooks/useStats'
import { useToast } from '../components/ui/Toast'
import { SkeletonCard } from '../components/ui/Skeleton'
import { AnimatedNumber } from '../components/ui/AnimatedNumber'
import { cn, fmtPct, fmtNumber } from '../utils/helpers'

// Mock historical data for line chart
const MOCK_HISTORY = Array.from({ length: 12 }, (_, i) => ({
  time: `${i * 5}m`,
  entries: Math.floor(20 + i * 3.5 + Math.random() * 8),
  hits: Math.floor(5 + i * 2.2 + Math.random() * 5),
}))

function MetricCard({
  label,
  value,
  sub,
  icon: Icon,
  color,
}: {
  label: string
  value: number
  sub?: string
  icon: React.ElementType
  color: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">{label}</p>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            <AnimatedNumber value={value} decimals={label.includes('Rate') ? 1 : 0} />
            {label.includes('Rate') && <span className="text-xl">%</span>}
          </div>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <div className={cn('p-2.5 rounded-lg', color)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </motion.div>
  )
}

function ConfirmDialog({ onConfirm, onCancel, loading }: { onConfirm: () => void; onCancel: () => void; loading: boolean }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onCancel} />
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-6 w-full max-w-sm mx-4 border border-slate-200 dark:border-slate-700"
      >
        <button onClick={onCancel} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600">
          <X className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-full bg-red-100 dark:bg-red-900/30">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
          </div>
          <h3 className="font-semibold text-slate-900 dark:text-white">Clear all cache?</h3>
        </div>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-5">
          This permanently removes all cached entries. Cache misses will spike until entries rebuild.
        </p>
        <div className="flex gap-2">
          <button
            onClick={onCancel}
            className="flex-1 py-2 rounded-lg border border-slate-200 dark:border-slate-600 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 py-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-medium transition-colors"
          >
            {loading ? 'Clearing…' : 'Clear cache'}
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export function StatsPage() {
  const { data: stats, isLoading, error } = useStats()
  const clearMut = useClearCache()
  const { toast } = useToast()
  const [showConfirm, setShowConfirm] = useState(false)

  const handleClear = async () => {
    try {
      await clearMut.mutateAsync()
      toast('success', 'Cache cleared')
      setShowConfirm(false)
    } catch (e) {
      toast('error', (e as Error).message)
    }
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        Failed to load stats: {(error as Error).message}
      </div>
    )
  }

  const hitRatePct = stats ? stats.hit_rate * 100 : 0
  const gaugeData = [
    { name: 'Hit Rate', value: hitRatePct, fill: '#10b981' },
    { name: 'Miss Rate', value: 100 - hitRatePct, fill: '#e2e8f0' },
  ]

  const latencyData = [
    { name: 'Cache Hit', latency: 12, fill: '#10b981' },
    { name: 'Cache Miss', latency: 340, fill: '#64748b' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Stats</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Cache performance metrics
          </p>
        </div>
        <button
          onClick={() => setShowConfirm(true)}
          className="flex items-center gap-2 px-3 py-2 rounded-lg border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm font-medium hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Clear Cache
        </button>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <MetricCard
              label="Total Requests"
              value={stats?.total_requests ?? 0}
              icon={Database}
              color="bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
              sub="all time"
            />
            <MetricCard
              label="Cache Hits"
              value={stats?.cache_hits ?? 0}
              icon={TrendingUp}
              color="bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400"
            />
            <MetricCard
              label="Cache Misses"
              value={stats?.cache_misses ?? 0}
              icon={TrendingDown}
              color="bg-slate-100 dark:bg-slate-700 text-slate-500"
            />
            <MetricCard
              label="Hit Rate"
              value={hitRatePct}
              icon={TrendingUp}
              color="bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400"
              sub={`${fmtNumber(stats?.total_tokens_saved ?? 0)} tokens saved`}
            />
          </>
        )}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Hit rate gauge */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-3">Hit Rate</h3>
          <div className="relative h-36">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                cx="50%"
                cy="100%"
                innerRadius="60%"
                outerRadius="100%"
                startAngle={180}
                endAngle={0}
                data={gaugeData}
              >
                <RadialBar dataKey="value" cornerRadius={4} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute inset-x-0 bottom-0 text-center">
              <div className="text-2xl font-bold text-emerald-500">
                {fmtPct(stats?.hit_rate ?? 0)}
              </div>
              <div className="text-xs text-slate-400">hit rate</div>
            </div>
          </div>
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>0%</span>
            <span>{stats?.entries_count ?? 0} entries</span>
            <span>100%</span>
          </div>
        </div>

        {/* Latency comparison */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-3">
            Latency Comparison
          </h3>
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={latencyData} margin={{ top: 4, right: 8, bottom: 4, left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f020" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} unit="ms" />
              <Tooltip
                contentStyle={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: 8,
                  color: '#f1f5f9',
                  fontSize: 12,
                }}
              />
              <Bar dataKey="latency" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-slate-400 text-center">
            ~28× faster with cache
          </p>
        </div>

        {/* Cache entries over time */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-3">
            Entries Over Time
          </h3>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={MOCK_HISTORY} margin={{ top: 4, right: 8, bottom: 4, left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f020" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
              <Tooltip
                contentStyle={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: 8,
                  color: '#f1f5f9',
                  fontSize: 12,
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              <Line type="monotone" dataKey="entries" stroke="#10b981" strokeWidth={2} dot={false} name="Entries" />
              <Line type="monotone" dataKey="hits" stroke="#34d399" strokeWidth={1.5} dot={false} strokeDasharray="4 2" name="Hits" />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-xs text-slate-400 text-center mt-1">Simulated — connect backend for live data</p>
        </div>
      </div>

      <AnimatePresence>
        {showConfirm && (
          <ConfirmDialog
            onConfirm={handleClear}
            onCancel={() => setShowConfirm(false)}
            loading={clearMut.isPending}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
