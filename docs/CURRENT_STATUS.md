# KapiHome - Current Status

**Last Updated**: 2026-01-04  
**Version**: 0.5.0  
**Status**: ✅ Production Ready (with known issues)

---

## 🎯 Project Overview

KapiHome is a personal dashboard aggregating data from multiple platforms (LinkedIn, GitHub, Exercism, Udemy, RTM, Welltory) into a unified, elegant interface. Built with FastAPI backend, Bun frontend, and Handlebars templates.

**Philosophy**: Zen Capibara - Calm, professional, with playful touches.  
**Design**: Flat Material 3 with fluorescent accents (OKLCH color space).

---

## ✅ Completed Features

### Core Infrastructure
- ✅ FastAPI backend with async support
- ✅ Bun frontend with Handlebars templates
- ✅ Docker Compose orchestration
- ✅ Dual theme system (Light/Dark with OKLCH)
- ✅ Responsive grid layout (12-column)
- ✅ HTMX for dynamic content loading
- ✅ Taskfile for development commands

### Data Sources Integration

#### LinkedIn
- ✅ Tampermonkey stats extractor (v1.6.0)
- ✅ Tampermonkey posts extractor (v1.1.0)
- ✅ Python import scripts
- ✅ 4 real metrics display
- ✅ Up to 5 clickable posts
- ✅ Dedicated `/linkedin` page
- ✅ Auto-download + clipboard copy

#### Exercism
- ✅ Tampermonkey profile extractor
- ✅ API v2 integration for solutions
- ✅ DOM scraping for badges
- ✅ Python import script
- ✅ Dedicated `/exercism` page
- ✅ Badges, tracks, solutions display

#### GitHub
- ✅ Basic integration
- ✅ Mini stats card
- ✅ Repository count, stars, followers

#### Udemy
- ✅ Data import system
- ✅ Course progress tracking
- ✅ Mini stats card
- ✅ Student alias field

#### Remember The Milk (RTM)
- ✅ Tasks integration
- ✅ Active tasks, overdue, completed
- ✅ Mini stats card
- ✅ Priority indicators

#### Welltory Health (NEW in 0.5.0)
- ✅ Tampermonkey web app extractor
- ✅ 7 health metrics tracking
- ✅ Python import with trend calculation
- ✅ Database table (welltory_stats_history)
- ✅ Health score algorithm (6 weighted metrics)
- ✅ Homepage mini card
- ✅ Dedicated `/welltory` page with charts
- ✅ Detailed metrics explanations
- ✅ Monitoring page integration

### Pages

#### Homepage (`/`)
- ✅ Bio card (1/3 width, photo + info + learning + health)
- ✅ 6 mini stats cards (LinkedIn, Exercism, GitHub, Udemy, RTM, Welltory)
- ✅ Equal 1/3 distribution (masonry grid)
- ✅ Clickable health indicator (links to Welltory)

#### LinkedIn Page (`/linkedin`)
- ✅ Full stats grid (4 metrics)
- ✅ Recent posts (up to 5, clickable)
- ✅ Dedicated styling

#### Exercism Page (`/exercism`)
- ✅ Stats grid (reputation, badges, solutions, tracks)
- ✅ Badges showcase
- ✅ Language tracks
- ✅ Recent solutions

#### Welltory Page (`/welltory`) - NEW
- ✅ Health score card
- ✅ 6 metric stats grid
- ✅ General insights section
- ✅ Detailed metrics explanations (6 cards)
- ✅ Historical charts (Chart.js)
- ✅ Trends visualization

#### About Page (`/about`) - NEW
- ⚠️ **CRITICAL ISSUE**: Page not loading
- ✅ Template created
- ✅ API endpoint created (`/api/about-me`)
- ✅ Data aggregation logic
- ✅ Infographic styling
- ❌ Needs debugging (next session priority)

#### Monitoring Page (`/monitoring`)
- ✅ Scraper status
- ✅ Historical graphs
- ✅ Welltory stats included

