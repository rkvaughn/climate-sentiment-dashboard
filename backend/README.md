# Climate Sentiment Pipeline

Standalone script that fetches climate news RSS feeds, scores new articles with ClimateBERT (`climatebert/distilroberta-base-climate-sentiment`), and writes the static JSON the dashboard reads from `frontend/public/data/`.

It runs daily on GitHub Actions (`.github/workflows/pipeline.yml`), which commits the updated data and redeploys the site. No credentials are needed.

## What it does

1. **Fetch** — parses active feeds in `app/data/sources.json`; adds articles whose URL isn't already stored.
2. **Score** — scores every article not yet scored by the current model (`MODEL_NAME`), storing class probabilities, the most probable class, and `P(opportunity) − P(risk)`.
3. **Write** — `articles/YYYY-MM.json`, `aggregations.json` (daily averages by UTC date), and `latest.json`.

## Run manually on GitHub

Actions tab → **Daily sentiment pipeline** → **Run workflow**.

## Run locally

```bash
cd ~/Projects/climate-sentiment-dashboard
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python backend/pipeline.py
```

The first run downloads the model from Hugging Face and caches it. Local runs modify `frontend/public/data/`; commit those changes or discard them so they don't conflict with the scheduled bot commits.
