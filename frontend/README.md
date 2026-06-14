# Green Cache Dashboard

A production-ready React + TypeScript + Tailwind CSS dashboard for the Green Cache semantic LLM caching system.

## Prerequisites

- Node.js 18+
- Green Cache backend running at `http://localhost:8000`

## Quick Start

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Stack

- **React 18** + **TypeScript** — strict mode, no `any`
- **Vite** — fast HMR dev server, proxies `/api` to backend
- **Tailwind CSS** — dark mode via `class` strategy
- **TanStack Query** — data fetching, caching, retry logic
- **Recharts** — charts (hit rate gauge, latency bar, line chart)
- **Framer Motion** — card entrances, confirm dialog animations
- **Lucide React** — icons

## Features

### Query View
- Quality tier selector: Brief / Standard / Detailed
- Typewriter effect on responses
- Cache HIT/MISS badge with similarity score progress bar
- 4-metric row: latency, tokens, water, energy
- Query history (last 10)
- Example queries including Telugu + Hindi
- `Ctrl+Enter` to send

### Stats View
- 4 metric cards with animated counters
- Hit rate radial gauge
- Latency comparison bar chart (hit vs miss)
- Cache entries over time line chart
- Clear cache with confirmation dialog

### Impact View
- Hero water counter with ripple animation
- 4 environmental metric cards (water, energy, trees, car km)
- Contextualisation: "enough water for X people"
- Auto-refresh toggle (polls every 5s)
- Export impact report as JSON
- Expandable methodology section

### Settings View
- API base URL (persisted, proxied)
- Similarity threshold slider (0.80–0.99)
- Light / Dark mode toggle
- Backend info (read-only from health endpoint)

## Project Structure

```
src/
├── types/api.ts        — all TypeScript interfaces
├── services/api.ts     — fetch wrappers
├── hooks/              — React Query hooks
├── utils/helpers.ts    — cn(), formatters
├── components/
│   ├── layout/         — Sidebar, TopBar
│   └── ui/             — AnimatedNumber, Skeleton, Toast
└── pages/              — QueryPage, StatsPage, ImpactPage, SettingsPage
```

## Build for Production

```bash
npm run build
npm run preview
```
