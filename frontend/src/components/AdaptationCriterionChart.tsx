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
    <figure className="criterion-chart">
      <figcaption>
        <h3>Pasos hasta el criterio</h3>
        <p>Una marca en 0 indica que el agente ya cumplía el criterio al inicio.</p>
      </figcaption>

      <ul>
        {rows.map(({ job, steps }) => (
          <li key={job.id}>
            <span>{job.agent}</span>
            <span className="criterion-chart__track" aria-hidden="true">
              {steps !== null && (
                <span
                  className="criterion-chart__bar"
                  data-zero={steps === 0}
                  style={{ width: `${(steps / scale) * 100}%` }}
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
