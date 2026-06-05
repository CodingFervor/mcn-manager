# MCN Manager — Frontend

Vue 3 single-page application for the MCN Manager live-commerce operations platform.

For the full project overview, backend setup, and architecture details, see the [main project README](../docs/README.md).

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Vue 3 (Composition API, `<script setup>`) |
| Build Tool | Vite |
| UI Library | Element Plus |
| Charts | ECharts |
| State Management | Pinia |
| Routing | Vue Router |
| HTTP Client | Axios (via `src/api.js`) |

---

## Getting Started

### Prerequisites

- Node.js 16+
- npm 8+

### Install & Run

```bash
# Install dependencies
npm install

# Start development server (http://127.0.0.1:5173)
npm run dev

# Production build (output to dist/)
npm run build
```

The dev server proxies API requests to the Django backend at `http://127.0.0.1:8000` (configured in `vite.config.js`).

---

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── api.js           # Axios instance & API helpers
│   ├── App.vue          # Root component
│   ├── main.js          # App entry point
│   ├── echarts.js       # ECharts global configuration
│   ├── style.css        # Global styles
│   ├── assets/          # Images, icons, fonts
│   ├── components/      # Reusable UI components
│   ├── composables/     # Shared composables (hooks)
│   ├── router/          # Vue Router configuration
│   ├── stores/          # Pinia stores
│   └── views/           # Page-level components (60 pages)
├── index.html           # HTML entry point
├── vite.config.js       # Vite configuration (proxy, aliases)
└── package.json         # Dependencies & scripts
```

---

## Design System

The UI follows a **dark neon** theme:

- **Background**: Deep dark tones (#0a0a1a, #1a1a2e)
- **Accent Colors**: Neon cyan (#00d4ff) and electric blue highlights
- **Cards**: Translucent dark panels with subtle borders
- **Typography**: Clean sans-serif with high-contrast foreground text
- **Data Visualization**: ECharts with matching dark neon color palette

Global styles are defined in `src/style.css`. All pages share a consistent layout with a collapsible sidebar, top navigation bar, and content area.

---

## Pages

The application includes 60 frontend pages covering:

- **Dashboard** — Real-time analytics with charts and KPI widgets
- **Store Management** — Multi-platform store CRUD
- **Personnel** — Streamer, operator, and staff management
- **Scheduling** — Shift planning with conflict detection
- **Attendance** — Clock-in/out with late-arrival flags
- **Performance** — GMV tracking, conversion rates, order stats
- **AI Center** — GMV forecasting, anomaly detection, smart matching
- **Finance** — Income, expenses, commissions, contracts
- **Tasks** — Kanban-style task board
- **Products** — Product catalog with stock alerts
- **Marketing** — Campaign management
- **Competitor** — Monitoring and follower analysis
- **Training & Goals** — Staff development tracking
- **Settings** — Roles, permissions, audit logs

---

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server with hot reload |
| `npm run build` | Build for production (outputs to `dist/`) |
| `npm run preview` | Preview the production build locally |

---

## Related Documentation

- [System Architecture](../docs/architecture.md)
- [API Reference](../docs/api.md)
- [AI Engine Details](../docs/ai-engine.md)
- [Frontend Page Catalog](../docs/frontend.md)
