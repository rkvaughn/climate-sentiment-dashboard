from pydantic import BaseModel
from datetime import datetime


class ArticleIn(BaseModel):
    source_id: str
    title: str
    url: str
    published_at: datetime | None = None
    summary: str | None = None


class ArticleOut(BaseModel):
    id: str
    source_id: str
    title: str
    url: str
    published_at: datetime | None = None
    summary: str | None = None
    sentiment_score: float | None = None
    sentiment_label: str | None = None


class SentimentScore(BaseModel):
    sentiment_score: float
    sentiment_label: str


class AggregationOut(BaseModel):
    time_window: str
    window_date: str
    avg_score: float
    article_count: int
    min_score: float | None = None
    max_score: float | None = None


class IngestResult(BaseModel):
    articles_fetched: int
    articles_inserted: int
    articles_scored: int
    aggregation_updated: bool
