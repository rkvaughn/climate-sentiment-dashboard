# Climate Sentiment Meter — Full Project Context

## What This Is

A web dashboard that displays climate news sentiment as a "gas gauge" dial. An automated pipeline fetches articles from climate news RSS feeds, scores each article's sentiment, stores results in Supabase (Postgres), and a React frontend renders a D3.js gauge plus an article list.

**Current status**: MVP scaffolding complete. Backend pipeline fetches RSS and inserts articles into Supabase. Sentiment scoring is **blocked** — the Gemini API key hit quota limits. We're actively researching **free local (non-API) sentiment analysis** alternatives to replace Gemini.

---

## Architecture

```
[RSS Feeds] → [FastAPI rss_fetcher] → [Sentiment Scorer] → [Supabase Postgres]
                                                                  ↕
                                                        [React via Supabase JS client]
                                                           ↕            ↕
                                                    [ArticleList]  [SentimentGauge]
```

- Frontend reads directly from Supabase (anon key + RLS for SELECT)
- Backend writes with service_role key (bypasses RLS)
- Pipeline triggered via `POST /api/ingest/run`

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, Vite 7, D3.js 7, @supabase/supabase-js |
| Backend | Python 3.13, FastAPI 0.115, feedparser, supabase-py |
| Database | Supabase (Postgres) — free tier |
| Scoring | **Currently**: google-generativeai (Gemini 2.0 Flash) — **needs replacement** |
| Deployment | Not yet deployed. Plan: Vercel (frontend), Railway (backend) |

---

## Folder Structure

```
climate-sentiment-dashboard/
├── context.md                     ← This file
├── README.md                      ← Setup instructions
├── .gitignore
├── docs/
│   ├── climate_sentiment_meter_project_plan.md   ← Full project plan (phases 1-5)
│   ├── sentiment_scoring_methodology.md          ← Scoring methodology doc
│   ├── detailed_mockup_description.md            ← UI mockup spec
│   └── gemini_pagerank_psuedocode.py             ← Future PageRank weighting idea
├── supabase/
│   └── schema.sql                 ← Tables, indexes, RLS policies, seed data
├── backend/
│   ├── requirements.txt           ← Python deps
│   ├── .env.example               ← Template for env vars
│   ├── .env                       ← Active env (gitignored, has real keys)
│   ├── .venv/                     ← Python virtual env (installed, working)
│   └── app/
│       ├── __init__.py
│       ├── main.py                ← FastAPI app, CORS, health check, router mounts
│       ├── config.py              ← pydantic-settings (reads .env)
│       ├── db.py                  ← Supabase client init (service_role key)
│       ├── models.py              ← Pydantic models (ArticleIn/Out, SentimentScore, etc.)
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── ingest.py          ← POST /api/ingest/run — full pipeline
│       │   ├── sentiment.py       ← GET /api/sentiment — recent aggregations
│       │   └── articles.py        ← GET /api/articles?limit=N — scored articles
│       ├── services/
│       │   ├── __init__.py
│       │   ├── rss_fetcher.py     ← feedparser RSS ingestion
│       │   ├── gemini_scorer.py   ← Gemini Flash sentiment scoring (NEEDS REPLACEMENT)
│       │   └── aggregator.py      ← Daily avg/min/max aggregation
│       └── data/
│           └── sources.json       ← 4 MVP sources (JSON)
└── frontend/
    ├── package.json               ← React 19 + D3 + Supabase
    ├── package-lock.json
    ├── vite.config.js
    ├── index.html
    ├── .env.example
    ├── .env                       ← Active env (gitignored, has real keys)
    ├── public/
    │   └── vite.svg
    └── src/
        ├── main.jsx               ← React entry point
        ├── App.jsx                ← Renders <Dashboard />
        ├── index.css              ← Global styles (dark slate theme)
        ├── App.css                ← Component styles
        ├── lib/
        │   └── supabase.js        ← Supabase client (anon key)
        ├── hooks/
        │   ├── useSentiment.js    ← Reads latest daily aggregation
        │   └── useArticles.js     ← Reads scored articles
        └── components/
            ├── Dashboard.jsx      ← Main layout, wires hooks to components
            ├── SentimentGauge.jsx ← D3.js semi-circular gauge with animated needle
            ├── ArticleList.jsx    ← Articles with colored sentiment dots
            ├── Header.jsx         ← Title + last-updated date
            └── RefreshButton.jsx  ← Triggers POST /api/ingest/run, refreshes data
```

