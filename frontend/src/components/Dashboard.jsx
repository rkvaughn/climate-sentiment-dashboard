import Header from './Header'
import SentimentGauge from './SentimentGauge'
import ArticleList from './ArticleList'
import ModelInfo from './ModelInfo'
import { useDashboardData } from '../hooks/useDashboardData'

export default function Dashboard() {
  const { data, loading, error } = useDashboardData()
  const aggregation = data?.aggregation

  return (
    <div className="dashboard">
      <Header lastUpdated={data?.generated_at} />

      <div className="gauge-section">
        {loading ? (
          <p className="loading-text">Loading sentiment data...</p>
        ) : error ? (
          <p className="error-text">Could not load sentiment data — {error}</p>
        ) : aggregation ? (
          <div className="gauge-wrap">
            <SentimentGauge score={aggregation.avg_score} articleCount={aggregation.article_count} />
            <p className="gauge-caption">
              Average ClimateBERT score for articles published{' '}
              {new Date(`${aggregation.window_date}T00:00:00Z`).toLocaleDateString('en-US', {
                month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC',
              })}{' '}
              (UTC)
            </p>
          </div>
        ) : (
          <p className="loading-text">No sentiment data yet. The daily pipeline hasn't produced any scores.</p>
        )}
      </div>

      {!loading && !error && (
        <ArticleList articles={data?.articles ?? []} sources={data?.sources ?? {}} />
      )}

      <ModelInfo model={data?.model} />
    </div>
  )
}
