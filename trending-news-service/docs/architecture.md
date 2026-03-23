# Architecture

## Components

1. **Article ingestion**
   - loads the provided JSON array into the `articles` table

2. **Event ingestion**
   - accepts explicit user events or generates demo events
   - stores them in `user_events`

3. **Trending computation**
   - periodically reads recent events
   - computes a decayed score per `(bucket_id, article_id)`
   - stores results in `trending_scores`

4. **Read API**
   - `GET /api/v1/trending`
   - derives a geographic bucket from `lat/lon`
   - reads the bucket and neighboring buckets
   - merges and ranks results
   - caches the final response

## Why this matches the task

The task asks for:
- a simulated event stream
- a candidate-designed event model
- trending logic based on interaction volume/type, recency, and geography
- a `GET /trending` endpoint
- location-based caching

This repo isolates exactly those concerns.
