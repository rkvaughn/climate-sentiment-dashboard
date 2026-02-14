import { useState } from 'react'

export default function RefreshButton({ onComplete }) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  async function handleRefresh() {
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch(`${apiUrl}/api/ingest/run`, { method: 'POST' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setResult(
        `Fetched ${data.articles_fetched}, inserted ${data.articles_inserted}, scored ${data.articles_scored}`
      )
      if (onComplete) onComplete()
    } catch (e) {
      setResult(`Error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="refresh-section">
      <button
        className="refresh-button"
        onClick={handleRefresh}
        disabled={loading}
      >
        {loading ? 'Running pipeline...' : 'Refresh Data'}
      </button>
      {result && <p className="refresh-result">{result}</p>}
    </div>
  )
}
