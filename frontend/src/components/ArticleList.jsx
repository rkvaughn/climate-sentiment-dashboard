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
  columbia_climate: 'Columbia Climate School',
  sabin_center: 'Sabin Center',
  yale_climate_connections: 'Yale Climate Connections',
  canary_media: 'Canary Media',
  climate_home_news: 'Climate Home News',
  mongabay: 'Mongabay',
  desmog: 'DeSmog',
  utility_dive: 'Utility Dive',
  cleantechnica: 'CleanTechnica',
  the_conversation: 'The Conversation',
  google_news_climate: 'Google News Climate',
}

const TIERS = [
  { key: 'negative', label: 'Negative', headerColor: '#f97316', test: (s) => s <= -0.2 },
  { key: 'neutral',  label: 'Neutral',  headerColor: '#eab308', test: (s) => s > -0.2 && s < 0.2 },
  { key: 'positive', label: 'Positive', headerColor: '#84cc16', test: (s) => s >= 0.2 },
]

function ArticleItem({ article }) {
  return (
    <li className="article-item">
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
  )
}

export default function ArticleList({ articles, loading, error }) {
  if (loading) return <p className="loading-text">Loading articles...</p>
  if (error) return <p className="error-text">Could not load articles — {error}</p>
  if (!articles.length) return <p className="loading-text">No scored articles yet. Try refreshing data.</p>

  const groups = TIERS.map((tier) => ({
    ...tier,
    articles: articles.filter((a) => a.sentiment_score != null && tier.test(a.sentiment_score)),
  })).filter((g) => g.articles.length > 0)

  return (
    <div className="article-list">
      <h2>Recent Articles</h2>
      <div className="article-columns">
        {groups.map((group) => (
          <div key={group.key} className="sentiment-group">
            <h3 className="sentiment-group-header" style={{ color: group.headerColor }}>
              {group.label}
              <span className="sentiment-group-count">{group.articles.length}</span>
            </h3>
            <ul>
              {group.articles.map((article) => (
                <ArticleItem key={article.id} article={article} />
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
