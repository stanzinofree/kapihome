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

## Future Endpoints

Microcard and scraper endpoints will be documented as they are developed.
