import { useState, useEffect, useRef, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Copy, Check, Zap, Droplets, Clock, Sparkles } from 'lucide-react'
import { postQuery } from '../services/api'
import type { QualityTier, QueryHistoryItem, QueryResponse } from '../types/api'
import { useToast } from '../components/ui/Toast'
import { cn, fmtLatency, fmtWater, fmtNumber, relativeTime } from '../utils/helpers'

const EXAMPLES = [
  { label: 'What is Python?', lang: 'en' },
  { label: 'ఫ్రాన్స్ రాజధాని ఏమిటి?', lang: 'te' },
  { label: 'फ्रांस की राजधानी क्या है?', lang: 'hi' },
]

const TIERS: { value: QualityTier; label: string; desc: string }[] = [
  { value: 'brief', label: 'Brief', desc: 'Fast, concise' },
  { value: 'standard', label: 'Standard', desc: 'Balanced' },
  { value: 'detailed', label: 'Detailed', desc: 'Thorough' },
]

function TypewriterText({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState('')
  const idx = useRef(0)

  useEffect(() => {
    setDisplayed('')
    idx.current = 0
    const interval = setInterval(() => {
      if (idx.current < text.length) {
        setDisplayed(text.slice(0, idx.current + 1))
        idx.current++
      } else {
        clearInterval(interval)
      }
    }, 12)
    return () => clearInterval(interval)
  }, [text])

  return <span>{displayed}<span className="animate-pulse text-emerald-400">▌</span></span>
}

function ResponseCard({ result }: { result: QueryResponse }) {
  const [copied, setCopied] = useState(false)
  const [isTyping, setIsTyping] = useState(true)

  useEffect(() => {
    const t = setTimeout(() => setIsTyping(false), result.response.length * 12 + 300)
    return () => clearTimeout(t)
  }, [result.response])

  const copy = () => {
    navigator.clipboard.writeText(result.response)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const score = result.similarity_score ?? 0
  const scoreColor =
    score > 0.9 ? 'bg-emerald-500' : score > 0.7 ? 'bg-yellow-500' : 'bg-slate-400'

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-hidden"
    >
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60">
        <div className="flex items-center gap-2">
          <span className={cn(
            'px-2 py-0.5 rounded-full text-xs font-bold tracking-wider',
            result.cache_hit
              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
              : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
          )}>
            {result.cache_hit ? '⚡ CACHE HIT' : '● CACHE MISS'}
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            {result.quality_tier} · {result.language}
          </span>
        </div>
        <button
          onClick={copy}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>

      {/* Response text */}
      <div className="p-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed whitespace-pre-wrap min-h-[80px]">
        {isTyping ? <TypewriterText text={result.response} /> : result.response}
      </div>

      {/* Similarity score */}
      {result.similarity_score != null && (
        <div className="px-4 pb-3 space-y-1">
          <div className="flex justify-between text-xs text-slate-500">
            <span>Similarity score</span>
            <span className="font-medium">{result.similarity_score.toFixed(3)}</span>
          </div>
          <div className="h-1.5 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${result.similarity_score * 100}%` }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className={cn('h-full rounded-full', scoreColor)}
            />
          </div>
        </div>
      )}

      {/* Metrics row */}
      <div className="grid grid-cols-4 gap-px bg-slate-100 dark:bg-slate-700 border-t border-slate-100 dark:border-slate-700">
        {[
          { icon: Clock, label: 'Latency', value: fmtLatency(result.latency_ms) },
          { icon: Sparkles, label: 'Tokens saved', value: fmtNumber(result.tokens_saved) },
          { icon: Droplets, label: 'Water', value: fmtWater(result.water_saved_ml) },
          { icon: Zap, label: 'Energy', value: `${result.energy_saved_wh.toFixed(4)}Wh` },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label} className="bg-white dark:bg-slate-800 px-3 py-2.5 text-center">
            <Icon className="w-3.5 h-3.5 text-slate-400 mx-auto mb-1" />
            <div className="text-xs font-semibold text-slate-700 dark:text-slate-200">{value}</div>
            <div className="text-xs text-slate-400">{label}</div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

function HistoryItem({ item }: { item: QueryHistoryItem }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-lg transition-colors">
      <div className={cn(
        'w-2 h-2 rounded-full shrink-0',
        item.cache_hit ? 'bg-emerald-400' : 'bg-slate-300 dark:bg-slate-600'
      )} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-700 dark:text-slate-200 truncate">{item.query}</p>
        <p className="text-xs text-slate-400">{relativeTime(item.timestamp)} · {fmtLatency(item.latency_ms)}</p>
      </div>
      <span className={cn(
        'text-xs font-medium px-1.5 py-0.5 rounded shrink-0',
        item.cache_hit
          ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20'
          : 'text-slate-500 bg-slate-100 dark:bg-slate-700'
      )}>
        {item.cache_hit ? 'HIT' : 'MISS'}
      </span>
    </div>
  )
}

export function QueryPage() {
  const { toast } = useToast()
  const [query, setQuery] = useState('')
  const [tier, setTier] = useState<QualityTier>('standard')
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [history, setHistory] = useState<QueryHistoryItem[]>([])
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const mutation = useMutation({
    mutationFn: postQuery,
    onSuccess: (data) => {
      setResult(data)
      const item: QueryHistoryItem = {
        id: Math.random().toString(36).slice(2),
        query: data.query,
        cache_hit: data.cache_hit,
        latency_ms: data.latency_ms,
        timestamp: Date.now(),
        response: data.response,
        tokens_saved: data.tokens_saved,
        water_saved_ml: data.water_saved_ml,
        energy_saved_wh: data.energy_saved_wh,
        similarity_score: data.similarity_score,
      }
      setHistory((prev) => [item, ...prev].slice(0, 10))
    },
    onError: (err: Error) => {
      toast('error', err.message || 'Query failed')
    },
  })

  const send = useCallback(() => {
    const q = query.trim()
    if (!q || mutation.isPending) return
    mutation.mutate({ query: q, quality_tier: tier })
  }, [query, tier, mutation])

  // Ctrl+Enter shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') send()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [send])

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Query</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Semantic cache checks similar past queries before hitting the LLM
        </p>
      </div>

      {/* Input card */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4 space-y-3">
        {/* Tier selector */}
        <div className="flex gap-2">
          {TIERS.map(({ value, label, desc }) => (
            <button
              key={value}
              onClick={() => setTier(value)}
              className={cn(
                'flex-1 py-1.5 rounded-lg text-xs font-medium border transition-all',
                tier === value
                  ? 'bg-emerald-500 border-emerald-500 text-white'
                  : 'border-slate-200 dark:border-slate-600 text-slate-500 dark:text-slate-400 hover:border-emerald-300 dark:hover:border-emerald-700'
              )}
            >
              {label}
              <span className="hidden sm:inline text-opacity-80"> · {desc}</span>
            </button>
          ))}
        </div>

        {/* Textarea */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything… language auto-detected"
            rows={3}
            className="w-full resize-none rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-900 px-3 py-2.5 text-sm text-slate-800 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/40 focus:border-emerald-400 transition"
          />
          <div className="absolute bottom-2 right-2 text-xs text-slate-300 dark:text-slate-600">
            Ctrl+Enter
          </div>
        </div>

        {/* Examples */}
        <div className="flex flex-wrap gap-1.5">
          {EXAMPLES.map(({ label }) => (
            <button
              key={label}
              onClick={() => setQuery(label)}
              className="px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-600 text-xs text-slate-500 dark:text-slate-400 hover:border-emerald-300 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
            >
              {label}
            </button>
          ))}
        </div>

        {/* Send button */}
        <button
          onClick={send}
          disabled={!query.trim() || mutation.isPending}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors"
        >
          {mutation.isPending ? (
            <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Querying…</>
          ) : (
            <><Send className="w-4 h-4" /> Send Query</>
          )}
        </button>
      </div>

      {/* Result */}
      <AnimatePresence mode="wait">
        {result && <ResponseCard key={result.query + result.latency_ms} result={result} />}
      </AnimatePresence>

      {/* History */}
      {history.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-hidden"
        >
          <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
            <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              Query History
            </h2>
          </div>
          <div className="divide-y divide-slate-50 dark:divide-slate-700/50 px-1 py-1">
            {history.map((item) => (
              <HistoryItem key={item.id} item={item} />
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
