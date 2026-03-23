# API

## GET /health

Returns service health.

## POST /api/v1/events

Creates a raw user event.

### Body
```json
{
  "article_id": "uuid",
  "event_type": "click",
  "user_lat": 28.6139,
  "user_lon": 77.2090,
  "user_id": "u-1"
}
```

## POST /api/v1/events/simulate?count=100

Creates simulated events for local demos.

## GET /api/v1/trending?lat=28.6139&lon=77.2090&limit=5

Returns the top trending articles near the provided location.
