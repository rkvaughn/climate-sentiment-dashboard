function sentimentColor(score) {
  if (score <= -0.5) return '#dc2626'
  if (score <= -0.2) return '#f97316'
  if (score <= 0.2) return '#eab308'
  if (score <= 0.5) return '#84cc16'
  return '#22c55e'
}

function sentimentText(label) {
  if (!label) return ''
  return label.replace(/_/g, ' ')
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

const SOURCE_NAMES = {
  carbon_brief: 'Carbon Brief',
  guardian_environment: 'The Guardian',
  inside_climate_news: 'Inside Climate News',
  grist: 'Grist',
}

export default function ArticleList({ articles, loading }) {
  if (loading) return <p className="loading-text">Loading articles...</p>
  if (!articles.length) return <p className="loading-text">No scored articles yet. Try refreshing data.</p>

  return (
    <div className="article-list">
      <h2>Recent Articles</h2>
      <ul>
        {articles.map((article) => (
          <li key={article.id} className="article-item">
            <span
              className="sentiment-dot"
              style={{ backgroundColor: sentimentColor(article.sentiment_score) }}
              title={`${article.sentiment_score?.toFixed(2)} — ${sentimentText(article.sentiment_label)}`}
            />
            <div className="article-info">
              <a href={article.url} target="_blank" rel="noopener noreferrer">
                {article.title}
              </a>
              <span className="article-meta">
                {SOURCE_NAMES[article.source_id] || article.source_id}
                {article.published_at && ` · ${formatDate(article.published_at)}`}
                {article.sentiment_score != null && (
                  <span
                    className="score-badge"
                    style={{ color: sentimentColor(article.sentiment_score) }}
                  >
                    {article.sentiment_score > 0 ? '+' : ''}
                    {article.sentiment_score.toFixed(2)}
                  </span>
                )}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
