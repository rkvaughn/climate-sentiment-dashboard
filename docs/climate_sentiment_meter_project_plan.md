# Project Plan: Climate News Sentiment Meter

## 1. Project Goal

Develop a web application that visualizes the sentiment (good news/bad news) of climate change-related news over different time horizons (daily, weekly, monthly, yearly) using "gas gauge" style dials. The application will aggregate sentiment from various data sources (popular media, academia, think tanks, research centers) and link to highly cited/popular sources for each time window.

## 2. Technical Stack (Proposed)

*   **Frontend:** React (for UI components), D3.js (for gauges/visualization).
*   **Backend/API:** Node.js (with Express.js) or Python (with FastAPI/Flask) for data ingestion, sentiment analysis, aggregation, and serving API endpoints.
*   **Database:** MongoDB or PostgreSQL (for storing raw news articles, processed content, sentiment scores, and source metadata).
*   **Deployment:** Docker (for containerization), suitable cloud platform (e.g., Google Cloud Run, AWS ECS).

## 3. Project Phases & Detailed Tasks for Claude Code

### Phase 1: Planning & Setup

*   **Task 1.1: Project Initialization & Repository Setup**
    *   Initialize a new full-stack project (e.g., React frontend + Node.js/Python backend).
    *   Set up basic project structure, `package.json` (or `pyproject.toml`), and initialize a Git repository.
    *   Configure `.gitignore` for common files/directories.
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Initialize a new React project in the `frontend/` directory and a Node.js Express backend project in the `backend/` directory. Set up basic `.gitignore` files for both. Provide the commands and any generated files."
        *   **Prompt for Gemini:** "Create a basic Dockerfile for a Node.js Express application that serves a React build. Provide the Dockerfile content."
*   **Task 1.2: Research & Source Identification**
    *   **Google Trends Assessment:** Conduct a Google Trends analysis for key climate-related terms ("climate", "climate change", "climate crisis") over various timeframes (last day, week, month, year). This will help understand public interest and media focus, which can inform source selection and sentiment interpretation.
        *   **Gemini Delegation Opportunity:**
            *   **Prompt for Gemini:** "Perform a Google Trends analysis for the keywords 'climate', 'climate change', and 'climate crisis' for the last day, week, month, and year. Summarize the trending patterns and relative search interest for each term across these periods."
    *   Identify a diverse set of reliable sources for climate change news from popular media, academia, think tanks, and research centers. Categorize sources by type (e.g., 'media', 'academic', 'social_media') to enable filtering.
    *   For each source, investigate available APIs, RSS feeds, or web scraping policies. Prioritize programmatic access.
    *   Compile a list of chosen sources with their access methods (API endpoint, RSS URL, scraping strategy).
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Perform web searches for 'best climate change news APIs', 'academic climate research RSS feeds', 'prominent climate change think tank reports feeds', 'NASA climate data APIs', and 'top climate change social media aggregators'. Compile a list of at least 10 unique, programmatically accessible sources, identifying their type (media, academic, social_media)."

### Phase 2: Data Ingestion & Storage

*   **Task 2.1: Database Schema Design**
    *   Design a flexible database schema to store:
        *   Raw articles (title, URL, content, publication date, source).
        *   Processed article content (e.g., cleaned text for sentiment analysis).
        *   Individual article sentiment scores.
        *   Aggregated sentiment scores per time window (day, week, month, year).
        *   Metadata about sources (name, type: 'media', 'academic', 'social_media', reliability score, API key if needed).
        *   Article categorization: `climateCategory` (e.g., 'physical_risk', 'transition_risk', 'general_climate').
    *   Create a separate collection/table for `userSuggestedSources` to store URLs submitted by users, along with their status (pending, approved, rejected).
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Suggest an optimal MongoDB schema for storing climate news articles and their sentiment scores, designed for efficient querying by date, time window, source type, and climate category. Include fields for source, title, URL, publishDate, rawContent, processedContent, individualSentimentScore, aggregatedSentiment, sourceType, climateCategory, and also suggest a schema for a separate `userSuggestedSources` collection."
*   **Task 2.2: Data Ingestion Modules**
    *   Develop backend modules (scrapers/collectors) for each identified source.
    *   Implement robust error handling, rate limiting, and data parsing.
    *   Store raw and processed content in the database.
    *   Develop a separate module for processing and ingesting user-submitted URLs from the `userSuggestedSources` collection, ensuring proper validation and queuing.
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Write a Python function that takes an RSS feed URL for news articles, fetches the feed, parses it, extracts title, link, and publication date, and returns a list of dictionaries. Handle basic errors."
        *   **Prompt for Gemini:** "Write a Node.js module using `axios` to fetch data from a given REST API endpoint (e.g., a news API), assuming a JSON response with an array of articles. Extract relevant fields like title, URL, content, and date. Provide example usage."
        *   **Prompt for Gemini:** "Design a simple Node.js module that can take a URL, perform a basic fetch of its content, and extract the main article text, suitable for processing user-submitted URLs."

