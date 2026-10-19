import { useState } from 'react'
import { getEvaluations } from '../services/evaluations'
import type { EvaluationSummary } from '../schemas/evaluations'

type EvaluationSelectorProps = {
  modelId: string
  selectedId: string
  onSelect: (evaluationId: string) => void
}

export function EvaluationSelector({
  modelId,
  selectedId,
  onSelect,
}: EvaluationSelectorProps) {
  const [evaluations, setEvaluations] = useState<
    EvaluationSummary[] | null
  >(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadEvaluations() {
    setLoading(true)
    setError('')
    setEvaluations(null)
    onSelect('')

    try {
      setEvaluations(await getEvaluations(modelId))
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudieron consultar las evaluaciones.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Evaluaciones guardadas</h2>

      <button
        type="button"
        onClick={handleLoadEvaluations}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar evaluaciones'}
      </button>

      {error && <p role="alert">{error}</p>}

      {evaluations?.length === 0 && (
        <p>No hay evaluaciones guardadas para este modelo.</p>
      )}

      <label>
        Evaluación:
        <select
          value={selectedId}
          onChange={event => onSelect(event.target.value)}
          disabled={
            loading || evaluations === null || evaluations.length === 0
          }
        >
          <option value="">Selecciona una evaluación</option>
          {evaluations?.map(evaluation => (
            <option key={evaluation.id} value={evaluation.id}>
              {new Date(evaluation.created_at).toLocaleString('es-MX')}
              {' — '}
              {evaluation.episode_count} episodios
            </option>
          ))}
        </select>
      </label>
    </section>
  )
}