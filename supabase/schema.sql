-- Climate Sentiment Dashboard — Supabase Schema
-- Run this in the Supabase SQL Editor to set up all tables and RLS policies.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Sources table — reference data, seeded once
-- ============================================================
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    feed_url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    bias_rating TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Articles table — one row per fetched + scored article
-- ============================================================
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT REFERENCES sources(id),
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    published_at TIMESTAMPTZ,
    summary TEXT,
    sentiment_score REAL,
    sentiment_label TEXT,
    raw_response JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id);

-- ============================================================
-- Sentiment aggregations — pre-computed daily scores
-- ============================================================
CREATE TABLE IF NOT EXISTS sentiment_aggregations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    time_window TEXT NOT NULL,
    window_date DATE NOT NULL,
    avg_score REAL NOT NULL,
    article_count INTEGER NOT NULL,
    min_score REAL,
    max_score REAL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(time_window, window_date)
);

CREATE INDEX IF NOT EXISTS idx_aggregations_window_date ON sentiment_aggregations(window_date DESC);

-- ============================================================
-- Row Level Security — anon can SELECT, service_role can write
-- ============================================================
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_aggregations ENABLE ROW LEVEL SECURITY;

-- Anon read access
CREATE POLICY "anon_read_sources" ON sources
    FOR SELECT TO anon USING (true);

CREATE POLICY "anon_read_articles" ON articles
    FOR SELECT TO anon USING (true);

CREATE POLICY "anon_read_aggregations" ON sentiment_aggregations
    FOR SELECT TO anon USING (true);

-- Service role full access (backend writes)
CREATE POLICY "service_all_sources" ON sources
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_all_articles" ON articles
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_all_aggregations" ON sentiment_aggregations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================
-- Seed MVP sources
-- ============================================================
INSERT INTO sources (id, name, url, feed_url, source_type, bias_rating, active) VALUES
    ('carbon_brief', 'Carbon Brief', 'https://www.carbonbrief.org', 'https://www.carbonbrief.org/feed', 'Specialized Journalism', 'Center', true),
    ('guardian_environment', 'The Guardian (Environment)', 'https://www.theguardian.com/us/environment', 'https://www.theguardian.com/us/environment/rss', 'Mainstream Media', 'Center-Left', true),
    ('inside_climate_news', 'Inside Climate News', 'https://insideclimatenews.org', 'https://insideclimatenews.org/feed/', 'Specialized Journalism', 'Center-Left', true),
    ('grist', 'Grist', 'https://grist.org', 'https://grist.org/feed/', 'Specialized Journalism', 'Left', true)
ON CONFLICT (id) DO NOTHING;
