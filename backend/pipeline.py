#!/usr/bin/env python3
"""
Climate Sentiment Pipeline
Fetches climate RSS feeds, scores new articles with ClimateBERT, and writes the
static JSON files the dashboard reads from frontend/public/data/.
Run: python backend/pipeline.py  (scheduled daily by .github/workflows/pipeline.yml)
"""
import json, re
from calendar import timegm
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "backend" / "app" / "data" / "sources.json"
DATA_DIR = ROOT / "frontend" / "public" / "data"
ARTICLES_DIR = DATA_DIR / "articles"
MODEL_NAME = "climatebert/distilroberta-base-climate-sentiment"
LATEST_ARTICLE_COUNT = 30
SUMMARY_MAX_CHARS = 500
MODEL_MAX_TOKENS = 512


def _parse_date(entry):
    if getattr(entry, "published_parsed", None):
        return datetime.fromtimestamp(timegm(entry.published_parsed), tz=timezone.utc).isoformat()
    return None


def _get_summary(entry):
    if getattr(entry, "summary", None):
        return re.sub(r"<[^>]+>", "", entry.summary).strip()[:SUMMARY_MAX_CHARS]
    return None


def _month_key(article):
    return (article.get("published_at") or article["fetched_at"])[:7]


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


class Scorer:
    def __init__(self):
        print(f"Loading {MODEL_NAME}...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).eval()
        self.labels = [self.model.config.id2label[i] for i in range(len(self.model.config.id2label))]

    def score(self, title, summary):
        text = f"{title}. {summary}" if summary else title
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=MODEL_MAX_TOKENS)
        with torch.no_grad():
            probs = torch.softmax(self.model(**inputs).logits, dim=-1).squeeze().tolist()
        probabilities = {lbl: round(p, 4) for lbl, p in zip(self.labels, probs)}
        return {
            "sentiment_score": round(probabilities["opportunity"] - probabilities["risk"], 4),
            "sentiment_label": max(probabilities, key=probabilities.get),
            "probabilities": probabilities,
            "model": MODEL_NAME,
        }


def load_articles():
    articles = {}
    for path in sorted(ARTICLES_DIR.glob("*.json")):
        for a in json.loads(path.read_text()):
            articles[a["url"]] = a
    return articles


def fetch_new(sources, articles):
    now = datetime.now(tz=timezone.utc).isoformat()
    fetched = added = 0
    for source in sources:
        try:
            feed = feedparser.parse(source["feed_url"])
        except Exception as e:
            print(f"Error fetching {source['id']}: {e}")
            continue
        for entry in feed.entries:
            link, title = entry.get("link"), entry.get("title")
            if not link or not title:
                continue
            fetched += 1
            url = link.strip()
            if url in articles:
                continue
            articles[url] = {
                "url": url,
                "source_id": source["id"],
                "title": title.strip(),
                "published_at": _parse_date(entry),
                "summary": _get_summary(entry),
                "fetched_at": now,
            }
            added += 1
    print(f"Fetched {fetched} entries, {added} new.")


def score_pending(articles):
    pending = [a for a in articles.values() if a.get("model") != MODEL_NAME]
    if not pending:
        print("No articles to score.")
        return
    scorer = Scorer()
    print(f"Scoring {len(pending)} articles...")
    for a in pending:
        a.update(scorer.score(a["title"], a.get("summary")))


def daily_aggregations(articles):
    by_date = defaultdict(list)
    for a in articles.values():
        if a.get("published_at") and a.get("model") == MODEL_NAME:
            by_date[a["published_at"][:10]].append(a)
    daily = []
    for day in sorted(by_date):
        scores = [a["sentiment_score"] for a in by_date[day]]
        labels = Counter(a["sentiment_label"] for a in by_date[day])
        daily.append({
            "window_date": day,
            "avg_score": round(sum(scores) / len(scores), 4),
            "article_count": len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "label_counts": dict(labels),
        })
    return daily


def write_outputs(articles, sources):
    by_month = defaultdict(list)
    for a in articles.values():
        by_month[_month_key(a)].append(a)
    for month, items in by_month.items():
        items.sort(key=lambda a: (a.get("published_at") or "", a["url"]), reverse=True)
        _write_json(ARTICLES_DIR / f"{month}.json", items)

    daily = daily_aggregations(articles)
    _write_json(DATA_DIR / "aggregations.json", {"model": MODEL_NAME, "daily": daily})

    scored = sorted(
        (a for a in articles.values() if a.get("model") == MODEL_NAME),
        key=lambda a: a.get("published_at") or "",
        reverse=True,
    )
    latest_fields = ("url", "source_id", "title", "published_at",
                     "sentiment_score", "sentiment_label", "probabilities")
    _write_json(DATA_DIR / "latest.json", {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "model": MODEL_NAME,
        "sources": {s["id"]: s["name"] for s in sources},
        "aggregation": daily[-1] if daily else None,
        "articles": [{k: a.get(k) for k in latest_fields} for a in scored[:LATEST_ARTICLE_COUNT]],
    })
    if daily:
        d = daily[-1]
        print(f"Latest day {d['window_date']}: {d['article_count']} articles, avg {d['avg_score']}")


def run():
    with open(SOURCES_FILE) as f:
        sources = json.load(f)["sources"]
    articles = load_articles()
    fetch_new([s for s in sources if s.get("active", True)], articles)
    score_pending(articles)
    write_outputs(articles, sources)


if __name__ == "__main__":
    run()
