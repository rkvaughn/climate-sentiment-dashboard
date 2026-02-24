#!/usr/bin/env python3
"""
Climate Sentiment Pipeline
Fetches RSS articles, scores with RoBERTa, writes to Supabase.
Run: python backend/pipeline.py
Cron: 0 8 * * * cd ~/Projects/climate-sentiment-dashboard && .venv/bin/python backend/pipeline.py >> ~/logs/climate-pipeline.log 2>&1
"""
import json, os, re
from datetime import date, datetime, timezone
from pathlib import Path
from time import mktime

import feedparser
import torch
from dotenv import load_dotenv
from supabase import create_client
from transformers import AutoModelForSequenceClassification, AutoTokenizer

load_dotenv(Path(__file__).parent / ".env")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
SOURCES_FILE = Path(__file__).parent / "app" / "data" / "sources.json"
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

print("Loading model...")
_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
_model.eval()
_labels = [_model.config.id2label[i] for i in range(len(_model.config.id2label))]
print("Model ready.")


def _score_to_label(score):
    if score >= 0.60: return "very_positive"
    if score >= 0.20: return "positive"
    if score >= 0.05: return "slightly_positive"
    if score > -0.05: return "neutral"
    if score > -0.20: return "slightly_negative"
    if score > -0.60: return "negative"
    return "very_negative"


def _score_article(title, summary):
    text = f"{title}. {summary}" if summary else title
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    with torch.no_grad():
        probs = torch.softmax(_model(**inputs).logits, dim=-1).squeeze().tolist()
    prob_map = {lbl.lower(): p for lbl, p in zip(_labels, probs)}
    score = round(prob_map.get("positive", 0.0) - prob_map.get("negative", 0.0), 4)
    return {
        "sentiment_score": score,
        "sentiment_label": _score_to_label(score),
        "raw_response": {lbl: round(p, 4) for lbl, p in zip(_labels, probs)},
    }


def _parse_date(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc).isoformat()
    return None


def _get_summary(entry):
    if hasattr(entry, "summary") and entry.summary:
        return re.sub(r"<[^>]+>", "", entry.summary).strip()[:500]
    return None


def run():
    db = create_client(SUPABASE_URL, SUPABASE_KEY)
    with open(SOURCES_FILE) as f:
        sources = [s for s in json.load(f)["sources"] if s.get("active", True)]

    # 1. Fetch & insert
    fetched = inserted = 0
    for source in sources:
        try:
            feed = feedparser.parse(source["feed_url"])
            for entry in feed.entries:
                link, title = entry.get("link"), entry.get("title")
                if not link or not title:
                    continue
                fetched += 1
                try:
                    r = db.table("articles").upsert(
                        {"source_id": source["id"], "title": title.strip(),
                         "url": link.strip(), "published_at": _parse_date(entry),
                         "summary": _get_summary(entry)},
                        on_conflict="url", ignore_duplicates=True,
                    ).execute()
                    if r.data:
                        inserted += 1
                except Exception as e:
                    print(f"  Insert error {link}: {e}")
        except Exception as e:
            print(f"Error fetching {source['id']}: {e}")
    print(f"Fetched {fetched}, inserted {inserted} new.")

    # 2. Score unscored (batch of 50)
    unscored = (
        db.table("articles")
        .select("id, title, summary")
        .is_("sentiment_score", "null")
        .limit(50)
        .execute()
    )
    scored = 0
    if unscored.data:
        print(f"Scoring {len(unscored.data)} articles...")
        for a in unscored.data:
            try:
                result = _score_article(a["title"], a.get("summary"))
                db.table("articles").update(result).eq("id", a["id"]).execute()
                scored += 1
            except Exception as e:
                print(f"  Score error {a['id']}: {e}")
    print(f"Scored {scored} articles.")

    # 3. Daily aggregation
    today = date.today().isoformat()
    resp = (
        db.table("articles")
        .select("sentiment_score")
        .not_.is_("sentiment_score", "null")
        .gte("published_at", f"{today}T00:00:00Z")
        .lt("published_at", f"{today}T23:59:59Z")
        .execute()
    )
    if resp.data:
        scores = [a["sentiment_score"] for a in resp.data]
        db.table("sentiment_aggregations").upsert(
            {"time_window": "daily", "window_date": today,
             "avg_score": round(sum(scores) / len(scores), 4),
             "article_count": len(scores),
             "min_score": min(scores), "max_score": max(scores)},
            on_conflict="time_window,window_date",
        ).execute()
        print(f"Aggregation: {len(scores)} articles, avg {round(sum(scores)/len(scores), 4)}")
    else:
        print("No articles published today — aggregation skipped.")


if __name__ == "__main__":
    run()
