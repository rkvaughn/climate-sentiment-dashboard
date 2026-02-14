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
        # Strip HTML tags (basic)
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