### Phase 3: Sentiment Analysis & Aggregation

*   **Task 3.1: Sentiment Model Selection & Implementation**
    *   Research and select a sentiment analysis model/library suitable for news text. Consider pre-trained models (e.g., from Hugging Face, Google Cloud Natural Language) that can be fine-tuned or are robust for general English text.
    *   Implement the chosen model into the data processing pipeline.
    *   Extend the model or pipeline to also categorize articles into `climateCategory` (e.g., 'physical_risk', 'transition_risk', 'general_climate') based on keywords or semantic analysis.
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Compare the pros and cons of using VADER (NLTK) vs. a Hugging Face transformer model for sentiment analysis of climate change news articles, specifically considering nuanced language. Provide example Python code for integrating one of them."
        *   **Prompt for Gemini:** "Propose a keyword-based approach (and example Python code) to categorize news articles into 'physical_risk', 'transition_risk', or 'general_climate'. Include example keywords for each category."
*   **Task 3.2: Sentiment Index Definition & User Refinement**
    *   Define a method for scoring individual articles (e.g., -1 to 1, or multi-class).
    *   **Directional Trend Emphasis:** The aggregated sentiment score for each time window should reflect a *directional trend* rather than just an absolute value. This means comparing the current period's sentiment to a previous baseline (e.g., current day vs. previous day's average, current week vs. previous week's average) to indicate if sentiment is "Trending Good" or "Trending Bad".
    *   **Crucial for User Refinement:** Design the sentiment aggregation logic with configurability in mind. Users must be able to refine:
        *   **Source Weighting:** Assign higher or lower importance to certain sources (e.g., academic papers weighted differently than popular media).
        *   **Keyword Adjustments:** Introduce specific keywords or phrases that should influence sentiment in a predefined way.
        *   **Thresholds:** Adjust thresholds for categorizing sentiment (e.g., what score constitutes "positive" vs. "neutral").
        *   **Social Media Toggle:** Include/exclude social media sources from aggregation.
        *   **Category Filtering:** Aggregate sentiment specifically for 'physical_risk', 'transition_risk', or 'general_climate' categories.
    *   Implement aggregation logic to combine individual sentiment scores into a single index for each time window (day, week, month, year), respecting weighting, configurable parameters, and filtering options.
    *   Store aggregated scores and their directional trends in the database.
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Draft a Python class `ClimateSentimentAggregator` that takes a list of `{score, source, date, sourceType, climateCategory}` objects and a configuration dictionary `{source_weights: {}, keyword_adjustments: {}, thresholds: {}, include_social_media: bool, category_filter: str}`. It should compute daily, weekly, monthly, and yearly aggregated sentiment scores, and for each, calculate a 'directional trend' by comparing to the previous equivalent period. Provide pseudocode for the `aggregate` and `calculate_directional_trend` methods."
*   **Task 3.3: Processing Pipeline Integration & Scheduling**
    *   Integrate data ingestion with sentiment analysis and aggregation.
    *   Set up a mechanism (e.g., cron jobs, cloud functions) for continuous data collection and sentiment updates.

### Phase 4: Frontend Development & Visualization

