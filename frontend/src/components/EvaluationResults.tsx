import { lazy, Suspense, useState } from 'react'
import { getEvaluation } from '../services/evaluations'
import type { EvaluationRecord } from '../schemas/evaluations'

const EvaluationEpisodeChart = lazy(() =>
  import('./EvaluationEpisodeChart').then(chartModule => ({
    default: chartModule.EvaluationEpisodeChart,
  })),
)

type EvaluationResultsProps = {
  evaluationId: string
  modelId: string
}

export function EvaluationResults({
  evaluationId,
  modelId,
}: EvaluationResultsProps) {
  const [record, setRecord] = useState<EvaluationRecord | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadResults() {
    setLoading(true)
    setError('')
    setRecord(null)

    try {
      const result = await getEvaluation(evaluationId)

      if (result.model_id !== modelId) {
        throw new Error(
          'La evaluación no pertenece al modelo seleccionado.',
        )
      }

      setRecord(result)
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudieron cargar los resultados.',
      )
    } finally {
      setLoading(false)
    }
  }

  const episodes = record?.episodes ?? []
  const successfulEpisodes = episodes.filter(
    episode => episode.success,
  ).length

  const meanReward = episodes.length > 0
    ? episodes.reduce(
      (total, episode) => total + episode.total_reward,
      0,
    ) / episodes.length
    : 0

  const successRate = episodes.length > 0
    ? successfulEpisodes / episodes.length * 100
    : 0

  return (
    <section>
      <h2>Resultados de evaluación</h2>

      <button
        type="button"
        onClick={handleLoadResults}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar resultados'}
      </button>

      {error && <p role="alert">{error}</p>}

      {record && (
        <div>
          <p>
            Pasos entrenados: {record.training_timesteps.toLocaleString('es-MX')}
          </p>
          <p>Episodios evaluados: {episodes.length}</p>
          <p>Recompensa original media: {meanReward.toFixed(2)}</p>
          <p>
            Aterrizajes exitosos: {successfulEpisodes}/{episodes.length}
          </p>
          <p>Tasa de éxito: {successRate.toFixed(1)} %</p>
          <Suspense fallback={<p role="status">Cargando gráficas...</p>}>
            <EvaluationEpisodeChart
              episodes={episodes}
              metric="total_reward"
            />
            <EvaluationEpisodeChart
              episodes={episodes}
              metric="steps"
            />
          </Suspense>
        </div>
      )}
    </section>
  )
}