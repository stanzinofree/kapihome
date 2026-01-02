# Exercism Data Export Guide

This guide explains how to extract and import your Exercism profile data into KapiHome.

## Overview

The Exercism integration combines:
- **Exercism API v2** for solutions data
- **DOM scraping** for badges (not available via API)
- **Tampermonkey userscript** for automated extraction
- **Python import script** for data import with auto-detection

## Extraction Methods

### Method 1: Tampermonkey Script (Recommended)

1. **Install the userscript**:
   - Open `scripts/tampermonkey/exercism-extractor.user.js`
   - Copy the entire content
   - In Tampermonkey, create a new script and paste
   - Save (Ctrl+S / Cmd+S)

2. **Run the script**:
   - Navigate to your Exercism profile: `https://exercism.org/profiles/YOUR_USERNAME`
   - The script runs automatically
   - Click the floating "💾 Export" button (bottom-right)
   - Script will:
     - Call Exercism API v2 for solutions
     - Scrape the page for badges
     - Extract stats from the page
     - Generate `exercism-data-YYYYMMDD-HHMMSS.json`
     - Auto-download the file
     - Copy JSON to clipboard

3. **Move the file**:
   ```bash
   mv ~/Downloads/exercism-data-*.json data_tmp/
   ```

### Method 2: Manual API Call + Page Scraping

Not recommended - use the Tampermonkey script instead.

## Import to KapiHome

### Auto-Detection (Recommended)

```bash
# Place JSON in data_tmp/
mv ~/Downloads/exercism-data-*.json data_tmp/

# Run import (finds latest file automatically)
task import-exercism
```

### Manual Path

```bash
# Specify exact file
task import-exercism -- path/to/exercism-data.json
```

## Data Structure

```json
{
  "profile": {
    "username": "stanzinofree",
    "name": "Alessandro Middei",
    "bio": "Learning by doing",
    "location": "Italy",
    "joined_at": "2024-01-15"
  },
  "stats": {
    "reputation": 1234,
    "total_badges": 15,
    "total_solutions": 42,
    "total_tracks": 8
  },
  "badges": [
    {
      "name": "Functional February",
      "rarity": "rare",
      "icon_url": "https://assets.exercism.org/badges/..."
    }
  ],
  "tracks": [
    {
      "name": "Python",
      "icon_url": "https://assets.exercism.org/tracks/python.svg",
      "exercises_completed": 25,
      "num_solutions": 25
    }
  ],
  "recent_solutions": [
    {
      "uuid": "abc123...",
      "exercise": "two-fer",
      "track": "Python",
      "track_icon": "https://...",
      "published_at": "2024-12-15",
      "num_stars": 3,
      "num_comments": 1,
      "url": "https://exercism.org/tracks/python/exercises/two-fer"
    }
  ],
  "extracted_at": "2026-01-02T15:30:00.000Z"
}
```

## Exercism API v2

The script uses the public Exercism API v2:

**Endpoint**: `https://exercism.org/api/v2/profiles/{username}/solutions`

**Response**:
```json
{
  "solutions": [
    {
      "uuid": "...",
      "private_url": "...",
      "public_url": "...",
      "status": "published",
      "mentoring_status": "finished",
      "published_iteration_head_tests_status": "passed",
      "has_notifications": false,
      "num_views": 12,
      "num_stars": 3,
      "num_comments": 1,
      "num_iterations": 4,
      "num_loc": 25,
      "is_out_of_date": false,
      "published_at": "2024-12-15T10:30:00Z",
      "completed_at": "2024-12-15T10:30:00Z",
      "updated_at": "2024-12-16T08:15:00Z",
      "last_iterated_at": "2024-12-15T10:25:00Z",
      "exercise": {
        "slug": "two-fer",
        "title": "Two Fer",
        "icon_url": "https://..."
      },
      "track": {
        "slug": "python",
        "title": "Python",
        "icon_url": "https://..."
      }
    }
  ],
  "meta": {
    "current_page": 1,
    "total_count": 42,
    "total_pages": 2
  }
}
```

## Badge Rarity Mapping

Badges are color-coded by rarity:
- **Common**: Grey (`#9e9e9e`)
- **Rare**: Blue (`#2196f3`)
- **Ultimate**: Purple (`#9c27b0`)
- **Legendary**: Orange (`#ff9800`)

The script detects rarity from badge background color classes.

## Displayed Data

### Homepage (Mini Stats)
- Reputation
- Total Badges
- Total Solutions
- Total Tracks

### Dedicated Page (/exercism)
- All stats (4 cards)
- Badge showcase (up to 10, with rarity indicators)
- Tracks progress (up to 6, with exercise counts)
- Recent solutions (up to 5, with stars and comments)

## Update Frequency

Recommended: Weekly or after significant activity

## Troubleshooting

### Script doesn't run
- Check Tampermonkey is enabled
- Verify the URL matches `https://exercism.org/profiles/*`
- Check browser console for errors

### Missing badges
- Badges are scraped from the page - ensure they're visible
- Scroll down to load all badges before running the script
- Some badges may have different DOM structure

### API rate limiting
- Exercism API v2 is public and doesn't require authentication
- No known rate limits for profile endpoints
- If limited, wait 1 minute and retry

### Import fails
- Verify JSON file is in `data_tmp/` directory
- Check JSON syntax with `jq . data_tmp/exercism-data-*.json`
- Ensure `data/exercism.json` is writable

## Data Privacy

- Only public profile data is extracted
- No authentication tokens are included
- Solutions must be published to be visible
- Private/unpublished solutions are not included

## Example Workflow

```bash
# 1. Extract data (visit profile page, click Export button)
# 2. Move file
mv ~/Downloads/exercism-data-20260102-153000.json data_tmp/

# 3. Import (auto-detects latest file)
task import-exercism

# 4. View results
open http://localhost:3000/exercism
```

## Related Files

- `scripts/tampermonkey/exercism-extractor.user.js` - Tampermonkey script
- `scripts/update_exercism_from_json.py` - Import script
- `data_tmp/README.md` - Auto-detection workflow
- `backend/app/main.py` - API endpoints
