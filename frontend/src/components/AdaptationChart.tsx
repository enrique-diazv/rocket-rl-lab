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
  precision: { stroke: '#ffad64', dash: '' },
  speed: { stroke: '#d5d7dc', dash: '4 3' },
  efficiency: { stroke: '#aeb2bb', dash: '8 3' },
  stability: { stroke: '#edf0f4', dash: '2 3' },
  balanced: { stroke: '#848a96', dash: '12 3' },
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
    <figure className="adaptation-chart">
      <figcaption>
        <h3>{title}</h3>
        <p>{description}</p>
      </figcaption>

      <div className="adaptation-plot">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <LineChart
            accessibilityLayer
            desc={description}
            margin={{ top: 14, right: 16, bottom: 6, left: 0 }}
          >
            <CartesianGrid
              stroke="var(--border)"
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="extra_training_timesteps"
              type="number"
              domain={[0, maxTimesteps]}
              allowDecimals={false}
              allowDuplicatedCategory={false}
              stroke="var(--text)"
              tickLine={false}
              minTickGap={32}
              tickFormatter={(value: number) =>
                value.toLocaleString('es-MX')
              }
            />

            <YAxis
              width={51}
              stroke="var(--text)"
              tickLine={false}
              axisLine={false}
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

            {successMetric && (
              <ReferenceLine
                y={0.9}
                label={{
                  value: 'Umbral 90%',
                  position: 'insideTopRight',
                  fill: 'var(--text)',
                  fontSize: 12,
                }}
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
      </div>

      <ul className="chart-key" aria-label="Agentes en la gráfica">
        {jobs.map(({ id, agent }) => (
          <li key={id}>
            <svg width="26" height="10" viewBox="0 0 26 10" aria-hidden="true">
              <line
                x1="0"
                y1="5"
                x2="26"
                y2="5"
                stroke={agentStyles[agent].stroke}
                strokeDasharray={agentStyles[agent].dash}
                strokeWidth="2"
              />
            </svg>
            {agent}
          </li>
        ))}
      </ul>
    </figure>
  )
}
