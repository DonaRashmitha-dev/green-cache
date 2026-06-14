import { useEffect, useState } from "react"
import { getImpact } from "../services/api"
import type { ImpactResponse } from "../types/api"

export function ImpactPage() {
  const [data, setData] = useState<ImpactResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const result = await getImpact()
        setData(result)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetch()
    const interval = setInterval(fetch, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="p-8 text-slate-400">Loading impact data...</div>

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Environmental Impact</h1>
      <p className="text-slate-500 dark:text-slate-400 mb-8">Every cache hit saves real energy and water.</p>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="text-4xl mb-2">💧</div>
          <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            {data?.total_water_saved_liters?.toFixed(6) ?? "0"} L
          </div>
          <div className="text-sm text-slate-500 mt-1">Water Saved</div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="text-4xl mb-2">⚡</div>
          <div className="text-3xl font-bold text-yellow-500">
            {data?.total_energy_saved_wh?.toFixed(4) ?? "0"} Wh
          </div>
          <div className="text-sm text-slate-500 mt-1">Energy Saved</div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="text-4xl mb-2">🌱</div>
          <div className="text-3xl font-bold text-green-500">
            {data?.equivalent_trees?.toFixed(6) ?? "0"}
          </div>
          <div className="text-sm text-slate-500 mt-1">Equivalent Trees</div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="text-4xl mb-2">🚗</div>
          <div className="text-3xl font-bold text-blue-500">
            {data?.equivalent_cars_km?.toFixed(4) ?? "0"} km
          </div>
          <div className="text-sm text-slate-500 mt-1">Car KM Avoided</div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700">
        <h2 className="font-semibold text-slate-700 dark:text-slate-300 mb-4">Summary</h2>
        <div className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
          <div className="flex justify-between"><span>Total Queries</span><span className="font-mono">{data?.total_queries ?? 0}</span></div>
          <div className="flex justify-between"><span>Cache Hit Rate</span><span className="font-mono">{((data?.cache_hit_rate ?? 0) * 100).toFixed(1)}%</span></div>
          <div className="flex justify-between"><span>Tokens Saved</span><span className="font-mono">{data?.total_tokens_saved ?? 0}</span></div>
          <div className="flex justify-between"><span>Water Saved (ml)</span><span className="font-mono">{data?.total_water_saved_ml?.toFixed(4) ?? "0"}</span></div>
        </div>
      </div>
    </div>
  )
}
