# LinkedIn Stats Extractor - Tampermonkey Script

Userscript per estrarre automaticamente le statistiche dal dashboard LinkedIn.

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

## Note di sicurezza

- Lo script NON invia dati a server esterni
- Funziona solo in locale nel tuo browser
- Non modifica nulla su LinkedIn, è read-only
- I dati estratti rimangono solo sul tuo computer
