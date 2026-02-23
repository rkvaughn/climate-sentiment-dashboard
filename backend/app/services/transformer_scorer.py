from __future__ import annotations

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.models import SentimentScore

_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Lazy-loaded globals — initialized on first call to avoid startup cost.
_tokenizer = None
_model = None
_labels: list[str] = []


def _load_model() -> None:
    global _tokenizer, _model, _labels
    if _model is not None:
        return
    _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
    _model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
    _model.eval()
    _labels = [_model.config.id2label[i] for i in range(len(_model.config.id2label))]


def _score_to_label(score: float) -> str:
    if score >= 0.60:
        return "very_positive"
    if score >= 0.20:
        return "positive"
    if score >= 0.05:
        return "slightly_positive"
    if score > -0.05:
        return "neutral"
    if score > -0.20:
        return "slightly_negative"
    if score > -0.60:
        return "negative"
    return "very_negative"


def _infer(title: str, summary: str | None) -> tuple[SentimentScore, dict]:
    """Run model inference, returning (SentimentScore, raw_probs_dict)."""
    text = title
    if summary:
        text = f"{title}. {summary}"

    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )

    with torch.no_grad():
        logits = _model(**inputs).logits

    probs = torch.softmax(logits, dim=-1).squeeze().tolist()

    prob_map = {label.lower(): prob for label, prob in zip(_labels, probs)}

    p_pos = prob_map.get("positive", 0.0)
    p_neg = prob_map.get("negative", 0.0)

    score = round(p_pos - p_neg, 4)

    raw = {label: round(prob, 4) for label, prob in zip(_labels, probs)}
    raw["score"] = score

    return SentimentScore(
        sentiment_score=score,
        sentiment_label=_score_to_label(score),
    ), raw


def score_article(title: str, summary: str | None) -> SentimentScore:
    """Score a single article. Combines title + summary for analysis."""
    _load_model()
    result, _ = _infer(title, summary)
    return result


def score_articles_batch(articles: list[dict]) -> list[dict]:
    """Score a list of articles, adding sentiment_score, sentiment_label, and raw_response."""
    _load_model()
    scored = []
    for article in articles:
        result, raw = _infer(article["title"], article.get("summary"))
        article["sentiment_score"] = result.sentiment_score
        article["sentiment_label"] = result.sentiment_label
        article["raw_response"] = raw
        scored.append(article)
    return scored
