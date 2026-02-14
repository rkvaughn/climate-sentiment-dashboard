import { useState, useEffect, useCallback } from 'react'
import { supabase } from '../lib/supabase'

export function useArticles(limit = 20) {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchArticles = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data, error: sbError } = await supabase
        .from('articles')
        .select('id, source_id, title, url, published_at, sentiment_score, sentiment_label')
        .not('sentiment_score', 'is', null)
        .order('published_at', { ascending: false })
        .limit(limit)

      if (sbError) throw sbError
      setArticles(data || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    fetchArticles()
  }, [fetchArticles])

  return { articles, loading, error, refetch: fetchArticles }
}
