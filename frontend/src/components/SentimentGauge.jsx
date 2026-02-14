import { useRef, useEffect } from 'react'
import * as d3 from 'd3'

const WIDTH = 300
const HEIGHT = 180
const MARGIN = 20
const RADIUS = (WIDTH - MARGIN * 2) / 2
const NEEDLE_LENGTH = RADIUS - 15

const LABELS = [
  { angle: -80, text: 'Alarming' },
  { angle: -40, text: 'Negative' },
  { angle: 0, text: 'Neutral' },
  { angle: 40, text: 'Positive' },
  { angle: 80, text: 'Hopeful' },
]

export default function SentimentGauge({ score, articleCount }) {
  const svgRef = useRef()

  useEffect(() => {
    if (score === null || score === undefined) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const g = svg
      .attr('viewBox', `0 0 ${WIDTH} ${HEIGHT}`)
      .append('g')
      .attr('transform', `translate(${WIDTH / 2}, ${HEIGHT - MARGIN})`)

    // Color gradient arc segments
    const arcGen = d3.arc().innerRadius(RADIUS - 30).outerRadius(RADIUS)

    const segments = [
      { start: -90, end: -54, color: '#dc2626' },
      { start: -54, end: -18, color: '#f97316' },
      { start: -18, end: 18, color: '#eab308' },
      { start: 18, end: 54, color: '#84cc16' },
      { start: 54, end: 90, color: '#22c55e' },
    ]

    segments.forEach(({ start, end, color }) => {
      g.append('path')
        .attr(
          'd',
          arcGen({
            startAngle: (start * Math.PI) / 180,
            endAngle: (end * Math.PI) / 180,
          })
        )
        .attr('fill', color)
        .attr('opacity', 0.8)
    })

    // Labels
    LABELS.forEach(({ angle, text }) => {
      const rad = (angle * Math.PI) / 180
      const x = Math.sin(rad) * (RADIUS + 12)
      const y = -Math.cos(rad) * (RADIUS + 12)
      g.append('text')
        .attr('x', x)
        .attr('y', y)
        .attr('text-anchor', 'middle')
        .attr('font-size', '9px')
        .attr('fill', '#94a3b8')
        .text(text)
    })

    // Needle — score [-1, 1] maps to angle [-90, 90] degrees
    const clampedScore = Math.max(-1, Math.min(1, score))
    const targetAngle = clampedScore * 90

    const needle = g
      .append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', 0)
      .attr('y2', -NEEDLE_LENGTH)
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', 2.5)
      .attr('stroke-linecap', 'round')
      .attr('transform', 'rotate(-90)')

    needle
      .transition()
      .duration(1200)
      .ease(d3.easeElasticOut.amplitude(1).period(0.5))
      .attr('transform', `rotate(${targetAngle})`)

    // Center dot
    g.append('circle').attr('r', 5).attr('fill', '#e2e8f0')

    // Score text
    g.append('text')
      .attr('y', -30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '24px')
      .attr('font-weight', 'bold')
      .attr('fill', '#f8fafc')
      .text(score.toFixed(2))

    // Article count
    if (articleCount) {
      g.append('text')
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .attr('font-size', '11px')
        .attr('fill', '#94a3b8')
        .text(`${articleCount} articles`)
    }
  }, [score, articleCount])

  return (
    <div className="gauge-container">
      <svg ref={svgRef} />
    </div>
  )
}
