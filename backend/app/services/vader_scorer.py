import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from app.models import SentimentScore

# Download vader lexicon on first import (no-op if already present)
nltk.download("vader_lexicon", quiet=True)

_analyzer = SentimentIntensityAnalyzer()


def _compound_to_label(compound: float) -> str:
    if compound <= -0.6:
        return "very_negative"
    if compound <= -0.3:
        return "negative"
    if compound <= -0.05:
        return "slightly_negative"
    if compound <= 0.05:
        return "neutral"
    if compound <= 0.3:
        return "slightly_positive"
    if compound <= 0.6:
        return "positive"
    return "very_positive"


def score_article(title: str, summary: str | None) -> SentimentScore:
    """Score a single article using VADER. Combines title + summary for analysis."""
    text = title
    if summary:
        text = f"{title}. {summary}"

    scores = _analyzer.polarity_scores(text)
    compound = round(scores["compound"], 4)

    return SentimentScore(
        sentiment_score=compound,
        sentiment_label=_compound_to_label(compound),
    )


def score_articles_batch(articles: list[dict]) -> list[dict]:
    """Score a list of articles, adding sentiment_score and sentiment_label fields."""
    scored = []
    for article in articles:
        result = score_article(article["title"], article.get("summary"))
        article["sentiment_score"] = result.sentiment_score
        article["sentiment_label"] = result.sentiment_label
        article["raw_response"] = result.model_dump()
        scored.append(article)
    return scored
