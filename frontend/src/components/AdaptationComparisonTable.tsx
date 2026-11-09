import type { AdaptationJob } from '../schemas/adaptation'
import { adaptationStatusLabels, formatThresholdSteps } from '../presentation/adaptation'
const columns = [
  'Agente',
  'Estado',
  'Pasos adicionales',
  'Pasos hasta criterio',
  'Éxito',
  'Recompensa original media',
  'Tiempo registrado (s)',
]

const cellStyle = {
  padding: '0.5rem',
  textAlign: 'right',
} as const

type AdaptationComparisonTableProps = {
  jobs: AdaptationJob[]
}

export function AdaptationComparisonTable({
  jobs,
}: AdaptationComparisonTableProps) {
  return (
    <div
      role="region"
      aria-label="Comparación de agentes"
      tabIndex={0}
      style={{ maxWidth: '100%', overflow: 'auto' }}
    >
      <table
        style={{
          width: '100%',
          minWidth: 960,
          borderCollapse: 'collapse',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        <caption>Última evaluación registrada por agente.</caption>

        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column} scope="col" style={cellStyle}>
                {column}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {jobs.map((job) => {
            const progress = job.progress
            const evaluation = progress?.last_evaluation

            return (
              <tr key={job.id}>
                <th scope="row" style={cellStyle}>
                  {job.agent}
                </th>

                <td style={cellStyle}>
                  {adaptationStatusLabels[job.status]}
                </td>

                <td style={cellStyle}>
                  {progress?.extra_training_timesteps.toLocaleString(
                    'es-MX',
                  ) ?? 'Sin registrar'}
                </td>

                <td style={cellStyle}>
                  {formatThresholdSteps(job)}
                </td>

                <td style={cellStyle}>
                  {evaluation
                    ? `${(evaluation.success_rate * 100).toFixed(1)}%`
                    : 'Sin evaluación'}
                </td>

                <td style={cellStyle}>
                  {evaluation
                    ? evaluation.mean_original_reward.toFixed(2)
                    : 'Sin evaluación'}
                </td>

                <td style={cellStyle}>
                  {progress
                    ? progress.elapsed_wall_seconds.toFixed(1)
                    : 'Sin registrar'}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}