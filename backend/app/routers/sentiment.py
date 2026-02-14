from fastapi import APIRouter

from app.db import supabase

router = APIRouter()


@router.get("/sentiment")
def get_sentiment():
    response = (
        supabase.table("sentiment_aggregations")
        .select("*")
        .order("window_date", desc=True)
        .limit(7)
        .execute()
    )
    return response.data
