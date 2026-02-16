# Climate Sentiment Meter

A dashboard that displays climate news sentiment as a "gas gauge" dial. Fetches articles from RSS feeds, scores them, stores results in Supabase, and displays everything in a React frontend.

## Architecture

```
[RSS Feeds] → [FastAPI pipeline] → [Gemini Flash scorer] → [Supabase Postgres]
                                                                  ↕
                                                        [React + D3.js frontend]
```

- **Backend** (Python/FastAPI): Fetches RSS, scores with Gemini, writes to Supabase
- **Frontend** (React/Vite/D3.js): Reads from Supabase directly via anon key
- **Database** (Supabase): Postgres with RLS — anon SELECT, service_role writes

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Supabase](https://supabase.com) account (free tier)
- [Gemini API key](https://aistudio.google.com/apikey)

## Setup

### 1. Supabase

1. Create a new Supabase project
2. Open the SQL Editor and run `supabase/schema.sql` — this creates tables, RLS policies, and seeds the 4 MVP sources
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
GEMINI_API_KEY=your-gemini-api-key
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
| POST | `/api/ingest/run` | Run full pipeline (fetch → score → aggregate) |
| GET | `/api/sentiment` | Get recent daily aggregations |
| GET | `/api/articles?limit=20` | Get scored articles |

## MVP Sources

| Source | Type | Bias |
|--------|------|------|
| Carbon Brief | Specialized Journalism | Center |
| The Guardian (Environment) | Mainstream Media | Center-Left |
| Inside Climate News | Specialized Journalism | Center-Left |
| Grist | Specialized Journalism | Left |

## Scoring

Sentiment scores range from **-1.0** (alarming) to **+1.0** (hopeful). Score is currently using Vader to  analyzes each article's title and summary, considering whether it covers climate damage/policy failure (negative) or solutions/progress (positive). Future versions will improve the tool by using a tranformer based model that can assess the articles context window better.
