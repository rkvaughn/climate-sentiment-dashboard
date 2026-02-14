from fastapi import APIRouter, Query

from app.db import supabase

router = APIRouter()


@router.get("/articles")
def get_articles(limit: int = Query(default=20, le=100)):
    response = (
        supabase.table("articles")
        .select("id, source_id, title, url, published_at, sentiment_score, sentiment_label")
        .not_.is_("sentiment_score", "null")
        .order("published_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data
