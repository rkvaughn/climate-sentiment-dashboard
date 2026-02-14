from datetime import date

from app.db import supabase


def compute_daily_aggregation(target_date: date | None = None) -> bool:
    if target_date is None:
        target_date = date.today()

    date_str = target_date.isoformat()

    # Query articles for this date with scores
    response = (
        supabase.table("articles")
        .select("sentiment_score")
        .not_.is_("sentiment_score", "null")
        .gte("published_at", f"{date_str}T00:00:00Z")
        .lt("published_at", f"{date_str}T23:59:59Z")
        .execute()
    )

    articles = response.data
    if not articles:
        return False

    scores = [a["sentiment_score"] for a in articles]

    agg = {
        "time_window": "daily",
        "window_date": date_str,
        "avg_score": round(sum(scores) / len(scores), 4),
        "article_count": len(scores),
        "min_score": min(scores),
        "max_score": max(scores),
    }

    # Upsert
    supabase.table("sentiment_aggregations").upsert(
        agg, on_conflict="time_window,window_date"
    ).execute()

    return True
