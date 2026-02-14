import asyncio
import json
import re

import google.generativeai as genai
from app.config import settings
from app.models import SentimentScore

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT_TEMPLATE = """Analyze the climate news sentiment of this article.

Title: {title}
Summary: {summary}

Rate the sentiment on a scale from -1.0 (extremely negative/alarming) to 1.0 (extremely positive/hopeful).
Consider: Is this about climate damage, policy failure, or worsening conditions (negative)?
Or about solutions, progress, adaptation success, or policy wins (positive)?
Neutral/factual reporting with no strong valence should be near 0.

Respond with ONLY valid JSON, no markdown:
{{"sentiment_score": <float between -1.0 and 1.0>, "sentiment_label": "<one of: very_negative, negative, slightly_negative, neutral, slightly_positive, positive, very_positive>"}}"""


def _parse_response(text: str) -> SentimentScore | None:
    # Try direct JSON parse
    try:
        data = json.loads(text.strip())
        return SentimentScore(**data)
    except (json.JSONDecodeError, ValueError):
        pass
    # Regex fallback
    score_match = re.search(r'"sentiment_score"\s*:\s*([-\d.]+)', text)
    label_match = re.search(r'"sentiment_label"\s*:\s*"([^"]+)"', text)
    if score_match and label_match:
        return SentimentScore(
            sentiment_score=float(score_match.group(1)),
            sentiment_label=label_match.group(1),
        )
    return None


async def score_article(title: str, summary: str | None) -> SentimentScore | None:
    prompt = PROMPT_TEMPLATE.format(
        title=title,
        summary=summary or "No summary available.",
    )
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            result = _parse_response(response.text)
            if result:
                return result
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = 5 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"Gemini error: {e}")
                break
    return None


async def score_articles_batch(articles: list[dict]) -> list[dict]:
    """Score a list of articles, adding sentiment_score and sentiment_label fields."""
    scored = []
    for article in articles:
        result = await score_article(article["title"], article.get("summary"))
        if result:
            article["sentiment_score"] = result.sentiment_score
            article["sentiment_label"] = result.sentiment_label
            article["raw_response"] = result.model_dump()
        scored.append(article)
        await asyncio.sleep(0.5)  # Rate limiting for free tier
    return scored
