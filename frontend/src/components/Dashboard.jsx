import Header from './Header'
import SentimentGauge from './SentimentGauge'
import ArticleList from './ArticleList'
import { useSentiment } from '../hooks/useSentiment'
import { useArticles } from '../hooks/useArticles'

export default function Dashboard() {
  const { sentiment, loading: sentLoading, error: sentError } = useSentiment()
  const { articles, loading: artLoading, error: artError } = useArticles(30)

  const score = sentiment?.avg_score ?? null
  const articleCount = sentiment?.article_count ?? null
  const lastUpdated = sentiment?.window_date ?? null

  return (
    <div className="dashboard">
      <Header lastUpdated={lastUpdated} />

      <div className="gauge-section">
        {sentLoading ? (
          <p className="loading-text">Loading sentiment data...</p>
        ) : sentError ? (
          <p className="error-text">Could not load sentiment data — {sentError}</p>
        ) : score !== null ? (
          <SentimentGauge score={score} articleCount={articleCount} />
        ) : (
          <p className="loading-text">No sentiment data yet. Run the pipeline to get started.</p>
        )}
      </div>

      <ArticleList articles={articles} loading={artLoading} error={artError} />
    </div>
  )
}
