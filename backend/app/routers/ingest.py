from fastapi import APIRouter

from app.db import supabase
from app.models import IngestResult
from app.services.rss_fetcher import fetch_all_sources
from app.services.vader_scorer import score_articles_batch
from app.services.aggregator import compute_daily_aggregation

router = APIRouter()


@router.post("/ingest/run", response_model=IngestResult)
async def run_pipeline():
    # 1. Fetch RSS
    raw_articles = fetch_all_sources()
    articles_fetched = len(raw_articles)

    # 2. Insert into Supabase (ON CONFLICT DO NOTHING via upsert)
    inserted = 0
    for article in raw_articles:
        row = article.model_dump()
        if row.get("published_at"):
            row["published_at"] = row["published_at"].isoformat()
        try:
            result = supabase.table("articles").upsert(
                row, on_conflict="url", ignore_duplicates=True
            ).execute()
            if result.data:
                inserted += 1
        except Exception as e:
            print(f"Insert error for {article.url}: {e}")

    # 3. Score unscored articles
    unscored = (
        supabase.table("articles")
        .select("id, title, summary")
        .is_("sentiment_score", "null")
        .limit(50)
        .execute()
    )

    scored_count = 0
    if unscored.data:
        scored = score_articles_batch(unscored.data)
        for article in scored:
            if article.get("sentiment_score") is not None:
                supabase.table("articles").update({
                    "sentiment_score": article["sentiment_score"],
                    "sentiment_label": article["sentiment_label"],
                    "raw_response": article.get("raw_response"),
                }).eq("id", article["id"]).execute()
                scored_count += 1

    # 4. Aggregate
    agg_ok = compute_daily_aggregation()

    return IngestResult(
        articles_fetched=articles_fetched,
        articles_inserted=inserted,
        articles_scored=scored_count,
        aggregation_updated=agg_ok,
    )
