import type { AdaptationJob } from '../schemas/adaptation'
import type { AdaptationEvaluationHistory } from '../state/adaptation'

export type AdaptationChartMetric =
  | 'success_rate'
  | 'mean_original_reward'

type AdaptationChartTooltipProps = {
  active: boolean
  label: string | number | undefined
  jobs: AdaptationJob[]
  history: AdaptationEvaluationHistory
  metric: AdaptationChartMetric
}

export function AdaptationChartTooltip({
  active,
  label,
  jobs,
  history,
  metric,
}: AdaptationChartTooltipProps) {
  if (!active || typeof label !== 'number') {
    return null
  }

  const measurements = jobs.flatMap((job) =>
    (history[job.id] ?? [])
      .filter((point) => point.extra_training_timesteps === label)
      .map((point) => ({
        jobId: job.id,
        agent: job.agent,
        point,
      })),
  )

  if (measurements.length === 0) {
    return null
  }

  return (
    <div
      style={{
        backgroundColor: 'var(--bg)',
        color: 'var(--text-h)',
        border: '1px solid var(--border)',
        padding: 12,
      }}
    >
      <p>Pasos adicionales: {label.toLocaleString('es-MX')}</p>

      <ul>
        {measurements.map(({ jobId, agent, point }) => (
          <li key={`${jobId}-${point.evaluation_index}`}>
            {agent} · Evaluación {point.evaluation_index}:{' '}
            {metric === 'success_rate'
              ? `${(point.success_rate * 100).toFixed(1)}%`
              : point.mean_original_reward.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  )
}