import { useState } from 'react'
import { getTrainingRuns } from '../services/training'
import type { TrainingSummary } from '../schemas/training'

type TrainingSelectorProps = {
  modelId: string
  selectedId: string
  onSelect: (runId: string) => void
}

export function TrainingSelector({
  modelId,
  selectedId,
  onSelect,
}: TrainingSelectorProps) {
  const [runs, setRuns] = useState<TrainingSummary[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadRuns() {
    setLoading(true)
    setError('')
    setRuns(null)
    onSelect('')

    try {
      setRuns(await getTrainingRuns(modelId))
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudieron consultar los entrenamientos.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Entrenamientos guardados</h2>

      <button
        type="button"
        onClick={handleLoadRuns}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar entrenamientos'}
      </button>

      {error && <p role="alert">{error}</p>}

      {runs?.length === 0 && (
        <p>No hay entrenamientos registrados para este modelo.</p>
      )}

      <label>
        Entrenamiento:
        <select
          value={selectedId}
          onChange={event => onSelect(event.target.value)}
          disabled={loading || runs === null || runs.length === 0}
        >
          <option value="">Selecciona un entrenamiento</option>
          {runs?.map(run => (
            <option key={run.id} value={run.id}>
              {new Date(run.created_at).toLocaleString('es-MX')}
              {' — presupuesto: '}
              {run.requested_timesteps.toLocaleString('es-MX')}
              {' pasos'}
            </option>
          ))}
        </select>
      </label>
    </section>
  )
}