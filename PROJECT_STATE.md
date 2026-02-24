# Climate Sentiment Meter — Project State

**Last updated:** February 2026
**Live:** https://rkvaughn.github.io/climate-sentiment-dashboard/
**Repo:** https://github.com/rkvaughn/climate-sentiment-dashboard

---

## What It Does

A dashboard that aggregates climate news from 15 RSS sources, scores each article's sentiment with a RoBERTa transformer model, and visualizes the daily average as an animated D3.js gauge dial. Articles are grouped by sentiment category (Negative / Neutral / Positive) in a three-column layout.

---

## Architecture

### Frontend (React + Vite → GitHub Pages)
- Reads directly from Supabase — no backend server
- `SentimentGauge.jsx` — semi-circular D3.js gauge, color-coded from red (alarming) to green (hopeful)
- `ArticleList.jsx` — three-column layout: Negative | Neutral | Positive, each with colored header and per-article score badge
- `Header.jsx` — title, subtitle, last-updated date
- Hooks: `useSentiment` (daily aggregation), `useArticles` (30 most recent scored articles)
- Deployed via GitHub Actions on every push to `main`

### Backend (Python pipeline script — local cron)
- `backend/pipeline.py` — self-contained script, no server
- **Step 1 — Fetch:** Parses all active RSS feeds in `app/data/sources.json`, upserts new articles into Supabase (deduplicates on URL)
- **Step 2 — Score:** Scores up to 50 unscored articles per run using `cardiffnlp/twitter-roberta-base-sentiment-latest`; stores `sentiment_score` (P_pos − P_neg, range −1 to +1), `sentiment_label` (7-class), and `raw_response`
- **Step 3 — Aggregate:** Computes avg/min/max score for articles published today, upserts into `sentiment_aggregations`
- Cron: `0 8 * * *` (8 AM daily), logs to `~/logs/climate-pipeline.log`
- Virtual env: `.venv/` at project root

### Data (Supabase / Postgres)
- `articles` table: `id`, `source_id`, `title`, `url`, `published_at`, `summary`, `sentiment_score`, `sentiment_label`, `raw_response`
- `sentiment_aggregations` table: `time_window`, `window_date`, `avg_score`, `article_count`, `min_score`, `max_score`
- Supabase project: `htcftmhqjpgsrcrnfbwy`

---

## Sources (15)
Carbon Brief, The Guardian, Inside Climate News, Grist, Columbia Climate School, Sabin Center, Yale Climate Connections, Canary Media, Climate Home News, Mongabay, DeSmog, Utility Dive, CleanTechnica, The Conversation, Google News Climate

---

## Tech Stack
- **Frontend:** React, Vite, D3.js, Supabase JS client
- **Backend:** Python, feedparser, Hugging Face Transformers (RoBERTa), PyTorch, Supabase Python client
- **Data:** Supabase (Postgres)
- **Deploy:** GitHub Pages (frontend), local cron (pipeline)

---

## Sentiment Scoring
- Model: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Score: `P_positive − P_negative` (range −1 to +1)
- 7-class label mapping:
  - `≥ 0.60` → very_positive
  - `≥ 0.20` → positive
  - `≥ 0.05` → slightly_positive
  - `> −0.05` → neutral
  - `> −0.20` → slightly_negative
  - `> −0.60` → negative
  - `≤ −0.60` → very_negative
- Display tiers: Negative (score ≤ −0.2), Neutral (−0.2 to 0.2), Positive (≥ 0.2)

---

## Key Files
```
backend/
  pipeline.py              # Main cron script
  requirements.txt         # feedparser, transformers, torch, supabase, python-dotenv
  .env                     # SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (gitignored)
  .env.example
  README.md                # Setup and cron instructions
  app/data/sources.json    # 15 RSS source definitions

frontend/
  src/
    components/
      Dashboard.jsx
      Header.jsx
      SentimentGauge.jsx
      ArticleList.jsx
    hooks/
      useSentiment.js
      useArticles.js
    lib/supabase.js
  .env                     # VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY (gitignored)

docs/
  sentiment_scoring_methodology.md
  vader_vs_transformer_scoring_analysis.md
  climate_sentiment_meter_project_plan.md
```

---

## What Was Removed
- FastAPI server (`app/main.py`, routers, services) — replaced by `pipeline.py`
- VADER scorer — replaced by RoBERTa transformer
- Gemini scorer — unused, removed
- Refresh button — pipeline runs on cron, not on-demand from UI

---

## Documentation
- [Sentiment Scoring Methodology](docs/sentiment_scoring_methodology.md)
- [VADER vs. Transformer Analysis](docs/vader_vs_transformer_scoring_analysis.md)
- [Project Plan](docs/climate_sentiment_meter_project_plan.md)