---

## Supabase Schema (3 tables)

**Project**: `htcftmhqjpgsrcrnfbwy` at `https://htcftmhqjpgsrcrnfbwy.supabase.co`

### `sources` — Reference data (4 rows seeded)
| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | e.g. `carbon_brief` |
| name | TEXT | Display name |
| url | TEXT | Source homepage |
| feed_url | TEXT | RSS feed URL |
| source_type | TEXT | e.g. "Specialized Journalism" |
| bias_rating | TEXT | e.g. "Center", "Center-Left" |
| active | BOOLEAN | Default true |

### `articles` — One row per fetched article
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | Auto-generated |
| source_id | TEXT FK→sources | |
| title | TEXT | |
| url | TEXT UNIQUE | Dedup key |
| published_at | TIMESTAMPTZ | |
| summary | TEXT | HTML-stripped, max 500 chars |
| sentiment_score | REAL | -1.0 to 1.0 (NULL if unscored) |
| sentiment_label | TEXT | e.g. "negative", "slightly_positive" |
| raw_response | JSONB | Raw scorer output |

### `sentiment_aggregations` — Pre-computed daily scores
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| time_window | TEXT | "daily" (MVP), future: weekly/monthly/yearly |
| window_date | DATE | |
| avg_score | REAL | |
| article_count | INT | |
| min_score | REAL | |
| max_score | REAL | |
| UNIQUE | | (time_window, window_date) |

**RLS**: anon gets SELECT on all. service_role gets full access.

**Current state**: 74 articles inserted, 0 scored.

---

## Key Source Files — Full Code

### backend/app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ingest, sentiment, articles

