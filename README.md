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

## Roadmap

- [ ] Base structure and styling
- [ ] First microcard components
- [ ] Data scrapers (LinkedIn, Exercism, Udemy, RSS)
- [ ] HTMX interactions and filters
- [ ] Cache system
- [ ] NPM deployment config

## Philosophy

> Zen capibara approach - calm, professional, with touches of playful originality. Building incrementally, one microcard at a time.
