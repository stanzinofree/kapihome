# Welltory Integration Setup

Integrazione completa di Welltory per monitorare i tuoi dati di salute e benessere in KapiHome.

## 📊 Metriche Disponibili

L'integrazione Welltory traccia le seguenti metriche:
- **Stress** - Livello di stress (0-100)
- **Energy** - Livello di energia (0-100)
- **Productivity** - Indice di produttività
- **HRV** - Heart Rate Variability (variabilità della frequenza cardiaca)
- **Resting Heart Rate** - Frequenza cardiaca a riposo
- **Sleep Quality** - Qualità del sonno
- **Mood** - Umore

## 🚀 Setup

### 1. Installare lo script Tampermonkey

1. Assicurati di avere **Tampermonkey** installato nel tuo browser
2. Apri il file `/scripts/tampermonkey/welltory-stats-extractor.user.js`
3. Copia il contenuto
4. In Tampermonkey, crea un nuovo script e incolla il codice
5. Salva lo script

### 2. Estrarre i dati

1. Vai su [app.welltory.com](https://app.welltory.com)
2. Fai login con le tue credenziali
3. Naviga nella Dashboard
4. Clicca sul pulsante **"📊 Extract Welltory Stats"** (apparirà in basso a destra)
5. Lo script:
   - Estrae automaticamente le metriche dalla pagina
   - Copia i dati negli appunti
   - Scarica un file JSON `welltory-stats-YYYY-MM-DD.json`

### 3. Importare i dati in KapiHome

#### Opzione A: Import automatico (con scheduler attivo)

```bash
# Sposta il file scaricato in data_tmp/
mv ~/Downloads/welltory-stats-*.json ./data_tmp/

# Lo scheduler importerà automaticamente i dati
```

#### Opzione B: Import manuale

```bash
# Sposta il file in data_tmp/
mv ~/Downloads/welltory-stats-*.json ./data_tmp/

# Esegui l'import manualmente
task import-welltory
```

#### Opzione C: Import da file specifico

```bash
task import-welltory -- path/to/welltory-stats-2026-01-03.json
```

## 📁 Struttura Dati

### File estratto da Tampermonkey (`welltory-stats-*.json`)

```json
{
  "stats": {
    "stress": 45,
    "energy": 72,
    "productivity": 68,
    "hrv": 55,
    "resting_heart_rate": 65,
    "sleep_quality": 80,
    "mood": 7
  },
  "date": "2026-01-03",
  "extracted_at": "2026-01-03T18:30:00.000Z",
  "source": "welltory_webapp",
  "note": "Extracted from Welltory Web App"
}
```

### File in KapiHome (`./data/welltory.json`)

```json
{
  "current": {
    "stress": 45,
    "energy": 72,
    "productivity": 68,
    "hrv": 55,
    "resting_heart_rate": 65,
    "sleep_quality": 80,
    "mood": 7
  },
  "date": "2026-01-03",
  "last_updated": "2026-01-03T18:30:00.000Z",
  "historical_data": [
    {
      "date": "2026-01-03",
      "stats": { ... },
      "extracted_at": "2026-01-03T18:30:00.000Z"
    },
    {
      "date": "2026-01-02",
      "stats": { ... },
      "extracted_at": "2026-01-02T20:15:00.000Z"
    }
  ]
}
```

## 💡 Interpretazione delle Metriche

### Stress (0-100)
- **0-30**: 🟢 Livello basso - Ottimo!
- **30-60**: 🟡 Livello medio - Normale
- **60-100**: 🔴 Livello alto - Considera tecniche di rilassamento

### Energy (0-100)
- **70-100**: 🚀 Energia alta - Eccellente!
- **40-70**: ⚡ Energia moderata - Buono
- **0-40**: 😴 Energia bassa - Riposo necessario

### HRV (Heart Rate Variability)
- **> 60**: ❤️ Eccellente - Ottimo recupero
- **40-60**: 👍 Buono
- **< 40**: ⚠️ Basso - Recupero necessario

### Mood (0-10)
- **8-10**: 😄 Ottimo umore
- **5-7**: 😊 Umore normale
- **0-4**: 😔 Umore basso

## 🔄 Automazione

### Scheduler Automatico

Il file scraper monitora `./data_tmp/welltory.json` e importa automaticamente i nuovi dati ogni minuto.

```bash
# Verifica lo stato dello scheduler
docker-compose logs scrapers --tail 50
```

### Frequenza Consigliata

- **Minimo**: 1 volta al giorno (preferibilmente la mattina)
- **Ottimale**: 2-3 volte al giorno (mattina, pomeriggio, sera)
- **Massimo**: Ogni volta che vuoi tracciare un cambiamento significativo

## 📈 Visualizzazione

### Homepage Card

La card Welltory sulla homepage mostra:
- Stress con indicatore colorato (🟢🟡🔴)
- Energy con emoji dinamica (🚀⚡😴)
- HRV (Heart Rate Variability)
- Mood

### Pagina Dettagli (Coming Soon)

La pagina `/welltory` mostrerà:
- Grafici storici delle metriche
- Trend settimanali e mensili
- Correlazioni tra stress, energy e HRV
- Insights e raccomandazioni

## 🛠️ Troubleshooting

### Lo script Tampermonkey non trova i dati

**Problema**: Lo script estrae valori `null` per tutte le metriche

**Soluzioni**:
1. Assicurati di essere sulla dashboard principale di Welltory
2. Aspetta che la pagina carichi completamente tutti i widget
3. Prova a scorrere la pagina per assicurarti che tutti i dati siano visibili
4. Verifica nella console del browser (`F12`) se ci sono errori

### L'import fallisce

**Problema**: `task import-welltory` restituisce errore

**Soluzioni**:
1. Verifica che il file JSON sia valido:
   ```bash
   cat data_tmp/welltory-stats-*.json | jq .
   ```
2. Controlla i permessi del file:
   ```bash
   chmod 644 data_tmp/welltory-stats-*.json
   ```
3. Verifica che la struttura del JSON sia corretta (deve avere il campo `stats`)

### I dati non appaiono sulla homepage

**Problema**: La card Welltory mostra "Data not available"

**Soluzioni**:
1. Verifica che il file esista:
   ```bash
   ls -la data/welltory.json
   ```
2. Riavvia il backend:
   ```bash
   docker-compose restart backend
   ```
3. Controlla i log del backend:
   ```bash
   docker-compose logs backend --tail 50
   ```

## 🔐 Privacy

- Tutti i dati rimangono **locali** sul tuo sistema
- Nessun dato viene inviato a server esterni
- Il file JSON può essere cancellato in qualsiasi momento
- L'integrazione è **completamente offline** dopo l'estrazione

## 📝 Note

- L'integrazione Welltory è **opzionale** - KapiHome funziona anche senza
- I dati storici vengono mantenuti per **90 giorni**
- Puoi esportare i tuoi dati in qualsiasi momento dal file `./data/welltory.json`
- Lo script Tampermonkey usa strategie multiple per estrarre i dati, garantendo compatibilità anche con aggiornamenti futuri dell'interfaccia

## 🎯 Prossimi Passi

1. ✅ Installare lo script Tampermonkey
2. ✅ Estrarre i primi dati
3. ✅ Importare in KapiHome
4. ⏳ Configurare l'estrazione regolare (es. ogni mattina)
5. ⏳ Monitorare i trend settimanali
6. ⏳ Correlare stress/energy con produttività

---

**Buon monitoraggio della salute! 🏥💪**