app = FastAPI(title="Climate Sentiment Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api")
app.include_router(sentiment.router, prefix="/api")
app.include_router(articles.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### backend/app/config.py
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str
    gemini_api_key: str

    model_config = {"env_file": ".env"}


settings = Settings()
```

### backend/app/db.py
```python
from supabase import create_client, Client
from app.config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
```

### backend/app/models.py
```python
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
```

### backend/app/services/rss_fetcher.py
```python
import json
from datetime import datetime, timezone
from pathlib import Path

import feedparser
from app.models import ArticleIn


def _parse_date(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        from time import mktime
        return datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
    return None


def _get_summary(entry) -> str | None:
    if hasattr(entry, "summary") and entry.summary:
        import re
        return re.sub(r"<[^>]+>", "", entry.summary).strip()[:500]
    return None


def fetch_feed(source_id: str, feed_url: str) -> list[ArticleIn]:
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        link = entry.get("link")
        title = entry.get("title")
        if not link or not title:
            continue
        articles.append(ArticleIn(
            source_id=source_id,
            title=title.strip(),
            url=link.strip(),
            published_at=_parse_date(entry),
            summary=_get_summary(entry),
        ))
    return articles


def load_sources() -> list[dict]:
    sources_path = Path(__file__).parent.parent / "data" / "sources.json"
    with open(sources_path) as f:
        data = json.load(f)
    return [s for s in data["sources"] if s.get("active", True)]


def fetch_all_sources() -> list[ArticleIn]:
    sources = load_sources()
    all_articles = []
    for source in sources:
        try:
            articles = fetch_feed(source["id"], source["feed_url"])
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error fetching {source['id']}: {e}")
    return all_articles
```

### backend/app/services/gemini_scorer.py — NEEDS REPLACEMENT
```python
import asyncio
import json
import re

import google.generativeai as genai
from app.config import settings
from app.models import SentimentScore

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT_TEMPLATE = """Analyze the climate news sentiment of this article.

Title: {title}
Summary: {summary}

Rate the sentiment on a scale from -1.0 (extremely negative/alarming) to 1.0 (extremely positive/hopeful).
Consider: Is this about climate damage, policy failure, or worsening conditions (negative)?
Or about solutions, progress, adaptation success, or policy wins (positive)?
Neutral/factual reporting with no strong valence should be near 0.

Respond with ONLY valid JSON, no markdown:
{{"sentiment_score": <float between -1.0 and 1.0>, "sentiment_label": "<one of: very_negative, negative, slightly_negative, neutral, slightly_positive, positive, very_positive>"}}"""


def _parse_response(text: str) -> SentimentScore | None:
    try:
        data = json.loads(text.strip())
        return SentimentScore(**data)
    except (json.JSONDecodeError, ValueError):
        pass
    score_match = re.search(r'"sentiment_score"\s*:\s*([-\d.]+)', text)
    label_match = re.search(r'"sentiment_label"\s*:\s*"([^"]+)"', text)
    if score_match and label_match:
        return SentimentScore(
            sentiment_score=float(score_match.group(1)),
            sentiment_label=label_match.group(1),
        )
    return None


async def score_article(title: str, summary: str | None) -> SentimentScore | None:
    prompt = PROMPT_TEMPLATE.format(
        title=title,
        summary=summary or "No summary available.",
    )
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            result = _parse_response(response.text)
            if result:
                return result
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = 5 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"Gemini error: {e}")
                break
    return None


async def score_articles_batch(articles: list[dict]) -> list[dict]:
    """Score a list of articles, adding sentiment_score and sentiment_label fields."""
    scored = []
    for article in articles:
        result = await score_article(article["title"], article.get("summary"))
        if result:
            article["sentiment_score"] = result.sentiment_score
            article["sentiment_label"] = result.sentiment_label
            article["raw_response"] = result.model_dump()
        scored.append(article)
        await asyncio.sleep(0.5)
    return scored
```

### backend/app/services/aggregator.py
```python
from datetime import date

from app.db import supabase


def compute_daily_aggregation(target_date: date | None = None) -> bool:
    if target_date is None:
        target_date = date.today()

    date_str = target_date.isoformat()

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

    supabase.table("sentiment_aggregations").upsert(
        agg, on_conflict="time_window,window_date"
    ).execute()

    return True
```

### backend/app/routers/ingest.py
```python
from fastapi import APIRouter

from app.db import supabase
from app.models import IngestResult
from app.services.rss_fetcher import fetch_all_sources
from app.services.gemini_scorer import score_articles_batch
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
        scored = await score_articles_batch(unscored.data)
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
```

### backend/app/routers/sentiment.py
```python
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
```

### backend/app/routers/articles.py
```python
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
```

### backend/app/data/sources.json
```json
{
  "metadata": {
    "description": "MVP climate news sources for sentiment analysis",
    "last_updated": "2026-02-14",
    "version": "1.0"
  },
  "sources": [
    {
      "id": "carbon_brief",
      "name": "Carbon Brief",
      "url": "https://www.carbonbrief.org",
      "feed_url": "https://www.carbonbrief.org/feed",
      "source_type": "Specialized Journalism",
      "bias_rating": "Center",
      "active": true
    },
    {
      "id": "guardian_environment",
      "name": "The Guardian (Environment)",
      "url": "https://www.theguardian.com/us/environment",
      "feed_url": "https://www.theguardian.com/us/environment/rss",
      "source_type": "Mainstream Media",
      "bias_rating": "Center-Left",
      "active": true
    },
    {
      "id": "inside_climate_news",
      "name": "Inside Climate News",
      "url": "https://insideclimatenews.org",
      "feed_url": "https://insideclimatenews.org/feed/",
      "source_type": "Specialized Journalism",
      "bias_rating": "Center-Left",
      "active": true
    },
    {
      "id": "grist",
      "name": "Grist",
      "url": "https://grist.org",
      "feed_url": "https://grist.org/feed/",
      "source_type": "Specialized Journalism",
      "bias_rating": "Left",
      "active": true
    }
  ]
}
```

### frontend/src/lib/supabase.js
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### frontend/src/hooks/useSentiment.js
```javascript
import { useState, useEffect, useCallback } from 'react'
import { supabase } from '../lib/supabase'

export function useSentiment() {
  const [sentiment, setSentiment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchSentiment = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data, error: sbError } = await supabase
        .from('sentiment_aggregations')
        .select('*')
        .eq('time_window', 'daily')
        .order('window_date', { ascending: false })
        .limit(1)
        .single()

      if (sbError && sbError.code !== 'PGRST116') throw sbError
      setSentiment(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSentiment()
  }, [fetchSentiment])

  return { sentiment, loading, error, refetch: fetchSentiment }
}
```

### frontend/src/hooks/useArticles.js
```javascript
import { useState, useEffect, useCallback } from 'react'
import { supabase } from '../lib/supabase'

