# Climate Sentiment Meter

A dashboard that shows how climate news is framed — **risk vs. opportunity** — as a "gas gauge" dial. A daily GitHub Actions job fetches articles from 15 climate news RSS feeds, scores each one with [ClimateBERT](https://huggingface.co/climatebert/distilroberta-base-climate-sentiment), commits the results as JSON, and redeploys the static React + D3.js site to GitHub Pages.

**Live:** https://rkvaughn.github.io/climate-sentiment-dashboard/

## Architecture

```
[RSS feeds] → GitHub Actions: backend/pipeline.py → ClimateBERT → frontend/public/data/*.json (committed)
                                                                        ↓
                                                     GitHub Pages: React + D3.js reads data/latest.json
```

No database, server, or API keys — everything runs on GitHub's free tier for public repos.

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, Vite 7, D3.js 7 |
| Pipeline | Python 3.13, feedparser, Hugging Face Transformers, PyTorch (CPU) |
| Model | `climatebert/distilroberta-base-climate-sentiment` |
| Data | JSON files versioned in this repo |
| Hosting / scheduling | GitHub Pages, GitHub Actions |

## Scoring

ClimateBERT classifies each article's headline + RSS summary as **risk**, **neutral**, or **opportunity**. The dashboard groups articles by their most probable class, scores each as `P(opportunity) − P(risk)` (−1 to +1), and shows the daily average on the gauge. See the "About the model" section on the dashboard and [PROJECT_STATE.md](PROJECT_STATE.md) for details and caveats.

## Local development

```bash
# Generate data (optional — committed data already exists)
python3 -m venv .venv && .venv/bin/pip install -r backend/requirements.txt
.venv/bin/python backend/pipeline.py

# Run the dashboard
cd frontend && npm install && npm run dev
```

## Roadmap

| Feature | Priority | Notes |
|---------|----------|-------|
| Weekly/monthly/yearly gauges | P1 | `aggregations.json` already has daily history |
| Trend line graphs (D3.js) | P1 | Read `aggregations.json` |
| Word cloud by class | P2 | See `BACKLOG.md` |
| Category filter (physical/transition risk) | P2 | Keyword-based categorization |
| Source weighting (PageRank) | P2 | See `docs/gemini_pagerank_psuedocode.py` |
| Social media toggle | P3 | Add Twitter/Reddit sources |
