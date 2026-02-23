#!/usr/bin/env python3
"""
Score comparison: VADER vs. Transformer (RoBERTa) sentiment scoring.

Fetches all articles from Supabase (which already carry transformer scores),
re-scores them with VADER, then bootstraps confidence intervals for the mean
score difference across methods.

Run from the backend directory:
    python -m scripts.score_comparison

Outputs a JSON file with all results (used by the markdown report generator).
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict

import nltk
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import supabase

nltk.download("vader_lexicon", quiet=True)
_vader = SentimentIntensityAnalyzer()

BATCH_SIZE = 50
N_BOOTSTRAP = 10_000
RANDOM_SEED = 42
SUBSET_SIZES = [50, 100, 200, 526]  # random subsets + full corpus
N_SUBSETS_PER_SIZE = 5              # independent draws for each size


# ──────────────────────────────────────────────────────────────────────────────
# Data collection
# ──────────────────────────────────────────────────────────────────────────────

def fetch_all_articles() -> list[dict]:
    articles: list[dict] = []
    offset = 0
    while True:
        resp = (
            supabase.table("articles")
            .select("id, title, summary, sentiment_score, sentiment_label")
            .not_.is_("sentiment_score", "null")
            .range(offset, offset + BATCH_SIZE - 1)
            .execute()
        )
        batch = resp.data or []
        articles.extend(batch)
        if len(batch) < BATCH_SIZE:
            break
        offset += BATCH_SIZE
    return articles


def vader_score(title: str, summary: str | None) -> float:
    text = title if not summary else f"{title}. {summary}"
    return round(_vader.polarity_scores(text)["compound"], 4)


# ──────────────────────────────────────────────────────────────────────────────
# Bootstrap
# ──────────────────────────────────────────────────────────────────────────────

def bootstrap_mean_diff(
    vader_scores: np.ndarray,
    transformer_scores: np.ndarray,
    n_boot: int = N_BOOTSTRAP,
    rng: np.random.Generator | None = None,
) -> dict:
    """
    Bootstrap the mean of (transformer − VADER) differences.

    Returns mean_diff, std, 95 % CI, and the full bootstrap distribution.
    """
    if rng is None:
        rng = np.random.default_rng(RANDOM_SEED)

    diffs = transformer_scores - vader_scores
    observed_mean = float(np.mean(diffs))

    boot_means = np.empty(n_boot)
    n = len(diffs)
    for i in range(n_boot):
        sample = rng.choice(diffs, size=n, replace=True)
        boot_means[i] = np.mean(sample)

    ci_lo, ci_hi = np.percentile(boot_means, [2.5, 97.5])

    return {
        "n": n,
        "observed_mean_diff": observed_mean,
        "bootstrap_std": float(np.std(boot_means)),
        "ci_95_lo": float(ci_lo),
        "ci_95_hi": float(ci_hi),
        "boot_dist_percentiles": {
            str(p): float(np.percentile(boot_means, p))
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Agreement / disagreement analysis
# ──────────────────────────────────────────────────────────────────────────────

LABEL_ORDER = [
    "very_negative", "negative", "slightly_negative",
    "neutral",
    "slightly_positive", "positive", "very_positive",
]
LABEL_INDEX = {l: i for i, l in enumerate(LABEL_ORDER)}


def vader_label(compound: float) -> str:
    if compound <= -0.6:  return "very_negative"
    if compound <= -0.3:  return "negative"
    if compound <= -0.05: return "slightly_negative"
    if compound <= 0.05:  return "neutral"
    if compound <= 0.3:   return "slightly_positive"
    if compound <= 0.6:   return "positive"
    return "very_positive"


def label_agreement(articles: list[dict]) -> dict:
    exact_match = 0
    direction_match = 0      # both positive / both negative / both neutral
    ordinal_errors: list[int] = []

    for a in articles:
        vl = vader_label(a["vader_score"])
        tl = a["transformer_label"]
        if vl == tl:
            exact_match += 1

        def sentiment_dir(label: str) -> str:
            if "positive" in label: return "positive"
            if "negative" in label: return "negative"
            return "neutral"

        if sentiment_dir(vl) == sentiment_dir(tl):
            direction_match += 1

        ordinal_errors.append(abs(LABEL_INDEX[vl] - LABEL_INDEX[tl]))

    n = len(articles)
    return {
        "exact_match_pct": round(exact_match / n * 100, 2),
        "direction_match_pct": round(direction_match / n * 100, 2),
        "mean_ordinal_error": round(float(np.mean(ordinal_errors)), 3),
        "median_ordinal_error": float(np.median(ordinal_errors)),
    }


def label_distribution(scores: np.ndarray, label_fn) -> dict:
    labels = [label_fn(s) for s in scores]
    dist = {}
    for l in LABEL_ORDER:
        dist[l] = round(labels.count(l) / len(labels) * 100, 2)
    return dist


def transformer_label_fn(score: float) -> str:
    if score >= 0.60:   return "very_positive"
    if score >= 0.20:   return "positive"
    if score >= 0.05:   return "slightly_positive"
    if score > -0.05:   return "neutral"
    if score > -0.20:   return "slightly_negative"
    if score > -0.60:   return "negative"
    return "very_negative"


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> dict:
    print("Fetching articles from Supabase…")
    articles = fetch_all_articles()
    print(f"  {len(articles)} articles with transformer scores")

    print("Computing VADER scores…")
    for a in articles:
        a["vader_score"] = vader_score(a["title"], a.get("summary"))
    print("  Done")

    vader_arr  = np.array([a["vader_score"]          for a in articles])
    trans_arr  = np.array([float(a["sentiment_score"]) for a in articles])

    # ── Full-corpus bootstrap ──────────────────────────────────────────────
    print("Bootstrapping full corpus…")
    rng = np.random.default_rng(RANDOM_SEED)
    full_boot = bootstrap_mean_diff(vader_arr, trans_arr, rng=rng)

    # ── Per-size subset bootstraps ─────────────────────────────────────────
    subset_results: dict = {}
    for size in SUBSET_SIZES:
        if size >= len(articles):
            continue   # skip — covered by full corpus above
        runs = []
        print(f"Bootstrapping {N_SUBSETS_PER_SIZE} subsets of size {size}…")
        for i in range(N_SUBSETS_PER_SIZE):
            idx = rng.choice(len(articles), size=size, replace=False)
            v_sub = vader_arr[idx]
            t_sub = trans_arr[idx]
            runs.append(bootstrap_mean_diff(v_sub, t_sub, rng=rng))
        subset_results[str(size)] = runs

    # ── Agreement analysis ─────────────────────────────────────────────────
    print("Computing label agreement…")
    for a in articles:
        a["transformer_label"] = a["sentiment_label"]  # already in DB
    agreement = label_agreement(articles)

    # ── Label distributions ────────────────────────────────────────────────
    vader_dist = label_distribution(vader_arr, vader_label)
    trans_dist = label_distribution(trans_arr, transformer_label_fn)

    # ── Descriptive stats ─────────────────────────────────────────────────
    def desc(arr: np.ndarray) -> dict:
        return {
            "mean":   round(float(np.mean(arr)), 4),
            "std":    round(float(np.std(arr)), 4),
            "min":    round(float(np.min(arr)), 4),
            "p25":    round(float(np.percentile(arr, 25)), 4),
            "median": round(float(np.median(arr)), 4),
            "p75":    round(float(np.percentile(arr, 75)), 4),
            "max":    round(float(np.max(arr)), 4),
        }

    results = {
        "n_articles": len(articles),
        "n_bootstrap": N_BOOTSTRAP,
        "random_seed": RANDOM_SEED,
        "descriptive": {
            "vader": desc(vader_arr),
            "transformer": desc(trans_arr),
            "diff_t_minus_v": desc(trans_arr - vader_arr),
        },
        "full_corpus_bootstrap": full_boot,
        "subset_bootstraps": subset_results,
        "label_agreement": agreement,
        "label_distributions": {
            "vader": vader_dist,
            "transformer": trans_dist,
        },
    }

    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "score_comparison_results.json"
    )
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved → {out_path}")
    return results


if __name__ == "__main__":
    results = main()
    print("\n── Summary ──────────────────────────────────────────────────")
    d = results["descriptive"]
    print(f"  VADER mean score:       {d['vader']['mean']:+.4f}")
    print(f"  Transformer mean score: {d['transformer']['mean']:+.4f}")
    diff = results["full_corpus_bootstrap"]
    print(f"  Mean diff (T − V):      {diff['observed_mean_diff']:+.4f}")
    print(f"  95% CI:                 [{diff['ci_95_lo']:+.4f}, {diff['ci_95_hi']:+.4f}]")
    print(f"  Label exact match:      {results['label_agreement']['exact_match_pct']}%")
    print(f"  Direction match:        {results['label_agreement']['direction_match_pct']}%")