export function useArticles(limit = 20) {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchArticles = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data, error: sbError } = await supabase
        .from('articles')
        .select('id, source_id, title, url, published_at, sentiment_score, sentiment_label')
        .not('sentiment_score', 'is', null)
        .order('published_at', { ascending: false })
        .limit(limit)

      if (sbError) throw sbError
      setArticles(data || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    fetchArticles()
  }, [fetchArticles])

  return { articles, loading, error, refetch: fetchArticles }
}
```

### frontend/src/components/Dashboard.jsx
```jsx
import Header from './Header'
import SentimentGauge from './SentimentGauge'
import ArticleList from './ArticleList'
import RefreshButton from './RefreshButton'
import { useSentiment } from '../hooks/useSentiment'
import { useArticles } from '../hooks/useArticles'

export default function Dashboard() {
  const { sentiment, loading: sentLoading, refetch: refetchSentiment } = useSentiment()
  const { articles, loading: artLoading, refetch: refetchArticles } = useArticles(30)

  function handleRefreshComplete() {
    refetchSentiment()
    refetchArticles()
  }

  const score = sentiment?.avg_score ?? null
  const articleCount = sentiment?.article_count ?? null
  const lastUpdated = sentiment?.window_date ?? null

  return (
    <div className="dashboard">
      <Header lastUpdated={lastUpdated} />

      <div className="gauge-section">
        {sentLoading ? (
          <p className="loading-text">Loading sentiment data...</p>
        ) : score !== null ? (
          <SentimentGauge score={score} articleCount={articleCount} />
        ) : (
          <p className="loading-text">No sentiment data yet. Run the pipeline to get started.</p>
        )}
      </div>

      <RefreshButton onComplete={handleRefreshComplete} />

      <ArticleList articles={articles} loading={artLoading} />
    </div>
  )
}
```

### frontend/src/components/SentimentGauge.jsx
```jsx
import { useRef, useEffect } from 'react'
import * as d3 from 'd3'

const WIDTH = 300
const HEIGHT = 180
const MARGIN = 20
const RADIUS = (WIDTH - MARGIN * 2) / 2
const NEEDLE_LENGTH = RADIUS - 15

const LABELS = [
  { angle: -80, text: 'Alarming' },
  { angle: -40, text: 'Negative' },
  { angle: 0, text: 'Neutral' },
  { angle: 40, text: 'Positive' },
  { angle: 80, text: 'Hopeful' },
]

