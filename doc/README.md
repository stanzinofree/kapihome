# KapiHome Documentation

Documentation for API endpoints, data structures, and integration workflows.

## Contents

- **[API Documentation](api/README.md)** - API endpoint specifications
- **[LinkedIn Data Export](LINKEDIN_DATA_EXPORT.md)** - LinkedIn integration guide
- **[Exercism Data Export](EXERCISM_DATA_EXPORT.md)** - Exercism integration guide

## Data Integration Workflow

1. **Extract**: Use Tampermonkey scripts to extract data from source platforms
2. **Save**: Download JSON files and move to `data_tmp/` directory
3. **Import**: Run `task import-*` commands (auto-detect latest file)
4. **View**: Check results at `http://localhost:3000`

## Available Integrations

### LinkedIn ✅
- **Data**: Stats (4 metrics), Recent Posts (5)
- **Method**: Tampermonkey extractors (stats + posts)
- **Guide**: [LINKEDIN_DATA_EXPORT.md](LINKEDIN_DATA_EXPORT.md)
- **Command**: `task import-stats`, `task import-posts`

### Exercism ✅
- **Data**: Stats, Badges, Tracks, Solutions
- **Method**: Tampermonkey extractor + API v2
- **Guide**: [EXERCISM_DATA_EXPORT.md](EXERCISM_DATA_EXPORT.md)
- **Command**: `task import-exercism`

## Pages

- **/** - Homepage with Bio + Mini stats
- **/linkedin** - Full LinkedIn data (stats + posts)
- **/exercism** - Full Exercism data (badges + tracks + solutions)

## Theme

KapiHome uses the **OKLCH Cyberpunk theme** from shadcn with dual light/dark modes:
- Toggle button in header (saves to localStorage)
- Auto-detects system preference on first visit
- OKLCH color space for better contrast and color perception

## Development

See main [README.md](../README.md) for development setup and commands.
