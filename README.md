# Trending News Service

A small standalone backend service for the **bonus API** in the Software Engineer task.

This service does one thing well:

- loads articles into a database
- simulates user engagement events near locations
- computes a **location-aware trending score**
- serves `GET /api/v1/trending?lat=...&lon=...&limit=...`
- caches results by **location bucket** for fast reads

---

## What problem this solves

The task’s bonus API asks for a system that can:

- simulate a stream of user activity events on articles
- define an event model
- compute a trending score using:
  - interaction volume/type
  - recency
  - geographic relevance
- expose a `GET /trending` endpoint
- use caching based on geographic segmentation

This repo is a focused implementation of exactly that.

---

## 60-second mental model

Think of the system like this:

1. **Articles** already exist in the database.
2. Users generate events like `view`, `click`, `share`, `bookmark`.
3. Each event is tied to:
   - an article
   - a timestamp
   - a user location
4. User locations are converted into **location buckets** using geohash.
5. A background job periodically computes **trending scores** for each `(bucket, article)` pair.
6. The API reads the top articles for the caller’s bucket and returns them.
7. Results are cached in Redis by bucket to reduce repeated computation.

---

## Main features

- FastAPI-based REST service
- PostgreSQL for persistent storage
- Redis for caching trending feeds
- SQLAlchemy ORM + Alembic migrations
- background jobs for:
  - loading articles
  - simulating events
  - recomputing trending scores
- tests for the core scoring and API behavior

---

## Project structure

```text
trending-news-service/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── deps.py
│   │   ├── errors.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── trending.py
│   │       └── events.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── constants.py
│   ├── db/
│   │   ├── session.py
│   │   ├── base.py
│   │   ├── models/
│   │   │   ├── article.py
│   │   │   ├── user_event.py
│   │   │   └── trending_score.py
│   │   └── repositories/
│   │       ├── article_repository.py
│   │       ├── event_repository.py
│   │       └── trending_repository.py
│   ├── schemas/
│   │   ├── article.py
│   │   ├── event.py
│   │   ├── trending_request.py
│   │   ├── trending_response.py
│   │   └── error.py
│   ├── services/
│   │   ├── ingestion/
│   │   │   └── article_ingestion_service.py
│   │   ├── events/
│   │   │   ├── event_simulator_service.py
│   │   │   └── event_ingestion_service.py
│   │   ├── geo/
│   │   │   ├── bucket_service.py
│   │   │   └── distance_service.py
│   │   ├── ranking/
│   │   │   └── trending_score_service.py
│   │   └── cache/
│   │       └── cache_service.py
│   ├── jobs/
│   │   ├── load_articles_job.py
│   │   ├── simulate_events_job.py
│   │   └── recompute_trending_job.py
│   └── utils/
│       ├── datetime_utils.py
│       ├── geohash_utils.py
│       └── json_utils.py
├── migrations/
├── scripts/
├── tests/
├── docs/
├── data/
├── requirements.txt
├── docker-compose.yml
└── README.md
