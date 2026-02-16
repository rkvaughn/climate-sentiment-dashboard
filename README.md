# Climate Sentiment Meter

A web dashboard that visualizes climate news sentiment as a "gas gauge" dial. An automated pipeline fetches articles from climate news RSS feeds, scores their sentiment locally with VADER, stores results in Supabase (Postgres), and renders everything in a React + D3.js frontend.

## Architecture

```
[RSS Feeds] --> [FastAPI pipeline] --> [VADER scorer] --> [Supabase Postgres]
                                                                ↕
                                                      [React + D3.js frontend]
```

- **Backend** (Python/FastAPI) — fetches RSS, scores with VADER, writes to Supabase
- **Frontend** (React 19/Vite/D3.js) — reads from Supabase directly via anon key
- **Database** (Supabase) — Postgres with RLS; anon SELECT, service_role writes

## Current Status

The MVP pipeline is **fully operational end-to-end**:

- 84 articles fetched and scored from 4 RSS sources
- Daily sentiment aggregation computed (avg, min, max, article count)
- Frontend renders a D3.js gauge with animated needle and a scored article list
- Pipeline triggered on demand via API or the in-app Refresh button

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, Vite 7, D3.js 7, @supabase/supabase-js |
| Backend | Python 3.13, FastAPI 0.115, feedparser, supabase-py |
| Database | Supabase (Postgres) — free tier |
| Scoring | NLTK VADER (local, rule-based, no API calls) |

## Setup

### 1. Supabase

1. Create a new Supabase project
2. Open the SQL Editor and run `supabase/schema.sql` — creates tables, RLS policies, and seeds the 4 MVP sources
3. Note your **Project URL**, **anon key**, and **service_role key** from Settings > API

### 2. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GEMINI_API_KEY=                # optional — not used by VADER scorer
```

Start the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `.env`:
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8000
```

Start the dev server:
```bash
npm run dev
```

### 4. First Run

Trigger the pipeline to fetch and score articles:

```bash
curl -X POST http://localhost:8000/api/ingest/run
```

Then open http://localhost:5173 to see the dashboard.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Interactive Swagger UI |
| POST | `/api/ingest/run` | Run full pipeline (fetch, score, aggregate) |
| GET | `/api/sentiment` | Recent daily aggregations |
| GET | `/api/articles?limit=20` | Scored articles (most recent first) |

## MVP Sources

| Source | Type | Bias Rating |
|--------|------|-------------|
| Carbon Brief | Specialized Journalism | Center |
| The Guardian (Environment) | Mainstream Media | Center-Left |
| Inside Climate News | Specialized Journalism | Center-Left |
| Grist | Specialized Journalism | Left |

## Sentiment Scoring

### How It Works

Sentiment scores range from **-1.0** (alarming) to **+1.0** (hopeful). The current scorer uses **VADER** (Valence Aware Dictionary and sEntiment Reasoner), a rule-based model from NLTK. VADER looks up words in a hand-curated lexicon of ~7,500 rated terms and applies heuristics for punctuation, capitalization, degree modifiers, negation, and contrastive conjunctions to produce a compound score.

Articles are scored on their title + summary text. The compound score maps directly to the -1.0 to +1.0 range and is bucketed into one of seven labels: `very_negative`, `negative`, `slightly_negative`, `neutral`, `slightly_positive`, `positive`, `very_positive`.

### VADER Limitations

VADER was designed for social media and product reviews, not climate journalism. Key limitations in this domain:

- **No contextual understanding** — scores individual words without grasping framing. A headline like "Native families were promised free solar. Trump took it away." scores positive because "free" and "solar" are positive lexicon entries, even though the article is about a policy reversal.
- **No climate domain knowledge** — terms like "stranded assets", "tipping point", or "net zero" carry no sentiment weight unless they happen to contain general positive/negative words.
- **Shallow negation handling** — simple negation ("not good") is caught, but complex rhetorical structures ("despite record investment, emissions continued to rise") are not.
- **Title bias** — news headlines are often crafted to be neutral or provocative in ways that don't map well to VADER's lexicon assumptions.

For the MVP, VADER proves the pipeline works end-to-end with zero API costs and instant scoring. Accuracy will improve with the transformer upgrade.

### Transformer Upgrade Roadmap

The scorer module (`backend/app/services/vader_scorer.py`) is a drop-in replacement — it implements the same `score_article(title, summary)` and `score_articles_batch(articles)` interface as the original Gemini scorer. Upgrading to a transformer model requires:

1. **Choose a model** — `cardiffnlp/twitter-roberta-base-sentiment-latest` (Cardiff NLP / HuggingFace) is the leading candidate. It's a fine-tuned RoBERTa model trained on ~124M tweets with 3-class sentiment. Alternatively, a climate-specific fine-tune could be explored.
2. **Create `transformer_scorer.py`** — same interface, using HuggingFace `transformers` + `torch`. Map the model's 3-class output (negative/neutral/positive) to the -1.0 to +1.0 scale using softmax probabilities.
3. **Swap the import** in `backend/app/routers/ingest.py` — one line change.
4. **Dependency cost** — `transformers` + `torch` adds ~2GB to the install. Consider ONNX Runtime for lighter inference in production.

## Roadmap

| Feature | Priority | Notes |
|---------|----------|-------|
| ~~Replace Gemini with local NLP~~ | ~~P0~~ | Done (VADER) |
| Upgrade to transformer scorer | P1 | See above |
| Weekly/monthly/yearly gauges | P1 | Add time_window values + frontend tabs |
| Trend line graphs (D3.js) | P1 | Needs data accumulation over time |
| Category filter (physical/transition risk) | P2 | Keyword-based article categorization |
| Scheduled cron for pipeline | P2 | Railway cron or pg_cron |
| Source weighting (PageRank) | P2 | See `docs/gemini_pagerank_psuedocode.py` |
| Historical trend storage from Jan 2026 | P2 | Per methodology doc |
| Social media toggle | P3 | Add Twitter/Reddit sources |
| User URL suggestion | P3 | Form + backend ingestion |
| Auth + user preferences | P3 | |
| Docker + deployment | P3 | Vercel (frontend) + Railway (backend) |

## Local Dev

```bash
# Terminal 1 — Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev

# Trigger pipeline
curl -X POST http://localhost:8000/api/ingest/run

# Open dashboard
open http://localhost:5173
```
