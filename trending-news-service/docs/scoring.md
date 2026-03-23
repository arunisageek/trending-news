# Scoring

Each raw event contributes:

```text
event_weight * recency_decay
```

Weights:
- view = 1
- click = 3
- bookmark = 4
- share = 5

Recency:
```text
exp(- age_hours / decay_hours)
```

Final score:
```text
sum(event contributions) + 0.25 * relevance_score + 0.15 * freshness_boost
```

Neighbor buckets are blended at read time with a multiplier of `0.8`.
