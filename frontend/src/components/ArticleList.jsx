function sentimentColor(score) {
  if (score <= -0.5) return '#dc2626'
  if (score <= -0.2) return '#f97316'
  if (score <= 0.2) return '#eab308'
  if (score <= 0.5) return '#84cc16'
  return '#22c55e'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function probabilityTooltip(article) {
  const p = article.probabilities
  if (!p) return article.sentiment_label
  const pct = (v) => `${Math.round(v * 100)}%`
  return `Risk ${pct(p.risk)} · Neutral ${pct(p.neutral)} · Opportunity ${pct(p.opportunity)}`
}

const GROUPS = [
  { key: 'risk', label: 'Risk', headerColor: '#f97316' },
  { key: 'neutral', label: 'Neutral', headerColor: '#eab308' },
  { key: 'opportunity', label: 'Opportunity', headerColor: '#84cc16' },
]

function ArticleItem({ article, sourceName }) {
  return (
    <li className="article-item">
      <span
        className="sentiment-dot"
        style={{ backgroundColor: sentimentColor(article.sentiment_score) }}
        title={probabilityTooltip(article)}
      />
      <div className="article-info">
        <a href={article.url} target="_blank" rel="noopener noreferrer">
          {article.title}
        </a>
        <span className="article-meta">
          {sourceName}
          {article.published_at && (
            <span className="nowrap">{` · ${formatDate(article.published_at)}`}</span>
          )}
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

export default function ArticleList({ articles, sources }) {
  if (!articles.length) return <p className="loading-text">No scored articles yet.</p>

  const groups = GROUPS.map((group) => ({
    ...group,
    articles: articles.filter((a) => a.sentiment_label === group.key),
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
                <ArticleItem
                  key={article.url}
                  article={article}
                  sourceName={sources[article.source_id] || article.source_id}
                />
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
