#!/usr/bin/env bash
set -euo pipefail

alembic upgrade head
python scripts/load_articles.py --file data/raw/news_data.json
python scripts/seed_events.py --count 200
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
