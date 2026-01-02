# KapiHome API Documentation

## Endpoints

### Health Check

```http
GET /health
```

Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "kapihome-backend"
}
```

### Root

```http
GET /
```

Returns API welcome message.

**Response:**
```json
{
  "message": "KapiHome API - Zen Capibara Style"
}
```

### LinkedIn Profile

```http
GET /api/linkedin
```

Returns LinkedIn profile data as HTML component for HTMX integration.

**Response:** HTML

Returns a fully formatted HTML snippet containing:
- Profile header (avatar, name, title, location)
- Bio/headline
- Statistics (profile views, post impressions - last 7 days)
- Current company and school badges
- Link to full LinkedIn profile
- Last update timestamp

**Data Source:** `data/linkedin.json`

**Update Frequency:** Every 4 hours via automated scraper

**Example HTML Structure:**
```html
<div class="linkedin-header">...</div>
<div class="linkedin-bio">...</div>
<div class="linkedin-stats">...</div>
<div class="linkedin-badge">...</div>
<div class="linkedin-actions">...</div>
<div class="linkedin-last-update">...</div>
```

## Data Structures

### LinkedIn JSON Schema

File: `data/linkedin.json`

```json
{
  "profile": {
    "name": "string",
    "title": "string",
    "headline": "string",
    "location": "string",
    "avatar_url": "string",
    "connections": "string",
    "profile_views": number,
    "post_impressions": number,
    "search_appearances": number,
    "current_company": "string",
    "current_school": "string"
  },
  "stats": {
    "profile_views_7d": number,
    "post_impressions_7d": number,
    "search_appearances_7d": number
  },
  "last_updated": "ISO 8601 datetime string"
}
```

## Future Endpoints

- `/api/exercism` - Exercism progress and badges
- `/api/udemy` - Udemy courses and certificates
- `/api/rss` - Aggregated RSS feeds
- `/api/projects` - Personal projects showcase
