# KapiHome 🦫

Personal homepage with zen capibara style - aggregating my digital presence through elegant microcard components.

## Philosophy

Building a calm, professional digital space that aggregates data from various sources. No CV, no resume - just microcard snapshots of interests, learning, and activities.

## Stack

- **Backend** - FastAPI (Python)
- **Frontend** - Bun + Handlebars + HTMX
- **Styling** - Material 3 + Neobrutalism hybrid
- **Data** - JSON files with caching
- **Scrapers** - Dockerized containers
- **Orchestration** - Docker Compose + Taskfile

## Project Structure

```
kapihome/
├── backend/          # FastAPI API server
│   ├── app/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # Bun + Handlebars UI
│   ├── src/
│   │   ├── templates/
│   │   ├── static/
│   │   └── server.ts
│   ├── Dockerfile
│   └── package.json
├── scrapers/         # Data collection containers
├── data/             # JSON data storage (gitignored)
├── doc/              # API and data documentation
├── AI/               # AI documents (gitignored)
├── docker-compose.yml
└── Taskfile.yml
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Task (taskfile)

### Configuration

1. **Copy environment file:**
```bash
cp .env.example .env
```

2. **Configure Remember The Milk API:**
   - Get your API key from: https://www.rememberthemilk.com/services/api/
   - Edit `.env` and add your credentials:
   ```
   RTM_API_KEY=your_actual_api_key
   RTM_API_SECRET=your_actual_secret
   ```
   - ⚠️ **IMPORTANTE**: Il file `.env` è in `.gitignore` e NON verrà mai committato su GitHub

### Development

```bash
# Start development environment
task dev

# View logs
task logs

# Stop services
task stop

# Clean everything
task clean
```

### Access

- Frontend -> http://localhost:3000
- Backend API -> http://localhost:8000
- API Docs -> http://localhost:8000/docs

## Deployment

Designed to be served via Nginx Proxy Manager (NPM). Internal services use HTTP, NPM handles HTTPS termination.

## Data Collection System

KapiHome includes an automated scraper service that:
- ✅ Collects data from RTM (Remember The Milk) every 10 minutes
- ✅ Automatically caches data from `data_tmp/` to `data/`
- ✅ Stores historical data in SQLite for analytics
- 🔄 Planned: LinkedIn, GitHub, Exercism, Udemy scrapers

See [scrapers/README.md](scrapers/README.md) for detailed documentation.

### Quick Start with Scrapers

```bash
# Setup RTM authentication (first time)
task setup-rtm

# Start scraper service (every 10 min)
task scrape-start

# View scraper logs
task logs-scrapers
```

## Roadmap

- [x] Base structure and styling
- [x] First microcard components  
- [x] RTM scraper with auto-caching
- [x] Historical database (SQLite)
- [x] Cache management system
- [ ] LinkedIn, GitHub, Exercism, Udemy scrapers
- [ ] Analytics dashboard with charts
- [ ] HTMX interactions and filters
- [ ] NPM deployment config

## Philosophy

> Zen capibara approach - calm, professional, with touches of playful originality. Building incrementally, one microcard at a time.
