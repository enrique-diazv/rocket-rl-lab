import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { EvaluationRecord } from '../schemas/evaluations'

type EvaluationEpisodeChartProps = {
  episodes: EvaluationRecord['episodes']
  metric: 'total_reward' | 'steps'
}

export function EvaluationEpisodeChart({
  episodes,
  metric,
}: EvaluationEpisodeChartProps) {
  const rewardMetric = metric === 'total_reward'
  const title = rewardMetric
    ? 'Recompensa original por seed'
    : 'Duración por seed (pasos)'
  const valueLabel = rewardMetric
    ? 'Recompensa original'
    : 'Pasos del episodio'

  return (
    <figure style={{ margin: 0 }}>
      <h3>{title}</h3>

      <ResponsiveContainer width="100%" height={300} minWidth={0}>
        <BarChart
          data={episodes}
          margin={{ top: 10, right: 20, bottom: 10, left: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="seed" />
          <YAxis allowDecimals={rewardMetric} />
          <Tooltip
            formatter={value =>
              typeof value === 'number'
                ? value.toFixed(rewardMetric ? 2 : 0)
                : value
            }
          />
          <ReferenceLine y={0} stroke="#94a3b8" />
          <Bar
            dataKey={metric}
            name={valueLabel}
            fill={rewardMetric ? '#38bdf8' : '#a78bfa'}
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </figure>
  )
}