# Climate Sentiment Meter — Project State

**Last updated:** 2026-11-07
**Live:** https://rkvaughn.github.io/climate-sentiment-dashboard/
**Repo:** https://github.com/rkvaughn/climate-sentiment-dashboard

---

## What It Does

A dashboard that aggregates climate news from 15 RSS sources, scores each article with **ClimateBERT** (risk / neutral / opportunity), and visualizes the daily average as an animated D3.js gauge. Articles are grouped by ClimateBERT class in a three-column layout, and an "About the model" section explains ClimateBERT with links to its source.

Runs entirely on GitHub (Actions + Pages) — no database, no server, no API keys, $0 to operate.

---

## Architecture

```
GitHub Actions (daily, .github/workflows/pipeline.yml)
  → backend/pipeline.py: fetch RSS → score new articles with ClimateBERT → write JSON
  → commit frontend/public/data/ → call deploy.yml → GitHub Pages
React (static) → fetch data/latest.json
```

### Pipeline (`backend/pipeline.py`)
1. **Fetch** — parses all active feeds in `backend/app/data/sources.json`; new URLs are added (dedup on URL).
2. **Score** — any article whose `model` field isn't the current model is scored, so changing `MODEL_NAME` re-scores the full history automatically.
3. **Write** — monthly article files, daily aggregations, and the `latest.json` snapshot the dashboard reads.

### Workflows
- `pipeline.yml` — schedule `0 8 * * *` (**UTC** on Actions) + manual `workflow_dispatch`. Commits data as `github-actions[bot]`, then calls `deploy.yml` (pushes made with `GITHUB_TOKEN` don't trigger other workflows).
- `deploy.yml` — builds `frontend/` and deploys to Pages; runs on push to `main`, when called by the pipeline, or manually.

### Data (`frontend/public/data/`, versioned in git)
- `latest.json` — `generated_at`, `model`, `sources` (id → name), latest daily `aggregation`, 30 most recent scored `articles`.
- `aggregations.json` — `daily[]`: `window_date`, `avg_score`, `article_count`, `min_score`, `max_score`, `label_counts`.
- `articles/YYYY-MM.json` — every article: `url`, `source_id`, `title`, `published_at`, `summary`, `fetched_at`, `sentiment_score`, `sentiment_label`, `probabilities`, `model`.

### Frontend (React + Vite + D3.js)
- `hooks/useDashboardData.js` — fetches `data/latest.json`
- `SentimentGauge.jsx` — gauge from Risk (−1) to Opportunity (+1)
- `ArticleList.jsx` — Risk | Neutral | Opportunity columns; dot tooltip shows class probabilities
- `ModelInfo.jsx` — ClimateBERT description, limitations, citations, links

---

## Sentiment Scoring
- Model: [`climatebert/distilroberta-base-climate-sentiment`](https://huggingface.co/climatebert/distilroberta-base-climate-sentiment) (Apache 2.0)
- Input: `"{title}. {summary}"` (summary = HTML-stripped RSS summary, first 500 chars), truncated to the model's 512-token limit
- `sentiment_label` = most probable class (`risk` / `neutral` / `opportunity`) — no thresholds
- `sentiment_score` = `P(opportunity) − P(risk)`, range −1 to +1
- Daily aggregate = mean score of scored articles by UTC publication date
- Label mapping verified 2026-11-07 against the first 100 rows of the `climatebert/climate_sentiment` test split: the model config's `id2label` (0 opportunity, 1 neutral, 2 risk) agreed with gold labels on 76/100; the dataset card lists the reverse index order, which does not match the model.

---

## Known Caveats
- ClimateBERT's sentiment head was trained on corporate disclosure paragraphs, not news; headlines with short summaries are least reliable.
- History restarted 2026-11-07 (the old Supabase project was deleted). Days before the first run only include articles still listed in feeds at that time, so early daily aggregates have partial coverage.
- GitHub disables scheduled workflows after 60 days without repository activity; the daily data commits should keep it active — confirm after the first couple of months.

---

## Key Files
```
.github/workflows/pipeline.yml   # Daily fetch/score/commit + deploy
.github/workflows/deploy.yml     # Build + deploy to Pages
backend/pipeline.py              # Pipeline script
backend/requirements.txt         # feedparser, transformers, torch
backend/app/data/sources.json    # 15 RSS source definitions
frontend/public/data/            # Generated data (committed)
frontend/src/components/         # Dashboard, Header, SentimentGauge, ArticleList, ModelInfo
frontend/src/hooks/useDashboardData.js
```

---

## What Was Removed
- Supabase (database deleted by the free tier; replaced by JSON in git) and `@supabase/supabase-js`
- Local cron job (replaced by GitHub Actions)
- `cardiffnlp/twitter-roberta-base-sentiment-latest` scorer and its 7-class threshold labels (replaced by ClimateBERT's 3 classes)
- Earlier: FastAPI server, VADER and Gemini scorers, Refresh button

---

## Documentation
- [Sentiment Scoring Methodology](docs/sentiment_scoring_methodology.md)
- [VADER vs. Transformer Analysis](docs/vader_vs_transformer_scoring_analysis.md) (historical)
- [Project Plan](docs/climate_sentiment_meter_project_plan.md)
