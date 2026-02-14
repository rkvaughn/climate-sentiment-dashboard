# Climate News Sentiment Scoring Methodology

This document describes the methodology used to calculate and present the climate news sentiment scores, emphasizing user configurability and the interpretation of directional trends.

## 1. Core Sentiment Score (Per Article)

Each individual news article ingested into the system will first undergo a sentiment analysis to determine its core sentiment.

*   **Process:** A selected sentiment analysis model (e.g., a transformer model or a lexicon-based approach like VADER) will process the article's text content.
*   **Output:** The model will output an individual sentiment score, typically a continuous value (e.g., from -1.0 for highly negative to +1.0 for highly positive) or a categorical classification (negative, neutral, positive).

## 2. Article Categorization (Physical Risk, Transition Risk, General Climate)

Beyond overall sentiment, each article will be categorized to provide a more granular view of climate change discourse.

*   **Process:** Keywords and semantic analysis will be used to assign each article to one or more categories:
    *   **Physical Risk:** Articles discussing direct impacts of climate change (e.g., extreme weather, sea-level rise, droughts, wildfires).
    *   **Transition Risk:** Articles focusing on the economic, policy, and social challenges/opportunities of transitioning to a low-carbon economy (e.g., carbon pricing, renewable energy investment, stranded assets, regulatory changes).
    *   **General Climate:** Broader discussions about climate change, scientific reports, public awareness, general policy debates not specific to physical or transition risks.
*   **Refinement:** The keyword lists and classification rules for these categories can be refined by the user.

## 3. Aggregated Sentiment Indices & Directional Trends

Individual article sentiments are aggregated over defined time windows (Day, Week, Month, Year) to create an overall sentiment index for each period. Crucially, these indices will reflect a *directional trend*.

*   **Aggregation:** For each time window, the individual sentiment scores of relevant articles are combined into a single average score.
*   **Directional Trend Calculation:** Instead of just displaying an absolute score, the system will calculate if the sentiment is "Trending Good" or "Trending Bad". This is done by comparing the current aggregated sentiment score of a period (e.g., the last 24 hours) against a baseline (e.g., the average sentiment of the previous 24 hours, or a longer moving average).
    *   If current sentiment is significantly more positive than the baseline, it indicates "Trending Good."
    *   If current sentiment is significantly more negative than the baseline, it indicates "Trending Bad."
    *   If sentiment is relatively stable or changes are minor, it will be considered "Neutral" or "Stable."
*   **Numerical Display:** The score displayed on the gauge will represent this directional shift (e.g., a higher positive number for "Trending Good," a lower negative number for "Trending Bad," with zero being stable).
*   **Historical Data:** Aggregated sentiment scores and directional trends will be stored and available from January 2026 onwards to support line graph visualizations.

## 4. User Refinability of Sentiment Indices

The methodology is designed to be highly configurable by the user to address potential biases and adapt to specific analytical needs.

*   **Source Weighting:** Users can assign different weights to specific sources. For example, academic papers might be given higher weight than popular media, or specific news outlets could be weighted based on perceived reliability.
*   **Keyword Adjustments:** Users can introduce or modify keyword lists that positively or negatively influence an article's sentiment score, or its categorization into risk types. For instance, specific policy terms might be flagged as positive, while terms related to climate disasters might be flagged as negative.
*   **Thresholds:** Users can adjust the numerical thresholds that define what constitutes "positive," "neutral," or "negative" sentiment, both for individual articles and for the aggregated directional trends.
*   **Social Media Inclusion/Exclusion:** A toggle will allow users to decide whether sentiment derived from social media sources is included in the aggregated indices for any given time window. This helps analyze sentiment across different discourse environments.

## 5. User-Suggested URLs

The system allows users to dynamically suggest new URLs for data ingestion.

*   **Process:** Users submit URLs through the UI. These URLs are then processed, and if deemed valid and relevant, their content is ingested, analyzed for sentiment, and included in the overall sentiment calculations. This allows the system to grow its data sources based on user input.

---

**Link to Main Page:**
This `sentiment_scoring_methodology.md` file will be served via an API endpoint and hyperlinked from the main Climate News Sentiment Tracker dashboard.