### UI/UX Features
- ✅ Navbar with all pages (Home, LinkedIn, GitHub, Exercism, RTM, Health, Monitoring, About)
- ✅ Navbar partials for reusability
- ✅ Theme toggle (light/dark)
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Hover effects and animations
- ✅ Loading states with HTMX
- ✅ Simplified health section in bio card

### Data Management
- ✅ JSON-based data storage (`/app/data/`)
- ✅ Temporary import directory (`data_tmp/`)
- ✅ Auto-detection of latest files
- ✅ SQLite for historical tracking
- ✅ Separated profile.json from linkedin.json
- ✅ File scraper system for auto-import

### Automation
- ✅ Taskfile commands for all operations
- ✅ Docker-based development
- ✅ Import scripts with confirmation
- ✅ Tampermonkey extractors with auto-download
- ✅ Clipboard copy for convenience

---

## ⚠️ Known Issues

### Critical
1. **`/about` page not loading**
   - Template and endpoint exist
   - Data aggregation might be failing
   - Needs debugging (Priority 1 for next session)

### Architecture
2. **Monolithic backend**
   - All services in single main.py
   - Hard to maintain when external APIs change
   - **NEEDS**: Microservices refactoring with bridge pattern

### Minor
- None currently

---

## 🚨 Next Session Priorities (2026-01-05)

### Priority 1: Fix /about Page
- Debug endpoint response
- Check data aggregation logic
- Verify all data sources are available
- Test error handling

### Priority 2: Microservices Architecture
- Design bridge pattern for service abstraction
- Create service interface contracts
- Separate services:
  - LinkedIn service
  - GitHub service
  - Exercism service
  - Udemy service
  - RTM service
  - Welltory service
- Implement unified bridge/adapter layer
- Create service discovery mechanism
- Add service health checks

### Priority 3: Documentation Update
- Document microservices architecture
- Update API contracts
- Add troubleshooting guide

---

## 📊 Statistics

### Code Metrics
- **Backend Lines**: ~2000+
- **Frontend Lines**: ~1500+
- **CSS Lines**: ~1000+
- **Total Files**: 60+
- **Docker Containers**: 2 (backend, frontend)

### Features
- **Data Sources**: 6 (LinkedIn, GitHub, Exercism, Udemy, RTM, Welltory)
- **Pages**: 7 (Home, LinkedIn, Exercism, GitHub, RTM, Welltory, About, Monitoring)
- **API Endpoints**: 15+
- **Tampermonkey Scripts**: 4 (LinkedIn stats, LinkedIn posts, Exercism, Welltory)

### Data
- **JSON Files**: 8 (profile, linkedin, github, exercism, udemy, rtm, welltory, cache)
- **Database Tables**: 2+ (welltory_stats_history, scraper_logs)
- **Historical Data**: 90 days (Welltory)

---

## 🛠️ Technology Stack

### Backend
- **Runtime**: Python 3.11
- **Framework**: FastAPI (async)
- **Database**: SQLite
- **Data Format**: JSON
- **Container**: Docker

### Frontend
- **Runtime**: Bun
- **Templates**: Handlebars
- **Interactivity**: HTMX
- **Styling**: CSS (OKLCH color space)
- **Charts**: Chart.js
- **Container**: Docker

### Development
- **Orchestration**: Docker Compose
- **Task Runner**: Taskfile
- **Version Control**: Git
- **Browser Automation**: Tampermonkey

### Deployment
- **NPM Proxy**: Planned
- **SSL**: Planned
- **Production**: Not yet configured

---

## 📁 Project Structure

