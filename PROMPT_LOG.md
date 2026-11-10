# Prompt Log — Climate Sentiment Meter

## 2026-11-07 — Dashboard outage; migrate off Supabase to ClimateBERT + GitHub-only stack

**Prompt:** The dashboard is broken, troubleshoot. Then: re-assess whether Supabase is the best solution, keeping the project free. Then: go with the static-JSON + GitHub Actions plan, refactor scoring to ClimateBERT, and add a detailed ClimateBERT description with a source link to the dashboard.

**Output:**
- Diagnosed outage: Supabase project `htcftmhqjpgsrcrnfbwy` returns NXDOMAIN (deleted by the free tier).
- Replaced Supabase with JSON in `frontend/public/data/`, written by `backend/pipeline.py` and committed daily by `.github/workflows/pipeline.yml`, which then calls `deploy.yml`.
- Switched the scorer to `climatebert/distilroberta-base-climate-sentiment`; label = argmax class, score = P(opportunity) − P(risk). Verified the label mapping on 100 rows of the ClimateBERT test split (76/100 agreement).
- Fixed a timezone bug (`mktime` → `calendar.timegm`) that shifted publication dates by the local UTC offset.
- Frontend: single `useDashboardData` hook, Risk/Neutral/Opportunity columns with probability tooltips, new `ModelInfo` section; removed `@supabase/supabase-js`.
- Removed `supabase/`, `.env.example` files, `backend/scripts/rescore_all.py`; updated README, PROJECT_STATE, backend README, methodology doc.