*   **Task 4.1: Backend API Endpoints**
    *   Create REST API endpoints to serve:
        *   Aggregated sentiment scores for specific time windows, including directional trend (`/api/sentiment?window=day&category=general_climate&social_media=true`).
        *   **Historical Sentiment Data:** Add an endpoint for historical sentiment trends over time, starting from Jan 2026, for each time window and filter combination (`/api/sentiment/history?window=month&start_date=2026-01-01`).
        *   A curated list of highly cited/popular articles/sources for each time window, including their sentiment and a link (`/api/sources?window=day&category=physical_risk`).
        *   An endpoint to submit new URLs for user-suggested sources (`/api/sources/suggest`).
        *   An endpoint to serve the plain English sentiment scoring methodology description (`/api/methodology`).
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Design a Node.js Express router and controller for API endpoints: `/api/sentiment`, `/api/sentiment/history`, `/api/sources`, `/api/sources/suggest`, and `/api/methodology`. Ensure `/api/sentiment` and `/api/sentiment/history` support `window`, `category`, and `social_media` query parameters. Provide example JSON responses for each, including historical data structure."
*   **Task 4.2: Frontend UI - Gauge Components & Trend Graphs**
    *   Develop React components for the "gas gauge" style dials.
    *   Utilize D3.js or a similar library for SVG-based dynamic visualizations.
    *   Each gauge should visually represent the sentiment's directional trend (e.g., using color and needle position).
    *   **Update Gauge Labels:** Change "Bad News" to "Trending Bad" and "Good News" to "Trending Good" on the gauge dial.
    *   **Trend Line Graphs:** For each time window, include an interactive line graph showing the sentiment trend over time, starting from Jan 2026.
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Generate a basic React component using SVG that draws a 'gas gauge' dial. It should accept a `directionalSentimentScore` prop and visually indicate it. The dial should be labeled 'Trending Bad' on the left and 'Trending Good' on the right. Include example CSS."
        *   **Prompt for Gemini:** "Create a React component that displays an interactive D3.js line graph for time-series sentiment data. The graph should plot sentiment scores over time, starting from January 2026, and be responsive to different time windows (daily, weekly, monthly, yearly). Provide example code."
*   **Task 4.3: Frontend UI - Source Panels & User Controls**
    *   Create React components to display clickable links to highly cited or popular data sources adjacent to their respective gauges.
    *   Ensure panels update with the relevant sources based on selected filters.
    *   **User Controls:**
        *   Implement UI elements (checkboxes/toggles) to allow the user to enable/disable social media sources.
        *   Implement UI elements (dropdowns/radio buttons) to filter sentiment by `climateCategory` ('physical_risk', 'transition_risk', 'general_climate').
        *   Implement a form/input field for users to suggest new URLs for data ingestion.
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Draft a responsive React component `SourcePanel` that takes `sources` (array of `{title, url, sourceName, sentimentScore}`) and `filters` as props. It should render clickable links, filtering them dynamically. Also, draft a React component `UserControls` including a social media toggle, category filter (dropdown), and a URL submission form. Include basic styling."
*   **Task 4.4: Data Integration & Methodology Link**
    *   Fetch data from the backend APIs (including historical trends) and integrate it into the frontend components.
    *   Implement refreshing mechanisms for data.
    *   **Methodology Link:** Include a prominent hyperlink on the main dashboard to the detailed sentiment scoring methodology page/section.

### Phase 5: Deployment & Maintenance

*   **Task 5.1: Dockerization**
    *   Refine Dockerfiles for both frontend and backend to ensure efficient build processes and container sizes.
    *   **Gemini Delegation Opportunity:**
        *   **Prompt for Gemini:** "Review and optimize the existing Dockerfile for the Node.js Express backend, focusing on multi-stage builds for smaller image size and faster build times."
*   **Task 5.2: Deployment Scripts**
    *   Create scripts or configuration for deploying the Dockerized application to a cloud platform.
*   **Task 5.3: Monitoring & Logging**
    *   Set up basic application performance monitoring and logging for data ingestion, sentiment analysis, and API health.

## 4. Key Considerations for Claude

*   **Bias Awareness:** Be critically aware of potential biases in chosen data sources and sentiment analysis models. The user refinement options are critical for mitigating this.
*   **Scalability:** Design the data ingestion and processing pipelines to handle increasing volumes of news data.
*   **Ethical Data Use:** Ensure compliance with terms of service for all data sources and APIs.
*   **Data Freshness:** Implement efficient caching and update strategies to keep sentiment data as current as possible for the daily gauge.
*   **Security:** Protect API keys and other sensitive information.
*   **User Experience:** Focus on clear, intuitive visualization for the sentiment meters and easy access to linked sources.
*   **Modularity:** Ensure that different components (data sources, sentiment models, aggregation logic, UI components) are modular and can be independently updated or replaced.
