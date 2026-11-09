import { formatThresholdSteps } from '../presentation/adaptation'
import type { AdaptationJob } from '../schemas/adaptation'

type AdaptationCriterionChartProps = {
  jobs: AdaptationJob[]
}

export function AdaptationCriterionChart({ jobs }: AdaptationCriterionChartProps) {
  const rows = jobs.map((job) => ({
    job,
    steps: job.progress?.time_to_threshold_steps ?? null,
  }))
  const scale = Math.max(1, ...rows.map(({ steps }) => steps ?? 0))

  return (
    <figure style={{ margin: 0 }}>
      <figcaption>
        <h3>Pasos hasta el criterio</h3>
        <p>Una marca en 0 indica que el agente ya cumplía el criterio al inicio.</p>
      </figcaption>

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {rows.map(({ job, steps }) => (
          <li
            key={job.id}
            style={{
              display: 'grid',
              gridTemplateColumns: '5rem minmax(1rem, 1fr) 7rem',
              alignItems: 'center',
              gap: '0.5rem',
              marginBlock: '0.5rem',
            }}
          >
            <span>{job.agent}</span>
            <span
              aria-hidden="true"
              style={{
                display: 'flex',
                alignItems: 'center',
                minHeight: '1rem',
                borderBottom: '1px solid var(--border)',
              }}
            >
              {steps !== null && (
                <span
                  style={{
                    width: `${(steps / scale) * 100}%`,
                    height: '0.65rem',
                    background: 'var(--accent)',
                    borderInlineStart: steps === 0 ? '2px solid var(--accent)' : undefined,
                  }}
                />
              )}
            </span>
            <span>{formatThresholdSteps(job)}</span>
          </li>
        ))}
      </ul>
    </figure>
  )
}