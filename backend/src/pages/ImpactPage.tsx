import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Droplets, Zap, TreePine, Car, RefreshCw, Download } from 'lucide-react'
import { useImpact } from '../../hooks/useImpact'

function formatWater(valueLiters: number): string {
  if (valueLiters >= 1) {
    return `${valueLiters.toFixed(2)} L`
  } else if (valueLiters >= 0.001) {
    return `${(valueLiters * 1000).toFixed(1)} ml`
  } else if (valueLiters > 0) {
    return `${(valueLiters * 1000).toFixed(2)} ml`
  }
  return '0.00 ml'
}

function formatEnergy(valueWh: number): string {
  if (valueWh >= 1000) {
    return `${(valueWh / 1000).toFixed(2)} kWh`
  }
  return `${valueWh.toFixed(2)} Wh`
}

function formatNumber(value: number, decimals: number = 1): string {
  if (value >= 1000000) return `${(value / 1000000).toFixed(decimals)}M`
  if (value >= 1000) return `${(value / 1000).toFixed(decimals)}k`
  return value.toFixed(decimals)
}

export function ImpactPage() {
  const { data: impact, isLoading, refetch } = useImpact(true)
  const [isLive, setIsLive] = useState(true)

  useEffect(() => {
    if (!isLive) return
    const interval = setInterval(() => refetch(), 5000)
    return () => clearInterval(interval)
  }, [isLive, refetch])

  const handleExport = () => {
    if (!impact) return
    const data = { timestamp: new Date().toISOString(), ...impact }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `green-cache-impact-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (isLoading || !impact) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Environmental Impact</h1>
            <p className="text-slate-400">Real savings from semantic caching</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse bg-slate-800/50 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  const waterDisplay = formatWater(impact.total_water_saved_liters)
  const energyDisplay = formatEnergy(impact.total_energy_saved_wh)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Environmental Impact</h1>
          <p className="text-slate-400">Real savings from semantic caching</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setIsLive(!isLive)} className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${isLive ? 'text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20' : 'text-slate-400 bg-slate-800 hover:bg-slate-700'}`}>
            <span className="relative flex h-2 w-2 mr-2 inline-block align-middle">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isLive ? 'bg-emerald-400' : 'bg-slate-400'}`} />
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isLive ? 'bg-emerald-400' : 'bg-slate-400'}`} />
            </span>
            {isLive ? 'Live' : 'Paused'}
          </button>
          <button onClick={() => refetch()} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button onClick={handleExport} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-900/40 via-slate-900 to-slate-900 border border-emerald-500/20 p-8">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(16,185,129,0.15),transparent_50%)]" />
        <div className="relative text-center">
          <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ duration: 4, repeat: Infinity }} className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-500/10 border border-emerald-500/30 mb-4">
            <Droplets className="w-10 h-10 text-emerald-400" />
          </motion.div>
          <p className="text-emerald-400/80 text-sm font-medium uppercase tracking-wider mb-2">Total Water Saved</p>
          <div className="text-6xl font-bold text-white mb-2">{waterDisplay}</div>
          <p className="text-slate-400 text-sm">{impact.total_water_saved_liters > 0 ? `That is ${waterDisplay} of clean water preserved` : 'Start caching to save water'}</p>
          <p className="text-slate-500 text-xs mt-2">Updated {new Date().toLocaleTimeString()}</p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <div className="p-6 rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-900/20 to-slate-900">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                <Droplets className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{waterDisplay}</div>
            <p className="text-slate-400 text-sm">Water Saved</p>
            <p className="text-cyan-400/60 text-xs mt-2">{impact.total_water_saved_ml.toFixed(2)} ml total</p>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <div className="p-6 rounded-xl border border-amber-500/20 bg-gradient-to-br from-amber-900/20 to-slate-900">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Zap className="w-5 h-5 text-amber-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{energyDisplay}</div>
            <p className="text-slate-400 text-sm">Energy Saved</p>
            <p className="text-amber-400/60 text-xs mt-2">{impact.total_energy_saved_wh.toFixed(4)} Wh total</p>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <div className="p-6 rounded-xl border border-emerald-500/20 bg-gradient-to-br from-emerald-900/20 to-slate-900">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <TreePine className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{impact.equivalent_trees.toFixed(2)}</div>
            <p className="text-slate-400 text-sm">trees</p>
            <p className="text-emerald-400/60 text-xs mt-2">Carbon Offset</p>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <div className="p-6 rounded-xl border border-purple-500/20 bg-gradient-to-br from-purple-900/20 to-slate-900">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <Car className="w-5 h-5 text-purple-400" />
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{impact.equivalent_cars_km.toFixed(1)}</div>
            <p className="text-slate-400 text-sm">km</p>
            <p className="text-purple-400/60 text-xs mt-2">Car KM Avoided</p>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-center">
          <div className="text-2xl font-bold text-white">{impact.total_queries}</div>
          <p className="text-slate-400 text-xs">Total Queries</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-center">
          <div className="text-2xl font-bold text-emerald-400">{(impact.cache_hit_rate * 100).toFixed(1)}%</div>
          <p className="text-slate-400 text-xs">Cache Hit Rate</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-center">
          <div className="text-2xl font-bold text-white">{formatNumber(impact.total_tokens_saved)}</div>
          <p className="text-slate-400 text-xs">Tokens Saved</p>
        </div>
      </div>

      <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">Impact Estimation Methodology</h3>
        <p className="text-slate-400 text-sm mb-4">How we calculate environmental savings</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-slate-900/50">
              <div className="flex items-center gap-2 text-cyan-400 mb-1">
                <Droplets className="w-4 h-4" />
                <span className="font-medium">Water per token</span>
              </div>
              <p className="text-slate-400">0.0015 ml / token</p>
              <p className="text-slate-500 text-xs">Based on Google/Microsoft datacenter PUE studies (2023)</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/50">
              <div className="flex items-center gap-2 text-emerald-400 mb-1">
                <TreePine className="w-4 h-4" />
                <span className="font-medium">Carbon to trees</span>
              </div>
              <p className="text-slate-400">0.021 kg CO₂ / Wh → 21.7 kg/tree/yr</p>
              <p className="text-slate-500 text-xs">IPCC carbon factor + average tree sequestration</p>
            </div>
          </div>
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-slate-900/50">
              <div className="flex items-center gap-2 text-amber-400 mb-1">
                <Zap className="w-4 h-4" />
                <span className="font-medium">Energy per token</span>
              </div>
              <p className="text-slate-400">0.0005 Wh / token</p>
              <p className="text-slate-500 text-xs">Average GPU inference efficiency (A100, H100 mix)</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/50">
              <div className="flex items-center gap-2 text-purple-400 mb-1">
                <Car className="w-4 h-4" />
                <span className="font-medium">Energy to car km</span>
              </div>
              <p className="text-slate-400">0.19 kWh / km (avg EV)</p>
              <p className="text-slate-500 text-xs">IEA EV efficiency benchmark 2022</p>
            </div>
          </div>
        </div>
        <p className="text-slate-500 text-xs mt-4 italic">Estimates are illustrative. Real-world values vary by datacenter, model size, and workload.</p>
      </div>
    </div>
  )
}