# LinkedIn Data Export - Open Data

## Opzione Migliore: Download Your Data

LinkedIn offre un'opzione ufficiale per scaricare TUTTI i tuoi dati in formato CSV/JSON!

### Come Scaricare

1. Vai su https://www.linkedin.com/mypreferences/d/download-my-data
2. Oppure: Settings & Privacy → Data Privacy → Get a copy of your data
3. Seleziona cosa scaricare:
   - **Fast file**: Dati base (connections, messages, profile)
   - **Complete archive**: Tutto (include analytics, views, engagement)

4. LinkedIn ti manda un'email quando è pronto (di solito in 10-24 ore)
5. Download ZIP file con tutti i dati

### Struttura dei Dati Scaricati

Il file ZIP contiene:

```
linkedin_data/
├── Profile.csv                 # Il tuo profilo
├── Connections.csv             # Lista connessioni
├── messages/                   # Messaggi
├── Reactions.csv              # Reactions ai post
├── Shares.csv                 # Post condivisi
├── Posts.csv                  # I tuoi post
├── Profile_Views.csv          # Chi ha visto il profilo
├── Search_Appearances.csv     # Apparizioni nelle ricerche
├── Post_Views.csv             # Statistiche post
└── ...
```

### Vantaggi

✅ **Ufficiale**: Dati certificati da LinkedIn
✅ **Completo**: Include tutto, anche dati storici
✅ **Legale**: Rispetta GDPR e ToS
✅ **No API**: Non serve token o autenticazione complessa
✅ **Aggiornabile**: Puoi richiedere nuovi export periodicamente

### Svantaggi

❌ Non in real-time (devi richiedere export)
❌ Può richiedere 24 ore
❌ Dati in CSV, serve parsing

## Script di Parsing

Possiamo creare uno script che:
1. Legge i CSV dall'export LinkedIn
2. Estrae i dati che ci servono
3. Aggiorna `data/linkedin.json`

### Esempio Script

```python
# scripts/parse_linkedin_export.py
import csv
import json
from datetime import datetime
from pathlib import Path

def parse_linkedin_export(export_dir):
    """Parse LinkedIn data export and update JSON"""
    
    export_path = Path(export_dir)
    data = {
        "profile": {},
        "stats": {},
        "recent_posts": [],
        "recent_shares": []
    }
    
    # Parse Profile
    profile_csv = export_path / "Profile.csv"
    if profile_csv.exists():
        with open(profile_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            profile_data = next(reader)
            data["profile"] = {
                "name": f"{profile_data['First Name']} {profile_data['Last Name']}",
                "job_position": profile_data.get('Headline', ''),
                "location": f"{profile_data.get('City', '')}, {profile_data.get('Country', '')}",
                # ... altri campi
            }
    
    # Parse Posts
    posts_csv = export_path / "Posts.csv"
    if posts_csv.exists():
        with open(posts_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            posts = list(reader)
            # Prendi gli ultimi 2 post
            for post in posts[:2]:
                data["recent_posts"].append({
                    "title": post.get('SharedText', '')[:100],
                    "excerpt": post.get('SharedText', '')[:200],
                    "date": post.get('Date', ''),
                    "url": post.get('SharedUrl', '#')
                })
    
    # Parse Shares
    shares_csv = export_path / "Shares.csv"
    if shares_csv.exists():
        with open(shares_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            shares = list(reader)
            for share in shares[:2]:
                data["recent_shares"].append({
                    "author": share.get('Author', 'Unknown'),
                    "title": share.get('SharedCommentary', '')[:100],
                    "date": share.get('Date', ''),
                    "url": share.get('SharedUrl', '#')
                })
    
    # Parse Stats (questi potrebbero non essere nel CSV, vedere sotto)
    # Profile views potrebbero essere calcolate da Profile_Views.csv
    
    # Save to JSON
    output_file = Path("../data/linkedin.json")
    data["last_updated"] = datetime.now().isoformat()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ LinkedIn data parsed and saved to {output_file}")
    return data

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        export_dir = sys.argv[1]
    else:
        export_dir = input("Path to LinkedIn export directory: ")
    
    parse_linkedin_export(export_dir)
```

### Uso

```bash
# Scarica ed estrai il file ZIP da LinkedIn
unzip linkedin_export.zip -d linkedin_data/

# Esegui lo script
cd scripts
python parse_linkedin_export.py ../linkedin_data/
```

## Note sulle Statistiche

⚠️ **Importante**: Il data export NON include alcune metriche in tempo reale come:
- Profile views count (ultimi 7/30/90 giorni)
- Post impressions totali
- Search appearances count

Queste metriche sono visibili solo nel dashboard LinkedIn.

### Soluzione Ibrida

1. **Dati base**: Usa LinkedIn export (post, shares, profile)
2. **Stats dashboard**: 
   - Opzione A: Aggiornamento manuale settimanale
   - Opzione B: Playwright scraper solo per stats
   - Opzione C: Script helper che ti chiede i numeri

### Script Helper per Stats

```python
# scripts/update_stats.py
import json
from datetime import datetime

def update_stats():
    print("=== Update LinkedIn Stats ===")
    print("Copia i numeri da: https://www.linkedin.com/dashboard/\n")
    
    stats = {
        "profile_views_7d": int(input("Profile views (7 giorni): ")),
        "profile_views_30d": int(input("Profile views (30 giorni): ")),
        "profile_views_90d": int(input("Profile views (90 giorni): ")),
        "post_impressions_7d": int(input("Post impressions (7 giorni): ")),
        "post_impressions_30d": int(input("Post impressions (30 giorni): ")),
        "search_appearances_7d": int(input("Search appearances (7 giorni): ")),
        "search_appearances_30d": int(input("Search appearances (30 giorni): ")),
        "followers": int(input("Followers: ")),
        "connection_growth_7d": int(input("New connections (7 giorni): ")),
        "engagement_rate": float(input("Engagement rate (%): "))
    }
    
    # Carica JSON esistente
    with open("../data/linkedin.json", "r") as f:
        data = json.load(f)
    
    # Aggiorna stats
    data["stats"] = stats
    data["last_updated"] = datetime.now().isoformat()
    
    # Salva
    with open("../data/linkedin.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Stats aggiornate!")

if __name__ == "__main__":
    update_stats()
```

## Raccomandazione Finale

**Setup ottimale:**

1. **Ogni mese**: Scarica LinkedIn data export
   - Esegui `parse_linkedin_export.py`
   - Aggiorna post, shares, profile automaticamente

2. **Ogni settimana**: Aggiorna stats manualmente
   - Esegui `update_stats.py`
   - Copia-incolla numeri dal dashboard (2 minuti)

3. **Futuro** (opzionale): Playwright scraper
   - Solo per stats
   - Eseguito automaticamente ogni 4 ore
   - Fallback su manuale se non funziona

Questa combo ti dà:
- ✅ Dati ufficiali e accurati
- ✅ Nessuna violazione ToS
- ✅ Minimo sforzo manuale
- ✅ Automation dove possibile

Vuoi che creiamo gli script di parsing?
