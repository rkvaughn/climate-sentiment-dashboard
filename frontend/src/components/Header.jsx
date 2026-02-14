export default function Header({ lastUpdated }) {
  const formattedDate = lastUpdated
    ? new Date(lastUpdated).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  return (
    <header className="header">
      <h1>Climate Sentiment Meter</h1>
      <p className="subtitle">Daily climate news sentiment at a glance</p>
      {formattedDate && (
        <p className="last-updated">Last updated: {formattedDate}</p>
      )}
    </header>
  )
}
