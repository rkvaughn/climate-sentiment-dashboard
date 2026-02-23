#!/usr/bin/env python3
"""
One-time migration: re-score all articles with the transformer model.

Run from the backend directory:
    python -m scripts.rescore_all
"""
from __future__ import annotations

import sys
from collections import defaultdict
from datetime import date

# Ensure the backend package root is on the path when run directly.
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import supabase
from app.services.transformer_scorer import score_articles_batch
from app.services.aggregator import compute_daily_aggregation

BATCH_SIZE = 50


def fetch_all_articles() -> list[dict]:
    """Fetch every article (id, title, summary, published_at) from Supabase."""
    all_articles: list[dict] = []
    offset = 0
    while True:
        response = (
            supabase.table("articles")
            .select("id, title, summary, published_at")
            .range(offset, offset + BATCH_SIZE - 1)
            .execute()
        )
        batch = response.data or []
        all_articles.extend(batch)
        if len(batch) < BATCH_SIZE:
            break
        offset += BATCH_SIZE
    return all_articles


def update_articles(scored: list[dict]) -> int:
    updated = 0
    for article in scored:
        if article.get("sentiment_score") is None:
            continue
        supabase.table("articles").update({
            "sentiment_score": article["sentiment_score"],
            "sentiment_label": article["sentiment_label"],
            "raw_response": article.get("raw_response"),
        }).eq("id", article["id"]).execute()
        updated += 1
    return updated


def collect_dates(articles: list[dict]) -> set[date]:
    dates: set[date] = set()
    for a in articles:
        pub = a.get("published_at")
        if pub:
            try:
                dates.add(date.fromisoformat(pub[:10]))
            except ValueError:
                pass
    return dates


def main() -> None:
    print("Fetching all articles…")
    articles = fetch_all_articles()
    total = len(articles)
    print(f"  Found {total} articles")

    print("Scoring in batches…")
    updated_total = 0
    all_scored: list[dict] = []

    for i in range(0, total, BATCH_SIZE):
        batch = articles[i: i + BATCH_SIZE]
        scored = score_articles_batch(batch)
        count = update_articles(scored)
        updated_total += count
        all_scored.extend(scored)
        print(f"  [{i + len(batch)}/{total}] updated {count} articles")

    print(f"\nTotal articles updated: {updated_total}")

    affected_dates = collect_dates(all_scored)
    print(f"\nRe-aggregating {len(affected_dates)} date(s)…")
    agg_ok = 0
    for d in sorted(affected_dates):
        ok = compute_daily_aggregation(d)
        if ok:
            agg_ok += 1
            print(f"  {d} ✓")
        else:
            print(f"  {d} — no scored articles for this date")

    print(f"\nDone. Aggregations updated: {agg_ok}/{len(affected_dates)}")


if __name__ == "__main__":
    main()
