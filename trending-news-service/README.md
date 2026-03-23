# Trending News Service

A standalone FastAPI service for the bonus "Trending News by Location" API from the contextual news retrieval task. It focuses on:

- loading article JSON into a database
- simulating user engagement events tied to article and user locations
- computing a location-aware trending score
- serving `GET /api/v1/trending`
- caching feeds by geographic bucket

The task asks for a simulated user event stream, a computed trending score that accounts for interaction volume/type, recency, and geography, plus location-based caching and a `GET /trending` endpoint. This repo is built around those requirements.

## Features

- FastAPI API with versioned endpoints
- SQLAlchemy ORM models
- Redis cache with in-memory fallback
- periodic recomputation support via CLI jobs
- article ingestion from JSON
- event simulation for local demos
- test suite for core ranking and API behavior
- Alembic migrations

## API

### Health
```bash
curl http://localhost:8000/health
```

### Create a user event
```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "article_id": "replace-with-article-id",
    "event_type": "click",
    "user_lat": 28.6139,
    "user_lon": 77.2090,
    "user_id": "u-1"
  }'
```

### Simulate events
```bash
curl -X POST "http://localhost:8000/api/v1/events/simulate?count=100"
```

### Fetch trending news
```bash
curl "http://localhost:8000/api/v1/trending?lat=28.6139&lon=77.2090&limit=5"
```

## Local setup

### 1) Create env file
```bash
cp .env.example .env
```

### 2) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Start Postgres and Redis
```bash
docker compose up -d postgres redis
```

### 4) Run migrations
```bash
alembic upgrade head
```

### 5) Load article data
Place your task dataset at `data/raw/news_data.json`, then run:

```bash
python scripts/load_articles.py --file data/raw/news_data.json
```

### 6) Start the API
```bash
uvicorn app.main:app --reload
```

## Jobs

### Simulate demo events
```bash
python scripts/seed_events.py --count 200
```

### Recompute trending scores
```bash
python -m app.jobs.recompute_trending_job
```

## Configuration notes

- `DATABASE_URL` defaults to SQLite for convenience if not set.
- For production-like runs, set PostgreSQL in `.env`.
- `REDIS_URL` is optional; if missing or unavailable, the service uses an in-memory TTL cache.
- Bucketing uses a fixed geographic grid with configurable cell size in km.

## Project layout

- `app/api` HTTP layer
- `app/db` ORM models and repositories
- `app/services` ingestion, simulation, geo, ranking, cache
- `app/jobs` CLI jobs
- `scripts` helper scripts
- `tests` test suite

## Suggested production hardening

- add authentication for event ingestion
- move event ingestion to a queue for higher throughput
- run recomputation on a scheduler
- add observability, tracing, and rate limiting
- switch to async DB/caching if throughput demands it
