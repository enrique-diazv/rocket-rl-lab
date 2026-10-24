import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TrainingPoint } from '../schemas/training'

type TrainingChartProps = {
  points: TrainingPoint[]
  metric: 'mean_episode_reward' | 'mean_episode_length'
}

export function TrainingChart({
  points,
  metric,
}: TrainingChartProps) {
  const rewardMetric = metric === 'mean_episode_reward'
  const title = rewardMetric
    ? 'Recompensa durante el entrenamiento'
    : 'Duración de los episodios durante el entrenamiento'
  const valueLabel = rewardMetric
    ? 'Recompensa media'
    : 'Duración media (pasos)'
  const description = rewardMetric
    ? 'Eje horizontal: pasos acumulados. Eje vertical: recompensa media, incluidos los premios y penalizaciones adicionales.'
    : 'Eje horizontal: pasos acumulados. Eje vertical: duración media de los episodios, en pasos.'

  return (
    <figure style={{ margin: 0 }}>
      <figcaption>
        <h3 style={{ color: 'var(--text-h)' }}>{title}</h3>
        <p>{description}</p>
      </figcaption>

      <ResponsiveContainer width="100%" height={320} minWidth={0}>
        <LineChart
          accessibilityLayer
          desc={description}
          data={points}
          margin={{ top: 16, right: 20, bottom: 16, left: 8 }}
        >
          <CartesianGrid
            stroke="var(--border)"
            strokeDasharray="3 3"
          />
          <XAxis
            dataKey="timesteps"
            type="number"
            domain={['dataMin', 'dataMax']}
            stroke="var(--text)"
            minTickGap={32}
            tickFormatter={(value: number) =>
              value.toLocaleString('es-MX')
            }
          />
          <YAxis
            width={64}
            stroke="var(--text)"
            domain={rewardMetric ? ['auto', 'auto'] : [0, 'auto']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg)',
              borderColor: 'var(--border)',
              color: 'var(--text-h)',
            }}
            labelFormatter={label =>
              `Pasos acumulados: ${
                typeof label === 'number'
                  ? label.toLocaleString('es-MX')
                  : String(label)
              }`
            }
            formatter={value =>
              typeof value === 'number' ? value.toFixed(2) : value
            }
          />
          {rewardMetric && (
            <ReferenceLine
              y={0}
              stroke="var(--text)"
              strokeDasharray="3 3"
            />
          )}
          <Line
            type="linear"
            dataKey={metric}
            name={valueLabel}
            stroke="var(--accent)"
            strokeWidth={2}
            dot={points.length === 1}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </figure>
  )
}