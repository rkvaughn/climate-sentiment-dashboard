import { useState, useEffect, useCallback } from 'react'
import { supabase } from '../lib/supabase'

export function useSentiment() {
  const [sentiment, setSentiment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchSentiment = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data, error: sbError } = await supabase
        .from('sentiment_aggregations')
        .select('*')
        .eq('time_window', 'daily')
        .order('window_date', { ascending: false })
        .limit(1)
        .single()

      if (sbError && sbError.code !== 'PGRST116') throw sbError
      setSentiment(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSentiment()
  }, [fetchSentiment])

  return { sentiment, loading, error, refetch: fetchSentiment }
}
