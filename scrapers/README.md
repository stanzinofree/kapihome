# KapiHome Scraper Service

Sistema automatizzato di raccolta dati con caching intelligente e storicizzazione in database.

## Architettura

```
┌──────────────────┐
│  Tampermonkey    │ ← Estrazione manuale (LinkedIn, GitHub, Exercism, Udemy)
│  Scripts         │
└────────┬─────────┘
         │
         v
┌──────────────────┐
│   data_tmp/      │ ← File JSON temporanei
│  *.json files    │
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  File Importers  │ ← Importano solo se file più recente
│  (ogni 10 min)   │
└────────┬─────────┘
         │
         ├─────→ data/*.json (cache attiva per il backend)
         │
         └─────→ data/kapihome.db (storico per analytics)
```

## Componenti

### 1. **File-based Scrapers** (da Tampermonkey)
- `LinkedInScraper` - Importa da `data_tmp/linkedin.json`
- `GitHubScraper` - Importa da `data_tmp/github.json`
- `ExercismScraper` - Importa da `data_tmp/exercism.json`
- `UdemyScraper` - Importa da `data_tmp/udemy.json`

### 2. **API Scrapers** (automatici)
- `RTMScraper` - Remember The Milk API (ogni 10 min)

### 2. **Cache Manager**
- Monitora `data_tmp/` per modifiche
- Sincronizza automaticamente in `data/`
- Salva snapshot in database SQLite
- Gira ogni 2 minuti

### 3. **Database SQLite**
- Storico completo di tutte le metriche
- Time-series per dashboard analytics
- Schema con tabelle per RTM, LinkedIn, GitHub, etc.

### 4. **Scheduler**
- Esegue scrapers ogni 10 minuti
- Sincronizza cache ogni 2 minuti
- Auto-restart su crash

## Setup Iniziale

### 1. Configura credenziali RTM

Aggiungi le tue API key nel file `.env`:

```env
RTM_API_KEY=your_api_key_here
RTM_API_SECRET=your_api_secret_here
```

### 2. Autentica RTM (prima volta)

```bash
task setup-rtm
```

Segui il link che apparirà, autorizza l'app, e premi Enter.
Il token verrà salvato in `data/.rtm_token` (gitignored).

### 3. Avvia il servizio scraper

```bash
task scrape-start
```

Il servizio ora gira in background e raccoglierà dati ogni 10 minuti.

## Comandi Disponibili

### Gestione Scraper Service

```bash
# Avvia servizio (background, ogni 10 min)
task scrape-start

# Ferma servizio
task scrape-stop

# Visualizza logs in tempo reale
task logs-scrapers

# Accedi alla shell del container
task shell-scrapers
```

### Operazioni Manuali

```bash
# Scrape RTM una sola volta
task scrape-rtm

# Forza sincronizzazione cache
task cache-sync

# Verifica stato database
task db-status
```

## Workflow Completo

### Per LinkedIn, GitHub, Exercism, Udemy (Manuale con Tampermonkey):

1. **Estrai dati** con script Tampermonkey
2. **Salva JSON** in `data_tmp/` (es: `linkedin.json`, `github.json`)
3. **Scheduler** (ogni 10 min):
   - Controlla timestamp dei file in `data_tmp/`
   - Se più recenti dell'ultima importazione:
     - Importa dati
     - Salva in `data/*.json` (cache)
     - Salva snapshot in `data/kapihome.db`
4. **Backend** legge da `data/*.json`
5. **Frontend** mostra i dati aggiornati

### Per RTM (Automatico via API):

1. **RTM Scraper** (ogni 10 min):
   - Si connette a RTM API
   - Scarica tasks aggiornati
   - Salva in `data_tmp/rtm.json`
2. **File Importer** rileva il file nuovo
3. Importa e salva nel DB
4. **Cache Manager** sincronizza in `data/`

### Comandi Utili:

```bash
# Verifica stato importazioni
task import-status

# Importa manualmente file aggiornati
task import-check

# Forza import di tutti i file (ignora timestamp)
task import-now
```