export default function SentimentGauge({ score, articleCount }) {
  const svgRef = useRef()

  useEffect(() => {
    if (score === null || score === undefined) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const g = svg
      .attr('viewBox', `0 0 ${WIDTH} ${HEIGHT}`)
      .append('g')
      .attr('transform', `translate(${WIDTH / 2}, ${HEIGHT - MARGIN})`)

    const arcGen = d3.arc().innerRadius(RADIUS - 30).outerRadius(RADIUS)

    const segments = [
      { start: -90, end: -54, color: '#dc2626' },
      { start: -54, end: -18, color: '#f97316' },
      { start: -18, end: 18, color: '#eab308' },
      { start: 18, end: 54, color: '#84cc16' },
      { start: 54, end: 90, color: '#22c55e' },
    ]

    segments.forEach(({ start, end, color }) => {
      g.append('path')
        .attr(
          'd',
          arcGen({
            startAngle: (start * Math.PI) / 180,
            endAngle: (end * Math.PI) / 180,
          })
        )
        .attr('fill', color)
        .attr('opacity', 0.8)
    })

    LABELS.forEach(({ angle, text }) => {
      const rad = (angle * Math.PI) / 180
      const x = Math.sin(rad) * (RADIUS + 12)
      const y = -Math.cos(rad) * (RADIUS + 12)
      g.append('text')
        .attr('x', x)
        .attr('y', y)
        .attr('text-anchor', 'middle')
        .attr('font-size', '9px')
        .attr('fill', '#94a3b8')
        .text(text)
    })

    const clampedScore = Math.max(-1, Math.min(1, score))
    const targetAngle = clampedScore * 90

    const needle = g
      .append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', 0)
      .attr('y2', -NEEDLE_LENGTH)
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', 2.5)
      .attr('stroke-linecap', 'round')
      .attr('transform', 'rotate(-90)')

    needle
      .transition()
      .duration(1200)
      .ease(d3.easeElasticOut.amplitude(1).period(0.5))
      .attr('transform', `rotate(${targetAngle})`)

    g.append('circle').attr('r', 5).attr('fill', '#e2e8f0')

    g.append('text')
      .attr('y', -30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '24px')
      .attr('font-weight', 'bold')
      .attr('fill', '#f8fafc')
      .text(score.toFixed(2))

    if (articleCount) {
      g.append('text')
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .attr('font-size', '11px')
        .attr('fill', '#94a3b8')
        .text(`${articleCount} articles`)
    }
  }, [score, articleCount])

  return (
    <div className="gauge-container">
      <svg ref={svgRef} />
    </div>
  )
}
```

### frontend/src/components/ArticleList.jsx
```jsx
function sentimentColor(score) {
  if (score <= -0.5) return '#dc2626'
  if (score <= -0.2) return '#f97316'
  if (score <= 0.2) return '#eab308'
  if (score <= 0.5) return '#84cc16'
  return '#22c55e'
}

