# Climate Sentiment Pipeline

Standalone script that fetches RSS articles from climate news sources, scores them with a RoBERTa sentiment model, writes results to Supabase, and computes a daily aggregation.

## What it does

1. **Fetch** — Parses RSS feeds from `app/data/sources.json` and upserts new articles into the `articles` table.
2. **Score** — Scores up to 50 unscored articles per run using `cardiffnlp/twitter-roberta-base-sentiment-latest`.
3. **Aggregate** — Computes daily avg/min/max sentiment score and upserts into `sentiment_aggregations`.

## Setup

```bash
cd ~/Projects/climate-sentiment-dashboard

# Create virtualenv and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Copy and fill in credentials
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase URL and service role key
```

> **Note:** First run will download the RoBERTa model (~500 MB) from Hugging Face and cache it locally.

## Manual run

```bash
cd ~/Projects/climate-sentiment-dashboard
source .venv/bin/activate
python backend/pipeline.py
```

## Cron setup

Add to crontab (`crontab -e`) to run daily at 8 AM:

```
0 8 * * * cd ~/Projects/climate-sentiment-dashboard && .venv/bin/python backend/pipeline.py >> ~/logs/climate-pipeline.log 2>&1
```

Create the log directory first: `mkdir -p ~/logs`
