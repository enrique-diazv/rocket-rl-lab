import { lazy, Suspense, useState } from 'react'
import { getTrainingProgress } from '../services/training'
import type { TrainingPoint } from '../schemas/training'
import { TrainingDataTable } from './TrainingDataTable'

const TrainingChart = lazy(() =>
  import('./TrainingChart').then(chartModule => ({
    default: chartModule.TrainingChart,
  })),
)

type TrainingProgressProps = {
  runId: string
}

export function TrainingProgress({
  runId,
}: TrainingProgressProps) {
  const [points, setPoints] = useState<TrainingPoint[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadProgress() {
    setLoading(true)
    setError('')
    setPoints(null)

    try {
      setPoints(await getTrainingProgress(runId))
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudieron cargar las métricas del entrenamiento.',
      )
    } finally {
      setLoading(false)
    }
  }

  const lastPoint = points?.at(-1)

  return (
    <section aria-busy={loading}>
      <h2>Curvas de entrenamiento</h2>

      <p>
        Para comparar políticas, consulta también los resultados
        de evaluación con recompensa original.
      </p>

      <button
        type="button"
        onClick={handleLoadProgress}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar métricas'}
      </button>

      {error && <p role="alert">{error}</p>}

      {points?.length === 0 && (
        <p role="status">
          Todavía no hay mediciones disponibles. Puedes volver
          a cargar las métricas más adelante.
        </p>
      )}

      {points && lastPoint && (
        <div>
          <p>Registros disponibles: {points.length}</p>
          <p>
            Pasos del último registro:{' '}
            {lastPoint.timesteps.toLocaleString('es-MX')}
          </p>
          <p>
            Última recompensa media de entrenamiento:{' '}
            {lastPoint.mean_episode_reward.toFixed(2)}
          </p>
          <p>
            Última duración media:{' '}
            {lastPoint.mean_episode_length.toFixed(2)} pasos
          </p>

          <Suspense fallback={<p role="status">Cargando gráficas...</p>}>
            <TrainingChart
              points={points}
              metric="mean_episode_reward"
            />
            <TrainingChart
              points={points}
              metric="mean_episode_length"
            />
          </Suspense>

          <TrainingDataTable points={points} />
        </div>
      )}
    </section>
  )
}