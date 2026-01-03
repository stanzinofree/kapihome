# Tampermonkey Scripts for KapiHome

Userscripts per estrarre automaticamente dati da LinkedIn ed Exercism.

## 📊 LinkedIn Stats & Posts Extractor

Due script separati per estrarre statistiche e post da LinkedIn.

### 🔢 LinkedIn Stats Extractor

Estrae le statistiche dal dashboard LinkedIn.

## Installazione

1. **Installa Tampermonkey**
   - Chrome: [Tampermonkey su Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
   - Firefox: [Tampermonkey su Firefox Add-ons](https://addons.mozilla.org/it/firefox/addon/tampermonkey/)
   - Edge: [Tampermonkey su Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd)

2. **Installa lo script**
   - Apri Tampermonkey e vai su "Dashboard"
   - Click su "+" (Nuovo script)
   - Copia il contenuto di `linkedin-stats-extractor.user.js`
   - Incolla nell'editor e salva (Ctrl+S)

## Utilizzo

1. **Accedi a LinkedIn**
   - Fai login su [linkedin.com](https://www.linkedin.com)

2. **Vai al Dashboard**
   - Apri [https://www.linkedin.com/dashboard/](https://www.linkedin.com/dashboard/)
   - Aspetta che la pagina carichi completamente le statistiche

3. **Estrai le statistiche**
   - Apparirà un pulsante flottante in basso a destra: **"📊 Extract Stats"**
   - Click sul pulsante
   - Si aprirà una modale con:
     - **Summary**: Riepilogo delle statistiche estratte
     - **JSON Output**: Dati in formato JSON

4. **Esporta i dati**
   - **📋 Copy JSON**: Copia il JSON negli appunti
   - **💾 Download JSON**: Scarica un file `linkedin-stats-YYYY-MM-DD.json`
   - **✕ Close**: Chiudi la modale

## Dati estratti

Lo script estrae automaticamente:

```json
{
  "stats": {
    "profile_views_7d": 183,
    "profile_views_30d": 650,
    "profile_views_90d": 1850,
    "post_impressions_7d": 1076,
    "post_impressions_30d": 4200,
    "search_appearances_7d": 8,
    "search_appearances_30d": 45,
    "followers": 520,
    "connection_growth_7d": 12,
    "engagement_rate": 3.2
  },
  "extracted_at": "2026-01-02T12:30:00.000Z",
  "note": "Extracted from LinkedIn Dashboard"
}
```

## Integrazione con update_stats.py

### Opzione 1: Copia manuale del JSON

```bash
# 1. Estrai le stats dal browser con Tampermonkey
# 2. Copia il JSON (button "Copy JSON")
# 3. Salva in un file temporaneo
echo '<json-copiato>' > /tmp/linkedin-stats.json

# 4. Aggiorna linkedin.json
python3 scripts/update_stats_from_json.py /tmp/linkedin-stats.json
```

### Opzione 2: Download automatico

```bash
# 1. Estrai le stats e scarica il file JSON
# 2. Il file sarà in ~/Downloads/linkedin-stats-YYYY-MM-DD.json
# 3. Importa direttamente
python3 scripts/update_stats_from_json.py ~/Downloads/linkedin-stats-*.json
```

## Come funziona

Lo script:
1. Inserisce un pulsante flottante sulla pagina del dashboard LinkedIn
2. Quando cliccato, scansiona il DOM della pagina cercando le card delle statistiche
3. Estrae i numeri usando pattern di ricerca (es. "profile view", "impressions", "followers")
4. Calcola automaticamente l'engagement rate se ha dati sufficienti
5. Mostra i risultati in una modale stilizzata con i colori del progetto KapiHome
6. Permette di copiare o scaricare il JSON

## Troubleshooting

### Non estrae nessun dato (tutti valori a 0)

**Causa**: Il layout LinkedIn potrebbe essere cambiato o le statistiche non sono ancora caricate.

**Soluzione**:
1. Aspetta che la pagina carichi completamente
2. Scorri verso il basso per assicurarti che tutte le card siano visibili
3. Ricarica la pagina e riprova
4. Apri la console browser (F12) e guarda i log per vedere cosa trova

### Il pulsante non appare

**Causa**: Lo script potrebbe non essere attivo o essere bloccato.

**Soluzione**:
1. Verifica che Tampermonkey sia attivo (icona verde nella toolbar)
2. Verifica che lo script sia abilitato nel dashboard Tampermonkey
3. Controlla che l'URL corrisponda: `https://www.linkedin.com/dashboard/`
4. Ricarica la pagina

### I numeri non corrispondono

**Causa**: LinkedIn mostra dati diversi in diverse sezioni.

**Soluzione**:
- Lo script cerca di estrarre i dati dalle card principali del dashboard
- Verifica visivamente che i numeri nel JSON corrispondano a quelli mostrati
- Se necessario, modifica manualmente i valori estratti

## Aggiornamenti dello script

LinkedIn aggiorna frequentemente il layout. Se lo script smette di funzionare:

1. Apri la console browser (F12)
2. Ispeziona le card delle statistiche
3. Nota i nuovi selettori CSS o classi
4. Aggiorna lo script modificando:
   ```javascript
   const viewsCards = document.querySelectorAll('[nuovi-selettori]');
   ```

### 📝 LinkedIn Posts Extractor

Estrae i post recenti dalla pagina attività LinkedIn.

**File**: `linkedin-posts-extractor.user.js`

**Come usare**:
1. Visita la tua pagina attività LinkedIn
2. Click sul pulsante "Extract LinkedIn Posts"
3. Scarica il JSON generato
4. Importa con: `task import-posts -- ~/Downloads/linkedin-posts-*.json`

**Dati estratti**:
- Titolo del post (prime 100 caratteri)
- Excerpt del contenuto (250 caratteri)
- Data di pubblicazione
- URL del post

---

## 🎯 Exercism Data Extractor

Script per estrarre badge, statistiche e soluzioni da Exercism.

**File**: `exercism-extractor.user.js`

### Installazione

1. Apri Tampermonkey Dashboard
2. Click "+" per nuovo script
3. Copia il contenuto di `exercism-extractor.user.js`
4. Salva (Ctrl+S)

### Utilizzo

1. **Visita il tuo profilo Exercism**
   - URL: `https://exercism.org/profiles/YOUR_USERNAME`

2. **Estrai i dati**
   - Apparirà un pulsante viola: **"📊 Extract Exercism Data"**
   - Click sul pulsante
   - Si aprirà un alert con il riepilogo dei dati estratti

3. **File generato**
   - JSON scaricato automaticamente: `exercism-data-YYYY-MM-DD.json`
   - JSON copiato negli appunti

### Dati estratti

```json
{
  "profile": {
    "username": "stanzinofree",
    "location": "Rome, Italy"
  },
  "stats": {
    "reputation": 27,
    "total_badges": 5,
    "total_solutions": 27,
    "total_tracks": 5,
    "badges_by_rarity": {
      "common": 4,
      "rare": 1,
      "ultimate": 0,
      "legendary": 0
    }
  },
  "badges": [
    {
      "name": "Anybody there?",
      "rarity": "common",
      "icon_url": "https://assets.exercism.org/..."
    }
  ],
  "tracks": [
    {
      "name": "Go",
      "exercises_completed": 8,
      "icon_url": "https://..."
    }
  ],
  "recent_solutions": [
    {
      "exercise": "Two Fer",
      "track": "Go",
      "status": "published",
      "published_at": "2024-12-15",
      "num_stars": 0,
      "num_comments": 0,
      "url": "https://exercism.org/tracks/go/exercises/two-fer"
    }
  ],
  "extracted_at": "2026-01-02T15:30:00.000Z"
}
```

### Integrazione con update_exercism_from_json.py

```bash
# 1. Estrai i dati dal browser con Tampermonkey
# 2. Il file sarà in ~/Downloads/exercism-data-YYYY-MM-DD.json
# 3. Importa direttamente
task import-exercism -- ~/Downloads/exercism-data-*.json

# Oppure con Python diretto
python3 scripts/update_exercism_from_json.py ~/Downloads/exercism-data-2026-01-02.json
```

### Come funziona

Lo script:
1. Inserisce un pulsante viola sulla pagina del profilo Exercism
2. Quando cliccato:
   - Estrae reputation, badge count, location dal profilo
   - Chiama l'API pubblica di Exercism (`/api/v2/profiles/{username}/solutions`)
   - Estrae i badge visibili sulla pagina (con icone e rarità)
   - Aggrega i dati delle soluzioni per track
   - Ottiene le 5 soluzioni più recenti
3. Genera un JSON completo con tutti i dati
4. Scarica automaticamente il file e lo copia negli appunti

### Troubleshooting

**Non estrae i badge**:
- Assicurati di essere sulla pagina principale del profilo
- Per vedere tutti i badge, visita: `https://exercism.org/profiles/YOUR_USERNAME/badges`
- Ricarica la pagina e riprova

**API non risponde**:
- Controlla la console (F12) per errori di rete
- Verifica che il profilo sia pubblico
- L'API potrebbe essere temporaneamente non disponibile

**Dati mancanti**:
- Lo script estrae solo dati pubblici
- Alcuni dati potrebbero non essere visibili senza login
- Verifica che il profilo sia completo

---

## 🐙 GitHub Stats Extractor

Script per estrarre statistiche, repository e linguaggi da GitHub.

**File**: `github-extractor.user.js`

### Installazione

1. Apri Tampermonkey Dashboard
2. Click "+" per nuovo script
3. Copia il contenuto di `github-extractor.user.js`
4. Salva (Ctrl+S)

### Utilizzo

1. **Visita il tuo profilo GitHub**
   - URL: `https://github.com/YOUR_USERNAME`

2. **Estrai i dati**
   - Apparirà un pulsante verde: **"💾 Export GitHub Stats"**
   - Click sul pulsante
   - Si aprirà un alert con il riepilogo dei dati estratti

3. **File generato**
   - JSON scaricato automaticamente: `github-data-YYYYMMDD-HHMMSS.json`
   - JSON copiato negli appunti

### Dati estratti

```json
{
  "profile": {
    "username": "stanzinofree",
    "name": "Alessandro Middei",
    "bio": "Full Stack Developer",
    "location": "Rome, Italy",
    "company": "Freelance",
    "website": "https://middei.info",
    "avatar_url": "https://avatars.githubusercontent.com/...",
    "profile_url": "https://github.com/stanzinofree"
  },
  "stats": {
    "followers": 42,
    "following": 30,
    "public_repos": 56,
    "total_stars": 124,
    "total_forks": 18,
    "contributions_last_year": 847,
    "current_streak": 12,
    "longest_streak": 45
  },
  "top_languages": [
    {
      "name": "Python",
      "count": 25,
      "percentage": 45
    },
    {
      "name": "JavaScript",
      "count": 18,
      "percentage": 32
    }
  ],
  "top_repos": [
    {
      "name": "kapihome",
      "full_name": "stanzinofree/kapihome",
      "description": "Personal homepage",
      "url": "https://github.com/stanzinofree/kapihome",
      "stars": 15,
      "forks": 3,
      "language": "Python",
      "updated_at": "2026-01-02T12:00:00Z"
    }
  ],
  "recent_activity": [
    {
      "name": "kapihome",
      "action": "Updated",
      "date": "2026-01-02T12:00:00Z",
      "url": "https://github.com/stanzinofree/kapihome"
    }
  ],
  "extracted_at": "2026-01-02T15:30:00.000Z"
}
```

### Integrazione con update_github_from_json.py

```bash
# 1. Estrai i dati dal browser con Tampermonkey
# 2. Il file sarà in ~/Downloads/github-data-YYYYMMDD-HHMMSS.json
# 3. Muovi il file in data_tmp/
mv ~/Downloads/github-data-*.json data_tmp/

# 4. Importa (auto-detect)
task import-github

# Oppure con Python diretto e path specifico
python3 scripts/update_github_from_json.py ~/Downloads/github-data-20260102-153000.json
```

### Come funziona

Lo script:
1. Inserisce un pulsante verde sulla pagina del profilo GitHub
2. Quando cliccato:
   - Estrae dati dal profilo (nome, bio, avatar, location, company)
   - Estrae statistiche visibili (followers, following)
   - Chiama l'API pubblica GitHub (`https://api.github.com/users/{username}/repos`)
   - Calcola total stars, forks dai repository
   - Analizza i linguaggi più usati
   - Estrae contribution calendar dal DOM (streak corrente e più lungo)
   - Seleziona i top 6 repository per stelle
   - Identifica i 10 repository aggiornati più di recente
3. Genera un JSON completo con tutti i dati
4. Scarica automaticamente il file e lo copia negli appunti

### Troubleshooting

**API rate limiting**:
- L'API pubblica GitHub ha un limite di 60 richieste/ora senza autenticazione
- Se raggiungi il limite, aspetta 1 ora prima di riprovare
- Per limiti più alti, considera di usare un token personale (non implementato)

**Contribution calendar non funziona**:
- Assicurati di essere sulla pagina principale del profilo
- Il contribution calendar deve essere visibile (scorri se necessario)
- Lo script cerca elementi con `tool-tip[id*="contribution-day"]`

**Repositories mancanti**:
- Lo script recupera solo i primi 100 repository (ordinati per aggiornamento)
- Repository privati non sono inclusi (solo pubblici)
- Fork sono inclusi nelle stats ma filtrati dai "top repos"

**Dati profilo mancanti**:
- Alcuni campi potrebbero essere vuoti se non impostati nel profilo
- Website, company, location sono opzionali

---

## Note di sicurezza

- Gli script NON inviano dati a server esterni
- Funzionano solo in locale nel tuo browser
- Non modificano nulla sui siti, sono read-only
- I dati estratti rimangono solo sul tuo computer
- Le API GitHub/Exercism sono pubbliche e accessibili senza autenticazione
- Nessun token o credenziale viene salvato o trasmesso
