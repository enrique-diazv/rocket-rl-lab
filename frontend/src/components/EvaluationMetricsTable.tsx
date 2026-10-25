import type { EvaluationRecord } from '../schemas/evaluations'

const metricColumns = [
  ['final_horizontal_error', 'Error final (u. mundo)'],
  ['engine_usage_cost', 'Costo de motores (relativo)'],
  ['pre_contact_speed', 'Velocidad previa (u. mundo/s)'],
  ['pre_contact_abs_angle', 'Inclinación previa (rad)'],
  ['pre_contact_angular_speed', 'Giro previo (rad/s)'],
] as const

const cellStyle = {
  padding: '0.5rem',
  textAlign: 'right',
} as const

type EvaluationMetricsTableProps = {
  episodes: EvaluationRecord['episodes']
}

function formatMetric(metric: number | null | undefined): string {
  return metric == null ? 'No medido' : metric.toFixed(3)
}

export function EvaluationMetricsTable({
  episodes,
}: EvaluationMetricsTableProps) {
  return (
    <details>
      <summary>
        Ver métricas por episodio ({episodes.length} episodios)
      </summary>

      <p>
        El error corresponde a la posición final, incluso en episodios
        fallidos. Velocidad, inclinación y giro corresponden al paso
        anterior al primer contacto detectado de las patas.
      </p>

      <div
        role="region"
        aria-label="Métricas de los episodios evaluados"
        tabIndex={0}
        style={{ maxWidth: '100%', maxHeight: 360, overflow: 'auto' }}
      >
        <table
          style={{
            width: '100%',
            minWidth: 960,
            borderCollapse: 'collapse',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          <caption>
            Mediciones por episodio. «No medido» indica un dato ausente.
          </caption>

          <thead>
            <tr>
              <th scope="col" style={cellStyle}>Seed</th>
              <th scope="col" style={cellStyle}>Resultado</th>
              <th scope="col" style={cellStyle}>Duración (pasos)</th>
              {metricColumns.map(([metricKey, label]) => (
                <th key={metricKey} scope="col" style={cellStyle}>
                  {label}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {episodes.map(episode => (
              <tr key={episode.seed}>
                <th scope="row" style={cellStyle}>{episode.seed}</th>
                <td style={cellStyle}>
                  {episode.success ? 'Éxito' : 'No exitoso'}
                </td>
                <td style={cellStyle}>
                  {episode.steps.toLocaleString('es-MX')}
                </td>
                {metricColumns.map(([metricKey]) => (
                  <td key={metricKey} style={cellStyle}>
                    {formatMetric(episode[metricKey])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}