## Database Schema

### Tabelle principali:

- `rtm_stats_history` - Statistiche RTM nel tempo
- `rtm_tasks_snapshot` - Snapshot completo dei task
- `linkedin_stats_history` - Metriche LinkedIn
- `github_stats_history` - Metriche GitHub
- `exercism_stats_history` - Metriche Exercism
- `udemy_stats_history` - Metriche Udemy
- `metrics_history` - Metriche generiche estensibili

### Query esempio:

```python
from database import KapiHomeDB

db = KapiHomeDB()

# Ultimi 30 giorni di statistiche RTM
history = db.get_rtm_stats_history(days=30)

# Trend completamento task
trend = db.get_completion_trend(source='rtm', days=30)
```

## File Struttura

```
scrapers/
├── Dockerfile              # Container scraper
├── requirements.txt        # Dipendenze Python
├── scheduler.py           # Orchestratore principale
├── database.py            # Gestione database SQLite
├── cache_manager.py       # Sincronizzazione cache
├── rtm_scraper.py         # Scraper RTM
├── setup_rtm.py          # Setup autenticazione RTM
└── README.md             # Questa documentazione
```

## Logs e Monitoring

### Visualizza logs scraper:
```bash
task logs-scrapers
```

### Formato logs:
```
[2026-01-03 14:30:00] 🚀 Starting scheduled scrape cycle
  → Fetching tasks from RTM...
  ✓ Fetched 45 tasks from RTM
  ✓ RTM data saved to /app/data_tmp/rtm.json
  
  🔄 Starting cache sync...
  ✓ Synced rtm.json to cache
    → Saved RTM stats to database (45 tasks)
  ✓ Cache sync completed
```

## Troubleshooting

### RTM authentication failed
- Verifica che RTM_API_KEY e RTM_API_SECRET siano corretti in `.env`
- Riesegui `task setup-rtm` per ri-autenticare
- Elimina `data/.rtm_token` e riprova

### Cache non sincronizzato
- Verifica permessi su `data/` e `data_tmp/`
- Controlla logs: `task logs-scrapers`
- Forza sync: `task cache-sync`

### Database locked
- Il database SQLite è single-writer
- Assicurati che non ci siano più processi che scrivono
- Riavvia il servizio: `task scrape-stop && task scrape-start`

## Esempio Workflow Completo

### Scenario: Aggiornare dati LinkedIn

1. Vai su LinkedIn dashboard
2. Esegui script Tampermonkey "Extract LinkedIn Stats"
3. Salva file `linkedin-stats-2026-01-03.json` generato
4. Copia in `data_tmp/linkedin.json`
5. Entro 10 minuti:
   ```
   [2026-01-03 15:00:00] 🔍 Checking for new data...
     ✓ Imported linkedin.json (modified: 2026-01-03 14:58:30)
       → Saved to DB: 650 followers, 1200 impressions
     ✓ Synced linkedin.json to cache
   ```
6. Il backend ora serve i dati aggiornati
7. Lo storico è salvato nel database per analytics

## Prossimi Sviluppi

- [x] File-based importers per LinkedIn, GitHub, Exercism, Udemy
- [x] RTM API scraper automatico
- [x] Sistema di tracking timestamp per evitare re-import
- [ ] Dashboard analytics con grafici storici
- [ ] API endpoint per dati storici (/api/analytics/linkedin?days=30)
- [ ] Notifiche su anomalie (es. drop improvviso followers)
- [ ] Export dati in CSV/Excel
- [ ] Backup automatico database
- [ ] Web UI per visualizzare log scraper in tempo reale

## Note

- Il servizio scraper gira in un container separato per isolamento
- I dati sono persistiti in volumi Docker
- Il database è in `data/kapihome.db` (gitignored)
- Token RTM salvato in `data/.rtm_token` (gitignored)
- Tutti i file sensibili sono protetti da `.gitignore`