function sentimentText(label) {
  if (!label) return ''
  return label.replace(/_/g, ' ')
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

const SOURCE_NAMES = {
  carbon_brief: 'Carbon Brief',
  guardian_environment: 'The Guardian',
  inside_climate_news: 'Inside Climate News',
  grist: 'Grist',
}

export default function ArticleList({ articles, loading }) {
  if (loading) return <p className="loading-text">Loading articles...</p>
  if (!articles.length) return <p className="loading-text">No scored articles yet. Try refreshing data.</p>

  return (
    <div className="article-list">
      <h2>Recent Articles</h2>
      <ul>
        {articles.map((article) => (
          <li key={article.id} className="article-item">
            <span
              className="sentiment-dot"
              style={{ backgroundColor: sentimentColor(article.sentiment_score) }}
              title={`${article.sentiment_score?.toFixed(2)} — ${sentimentText(article.sentiment_label)}`}
            />
            <div className="article-info">
              <a href={article.url} target="_blank" rel="noopener noreferrer">
                {article.title}
              </a>
              <span className="article-meta">
                {SOURCE_NAMES[article.source_id] || article.source_id}
                {article.published_at && ` · ${formatDate(article.published_at)}`}
                {article.sentiment_score != null && (
                  <span
                    className="score-badge"
                    style={{ color: sentimentColor(article.sentiment_score) }}
                  >
                    {article.sentiment_score > 0 ? '+' : ''}
                    {article.sentiment_score.toFixed(2)}
                  </span>
                )}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
```

### frontend/src/components/Header.jsx
```jsx
export default function Header({ lastUpdated }) {
  const formattedDate = lastUpdated
    ? new Date(lastUpdated).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  return (
    <header className="header">
      <h1>Climate Sentiment Meter</h1>
      <p className="subtitle">Daily climate news sentiment at a glance</p>
      {formattedDate && (
        <p className="last-updated">Last updated: {formattedDate}</p>
      )}
    </header>
  )
}
```

### frontend/src/components/RefreshButton.jsx
```jsx
import { useState } from 'react'

export default function RefreshButton({ onComplete }) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  async function handleRefresh() {
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch(`${apiUrl}/api/ingest/run`, { method: 'POST' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setResult(
        `Fetched ${data.articles_fetched}, inserted ${data.articles_inserted}, scored ${data.articles_scored}`
      )
      if (onComplete) onComplete()
    } catch (e) {
      setResult(`Error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="refresh-section">
      <button
        className="refresh-button"
        onClick={handleRefresh}
        disabled={loading}
      >
        {loading ? 'Running pipeline...' : 'Refresh Data'}
      </button>
      {result && <p className="refresh-result">{result}</p>}
    </div>
  )
}
```

---

## Environment Variables

### backend/.env
```
SUPABASE_URL=https://htcftmhqjpgsrcrnfbwy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role JWT>
GEMINI_API_KEY=<gemini key — currently quota-blocked>
```

### frontend/.env
```
VITE_SUPABASE_URL=https://htcftmhqjpgsrcrnfbwy.supabase.co
VITE_SUPABASE_ANON_KEY=<anon JWT>
VITE_API_URL=http://localhost:8000
```

---

## What's Working

1. **RSS fetching**: All 4 feeds return articles (74 total on first run)
2. **Supabase writes**: Articles insert with dedup on URL
3. **Supabase reads**: Frontend hooks and backend routes query correctly
4. **Frontend build**: Compiles cleanly (Vite, React 19, D3.js)
5. **Backend venv**: All Python deps installed and importable

## What's Blocked

1. **Sentiment scoring**: Gemini API key returns 429 with `limit: 0` on free tier. Every call fails. The 74 articles in Supabase have `sentiment_score = NULL`.

## Immediate Next Step

**Replace `gemini_scorer.py` with a free local sentiment analysis solution.** Options under consideration:
- VADER (NLTK) — rule-based, fast, no model download
- TextBlob — simple, pattern-based
- Hugging Face transformers locally — e.g. `cardiffnlp/twitter-roberta-base-sentiment-latest` (the Twitter/Cardiff NLP model)
- Flair NLP — Zalando's framework

The scorer interface is: `score_article(title, summary) → SentimentScore(sentiment_score: float, sentiment_label: str)` where score is -1.0 to 1.0 and label is one of `very_negative, negative, slightly_negative, neutral, slightly_positive, positive, very_positive`.

The `score_articles_batch` function loops through articles and calls `score_article` on each. The ingest router calls `score_articles_batch` then writes results back to Supabase.

---

## Backlog (Future Phases)

| Feature | Priority | Notes |
|---------|----------|-------|
| Replace Gemini scorer with local NLP | **P0 — blocking** | See above |
| Weekly/monthly/yearly gauges | P1 | Add more time_window values + frontend tabs |
| Trend line graphs (D3.js) | P1 | Needs data accumulation over time first |
| Category filter (physical/transition risk) | P2 | Keyword-based article categorization |
| Scheduled cron for pipeline | P2 | Railway cron or pg_cron |
| Source weighting (PageRank) | P2 | See `docs/gemini_pagerank_psuedocode.py` |
| Social media toggle | P3 | Add Twitter/Reddit sources |
| User URL suggestion | P3 | Form + backend ingestion |
| Auth + user preferences | P3 | |
| Docker + deployment | P3 | Vercel (FE) + Railway (BE) |
| Historical trend storage from Jan 2026 | P2 | Per methodology doc |
| Add Columbia Climate School source | P1 | Columbia University climate content — need to find RSS/scrape endpoint |
| Add Sabin Center Silencing Science Tracker | P1 | climate.law.columbia.edu — tracks gov't efforts to restrict science. Scrape or RSS TBD |

---

## Local Dev Commands

```bash
# Backend (Terminal 1)
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend && npm run dev

# Trigger pipeline
curl -X POST http://localhost:8000/api/ingest/run

# Then open http://localhost:5173
```

---

## Git State

- **Branch**: `main`
- **Latest commit**: `a5aaadb` — "Initial commit: full MVP scaffolding"
- **Remote**: Not yet pushed to GitHub
