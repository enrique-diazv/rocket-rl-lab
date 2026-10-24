import type { TrainingPoint } from '../schemas/training'

type TrainingDataTableProps = {
  points: TrainingPoint[]
}

export function TrainingDataTable({
  points,
}: TrainingDataTableProps) {
  return (
    <details>
      <summary>
        Ver valores numéricos ({points.length} registros)
      </summary>

      <div
        role="region"
        aria-label="Tabla de métricas de entrenamiento"
        tabIndex={0}
        style={{ maxHeight: 320, overflow: 'auto' }}
      >
        <table
          style={{
            width: '100%',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          <caption>Mediciones registradas por PPO</caption>

          <thead>
            <tr>
              <th scope="col">Pasos acumulados</th>
              <th scope="col">Recompensa media con ajustes</th>
              <th scope="col">Duración media (pasos)</th>
            </tr>
          </thead>

          <tbody>
            {points.map(point => (
              <tr key={point.timesteps}>
                <th scope="row">
                  {point.timesteps.toLocaleString('es-MX')}
                </th>
                <td>{point.mean_episode_reward.toFixed(2)}</td>
                <td>{point.mean_episode_length.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}