```
kapihome/
├── AI/                          # Session documents (gitignored)
│   ├── TODO.md                  # Next session priorities
│   ├── SESSION_NOTES.md         # Complete session history
│   ├── CHANGELOG.md             # Version changelog
│   ├── PROJECT_OVERVIEW.md      # Project description
│   └── STYLE_GUIDE.md           # Design system
├── backend/
│   ├── app/
│   │   └── main.py              # All API endpoints (NEEDS REFACTORING)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── server.ts            # Bun server with routes
│   │   ├── templates/
│   │   │   ├── partials/        # Reusable components
│   │   │   │   ├── navbar.hbs
│   │   │   │   └── head.hbs
│   │   │   ├── index.hbs        # Homepage
│   │   │   ├── linkedin.hbs
│   │   │   ├── exercism.hbs
│   │   │   ├── welltory.hbs     # NEW
│   │   │   ├── about.hbs        # NEW (not loading)
│   │   │   └── monitoring.hbs
│   │   └── static/
│   │       ├── css/             # 15+ CSS files
│   │       └── js/              # Theme toggle, HTMX
│   ├── Dockerfile
│   └── package.json
├── scrapers/
│   ├── database.py              # SQLite management
│   ├── file_scraper.py          # Auto-import system
│   └── cache_manager.py         # Cache sync
├── scripts/
│   ├── tampermonkey/            # 4 extractors
│   ├── update_*.py              # Import scripts
│   └── scheduler.py             # Cron jobs
├── data/                        # JSON data (gitignored)
│   ├── profile.json             # Separated from LinkedIn
│   ├── linkedin.json
│   ├── github.json
│   ├── exercism.json
│   ├── udemy.json
│   ├── rtm.json
│   ├── welltory.json            # NEW
│   └── cache.json
├── data_tmp/                    # Temporary imports (gitignored)
├── docs/                        # Documentation
│   ├── CURRENT_STATUS.md        # This file
│   ├── WELLTORY_SETUP.md
│   └── FINAL_SUMMARY.md
├── docker-compose.yml
├── Taskfile.yml
└── README.md
```

---

## 🎨 Design System

### Colors (OKLCH)
- **Primary**: `oklch(0.6726 0.2904 341.4084)` - Purple/Pink
- **Accent**: `oklch(0.8903 0.1739 171.2690)` - Cyan/Green
- **Background (Dark)**: `oklch(0.1649 0.0352 281.8285)`
- **Background (Light)**: `oklch(0.9816 0.0017 247.8390)`
- **Card (Dark)**: `oklch(0.2542 0.0611 281.1423)`
- **Card (Light)**: `oklch(1.0000 0 0)`

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 600, 700
- **Sizes**: Responsive with clamp()

### Components
- **Cards**: Glassmorphism with hover effects
- **Buttons**: Gradient with glow
- **Links**: Underline on hover
- **Charts**: Chart.js with theme colors

---

## 🔄 Workflow

### Development
```bash
task dev          # Start all services
task logs         # View logs
task restart      # Restart services
task clean        # Clean and rebuild
```

### Data Updates
```bash
# LinkedIn
task import-stats -- ~/Downloads/linkedin-stats-*.json
task import-posts -- ~/Downloads/linkedin-posts-*.json

# Exercism
task import-exercism -- ~/Downloads/exercism-*.json

# Welltory
task import-welltory -- ~/Downloads/welltory-*.json

# Or copy to data_tmp/ for auto-import
```

### Deployment
```bash
# Not yet configured
# Planned: NPM proxy, SSL, production env
```

---

## 📚 Documentation

- **README.md**: Quick start guide
- **AI/TODO.md**: Next session priorities
- **AI/SESSION_NOTES.md**: Complete session history
- **AI/CHANGELOG.md**: Version history
- **docs/WELLTORY_SETUP.md**: Welltory integration guide
- **scripts/tampermonkey/README.md**: Extractor documentation

---

## 🎯 Vision & Roadmap

### Immediate (Next Session)
1. Fix /about page
2. Microservices refactoring
3. Service health monitoring

### Short Term
- Automated data updates (Selenium/Puppeteer)
- Data visualization improvements
- Performance optimization
- Error handling enhancements

### Medium Term
- PWA support
- Offline mode
- Export functionality
- Admin panel

### Long Term
- Multi-user support
- Plugin system
- API for external integrations
- Mobile app

---

**Status**: Active Development  
**Maintainer**: Alessandro Middei  
**License**: Private  
**Repository**: https://github.com/stanzinofree/kapihome
