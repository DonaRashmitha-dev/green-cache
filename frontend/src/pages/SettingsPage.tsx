import { useState } from 'react'
import { useHealth } from '../hooks/useHealth'
import type { AppSettings } from '../types/api'
import { setBaseUrl } from '../services/api'
import { useToast } from '../components/ui/Toast'
import { cn } from '../utils/helpers'
import { Moon, Sun, Save } from 'lucide-react'

interface Props {
  settings: AppSettings
  onSettingsChange: (s: AppSettings) => void
}

export function SettingsPage({ settings, onSettingsChange }: Props) {
  const { data: health } = useHealth()
  const { toast } = useToast()
  const [localUrl, setLocalUrl] = useState(settings.apiBaseUrl)
  const [localThreshold, setLocalThreshold] = useState(settings.similarityThreshold)

  const save = () => {
    setBaseUrl(localUrl)
    onSettingsChange({
      ...settings,
      apiBaseUrl: localUrl,
      similarityThreshold: localThreshold,
    })
    toast('success', 'Settings saved')
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Configure dashboard preferences
        </p>
      </div>

      {/* Backend info */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 divide-y divide-slate-100 dark:divide-slate-700">
        <div className="px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4">Backend</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
                Cache Backend
              </label>
              <div className="flex items-center gap-2">
                <div className="flex-1 px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-900 text-sm text-slate-600 dark:text-slate-300 font-mono border border-slate-200 dark:border-slate-700">
                  {health?.backend ?? '—'}
                </div>
                <span className="text-xs text-slate-400 italic">read-only</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
                API Base URL
              </label>
              <input
                type="text"
                value={localUrl}
                onChange={(e) => setLocalUrl(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-sm text-slate-700 dark:text-slate-200 font-mono focus:outline-none focus:ring-2 focus:ring-emerald-400/40 focus:border-emerald-400 transition"
                placeholder="http://localhost:8000"
              />
            </div>
          </div>
        </div>

        {/* Similarity threshold */}
        <div className="px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4">Cache</h2>
          <div>
            <div className="flex justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-500 dark:text-slate-400">
                Similarity Threshold
              </label>
              <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400">
                {localThreshold.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min={0.80}
              max={0.99}
              step={0.01}
              value={localThreshold}
              onChange={(e) => setLocalThreshold(parseFloat(e.target.value))}
              className="w-full h-2 appearance-none rounded-full bg-slate-200 dark:bg-slate-700 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-emerald-500 [&::-webkit-slider-thumb]:cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>0.80 (loose)</span>
              <span>0.99 (strict)</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Higher = more precise matching, fewer cache hits. Lower = broader matches, more hits.
            </p>
          </div>
        </div>

        {/* Appearance */}
        <div className="px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4">Appearance</h2>
          <div>
            <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">
              Theme
            </label>
            <div className="flex gap-2">
              {[
                { value: false, icon: Sun, label: 'Light' },
                { value: true, icon: Moon, label: 'Dark' },
              ].map(({ value, icon: Icon, label }) => (
                <button
                  key={label}
                  onClick={() => onSettingsChange({ ...settings, darkMode: value })}
                  className={cn(
                    'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg border text-sm font-medium transition-all',
                    settings.darkMode === value
                      ? 'bg-emerald-500 border-emerald-500 text-white'
                      : 'border-slate-200 dark:border-slate-600 text-slate-500 dark:text-slate-400 hover:border-emerald-300'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Save */}
      <button
        onClick={save}
        className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm transition-colors"
      >
        <Save className="w-4 h-4" />
        Save Settings
      </button>

      {/* Info */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-4">
        <p className="text-xs text-slate-400 text-center">
          Green Cache — Multilingual semantic cache for LLMs.<br />
          Reducing AI's environmental footprint, one query at a time.
        </p>
      </div>
    </div>
  )
}
