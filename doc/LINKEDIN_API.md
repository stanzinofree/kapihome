# LinkedIn API Integration

## Authentication

LinkedIn usa OAuth 2.0 per l'autenticazione. Per accedere alle tue statistiche personali:

### 1. Creare un'App LinkedIn
1. Vai su https://www.linkedin.com/developers/apps
2. Crea una nuova app
3. Ottieni:
   - **Client ID**
   - **Client Secret**

### 2. Permessi Necessari

Per le statistiche del dashboard ti servono questi scopes:
- `r_basicprofile` - Informazioni profilo base
- `r_liteprofile` - Profilo lite
- `r_emailaddress` - Email (opzionale)
- `w_member_social` - Per i post
- `r_organization_social` - Statistiche organizzazione (se applicabile)

**NOTA**: LinkedIn ha limitato molto l'accesso alle statistiche personali. 
Le metriche del dashboard (`https://www.linkedin.com/dashboard/`) non sono sempre disponibili via API pubblica.

### 3. Generare Access Token

```bash
# Step 1: Authorization URL
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=r_liteprofile%20r_emailaddress%20w_member_social

# Step 2: Exchange code for token
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d grant_type=authorization_code \
  -d code={AUTHORIZATION_CODE} \
  -d redirect_uri={REDIRECT_URI} \
  -d client_id={CLIENT_ID} \
  -d client_secret={CLIENT_SECRET}
```

## Alternative: Web Scraping

Dato che le statistiche del dashboard non sono sempre accessibili via API, possiamo:

### Opzione 1: LinkedIn Unofficial API
Usare librerie come `linkedin-api` (Python) che fanno scraping:
```python
from linkedin_api import Linkedin

api = Linkedin('email', 'password')
profile = api.get_profile('stanzinofree')
```

**PRO**: Accesso a più dati
**CONTRO**: Viola i ToS di LinkedIn, rischio ban

### Opzione 2: Browser Automation (Puppeteer/Playwright)
Script che:
1. Fa login automatico
2. Naviga su https://www.linkedin.com/dashboard/
3. Estrae i dati dalla pagina
4. Salva in JSON

**PRO**: Dati completi, simula comportamento umano
**CONTRO**: Più complesso, richiede manutenzione

### Opzione 3: Manuale con estensione browser
Creare un'estensione Chrome/Firefox che:
1. Si autentica con le tue credenziali
2. Periodicamente estrae i dati dal dashboard
3. Li salva automaticamente nel JSON

**PRO**: Più sicuro, controllo totale
**CONTRO**: Richiede interazione periodica

## Statistiche Disponibili

Dal dashboard LinkedIn puoi ottenere:

### Profile Analytics
- Profile views (7/30/90 giorni)
- Search appearances
- Post impressions
- Follower count
- Connection growth

### Post Analytics
- Views per post
- Engagement rate
- Comments count
- Shares count
- Reactions breakdown

### Suggested Stats Structure

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
    "connections": "500+",
    "connection_growth_7d": 12,
    "engagement_rate": 3.2
  }
}
```

## Raccomandazione

Per ora, la soluzione più pratica è:

1. **Manuale periodico**: Tu aggiorni manualmente `data/linkedin.json` ogni settimana
2. **Script semi-automatico**: Creiamo uno script Python che ti chiede i dati e aggiorna il JSON
3. **Future scraper**: Quando hai tempo, implementiamo browser automation (Playwright)

### Script Helper (Opzione 2)

```python
# scripts/update_linkedin_stats.py
import json
from datetime import datetime

def update_stats():
    print("=== LinkedIn Stats Update ===")
    
    stats = {
        "profile_views_7d": int(input("Profile views (7d): ")),
        "post_impressions_7d": int(input("Post impressions (7d): ")),
        "search_appearances_7d": int(input("Search appearances (7d): ")),
    }
    
    with open("../data/linkedin.json", "r+") as f:
        data = json.load(f)
        data["stats"] = stats
        data["last_updated"] = datetime.now().isoformat()
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    
    print("✅ Stats updated!")

if __name__ == "__main__":
    update_stats()
```

## Next Steps

1. Decidi quale approccio preferisci
2. Se vuoi API ufficiale, crea l'app su LinkedIn Developer
3. Se preferisci automazione, implementiamo Playwright scraper
4. Per ora, aggiornamento manuale funziona perfettamente

Dimmi come preferisci procedere!
