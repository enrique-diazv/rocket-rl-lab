import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { AdaptationJob } from '../schemas/adaptation'
import type { AdaptationEvaluationHistory } from '../state/adaptation'
import {
  AdaptationChartTooltip,
  type AdaptationChartMetric,
} from './AdaptationChartTooltip'

const agentStyles: Record<
  AdaptationJob['agent'],
  { stroke: string; dash: string }
> = {
  precision: { stroke: '#3b82f6', dash: '' },
  speed: { stroke: '#ea580c', dash: '4 3' },
  efficiency: { stroke: '#0d9488', dash: '8 3' },
  stability: { stroke: '#16a34a', dash: '2 3' },
  balanced: { stroke: '#a855f7', dash: '12 3' },
}

type AdaptationChartProps = {
  jobs: AdaptationJob[]
  history: AdaptationEvaluationHistory
  metric: AdaptationChartMetric
}

export function AdaptationChart({
  jobs,
  history,
  metric,
}: AdaptationChartProps) {
  const successMetric = metric === 'success_rate'
  const title = successMetric
    ? 'Éxito durante la adaptación'
    : 'Recompensa original durante la adaptación'
  const description = successMetric
    ? 'Eje horizontal: pasos adicionales de entrenamiento. Eje vertical: aterrizajes exitosos (%).'
    : 'Eje horizontal: pasos adicionales de entrenamiento. Eje vertical: recompensa original media.'

  const series = jobs.map((job) => ({
    job,
    points: history[job.id] ?? [],
  }))

  const maxTimesteps = Math.max(
    1,
    ...series.flatMap(({ points }) =>
      points.map((point) => point.extra_training_timesteps),
    ),
  )

  return (
    <figure style={{ margin: 0 }}>
      <figcaption>
        <h3>{title}</h3>
        <p>{description}</p>
      </figcaption>

      <ResponsiveContainer width="100%" height={320} minWidth={0}>
        <LineChart
          accessibilityLayer
          desc={description}
          margin={{ top: 20, right: 24, bottom: 16, left: 8 }}
        >
          <CartesianGrid
            stroke="var(--border)"
            strokeDasharray="3 3"
          />

          <XAxis
            dataKey="extra_training_timesteps"
            type="number"
            domain={[0, maxTimesteps]}
            allowDecimals={false}
            allowDuplicatedCategory={false}
            stroke="var(--text)"
            minTickGap={32}
            tickFormatter={(value: number) =>
              value.toLocaleString('es-MX')
            }
          />

          <YAxis
            width={72}
            stroke="var(--text)"
            domain={successMetric ? [0, 1] : ['auto', 'auto']}
            tickFormatter={(value: number) =>
              successMetric
                ? `${Math.round(value * 100)}%`
                : value.toLocaleString('es-MX')
            }
          />

          <Tooltip
            content={({ active, label }) => (
              <AdaptationChartTooltip
                active={active}
                label={label}
                jobs={jobs}
                history={history}
                metric={metric}
              />
            )}
          />

          <Legend />

          {successMetric && (
            <ReferenceLine
              y={0.9}
              label="Umbral: 90%"
              stroke="var(--text)"
              strokeDasharray="5 4"
            />
          )}

          {series.map(({ job, points }) => (
            <Line
              key={job.id}
              data={points}
              dataKey={metric}
              name={job.agent}
              type="linear"
              stroke={agentStyles[job.agent].stroke}
              strokeDasharray={agentStyles[job.agent].dash}
              strokeWidth={2}
              dot={{ r: 3 }}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </figure>
  )
}