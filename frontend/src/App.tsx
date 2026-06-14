import { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Sidebar } from './components/layout/Sidebar'
import { TopBar } from './components/layout/TopBar'
import { QueryPage } from './pages/QueryPage'
import { StatsPage } from './pages/StatsPage'
import { ImpactPage } from './pages/ImpactPage'
import { SettingsPage } from './pages/SettingsPage'
import { ToastProvider } from './components/ui/Toast'
import type { NavView, AppSettings } from './types/api'
import { setBaseUrl } from './services/api'

const qc = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10_000,
      retry: 2,
    },
  },
})

const DEFAULT_SETTINGS: AppSettings = {
  apiBaseUrl: 'http://localhost:8000',
  similarityThreshold: 0.9,
  darkMode: true,
  autoRefreshImpact: true,
}

function AppInner() {
  const [view, setView] = useState<NavView>('query')
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS)

  // Apply dark mode
  useEffect(() => {
    if (settings.darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [settings.darkMode])

  // Sync API base url
  useEffect(() => {
    setBaseUrl(settings.apiBaseUrl)
  }, [settings.apiBaseUrl])

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900 font-sans overflow-hidden">
      <Sidebar active={view} onChange={setView} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">
          {view === 'query' && <QueryPage />}
          {view === 'stats' && <StatsPage />}
          {view === 'impact' && (
            <ImpactPage settings={settings} onSettingsChange={setSettings} />
          )}
          {view === 'settings' && (
            <SettingsPage settings={settings} onSettingsChange={setSettings} />
          )}
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <ToastProvider>
        <AppInner />
      </ToastProvider>
    </QueryClientProvider>
  )
}
