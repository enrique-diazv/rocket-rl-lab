import { useState, type SubmitEvent } from 'react'
import type { AdaptationExperiment } from '../schemas/adaptation'
import { getAdaptationExperiment } from '../services/adaptation'
import { AdaptationExperimentLive } from './AdaptationExperimentLive'

export function AdaptationExperimentViewer() {
  const [experimentId, setExperimentId] = useState('')
  const [experiment, setExperiment] = useState<AdaptationExperiment | null>(
    null,
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadExperiment(
    event: SubmitEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setExperiment(null)

    try {
      const loadedExperiment = await getAdaptationExperiment(experimentId)
      setExperiment(loadedExperiment)
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudo consultar el experimento.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section aria-busy={loading}>
      <h2>Consultar experimento</h2>

      <form onSubmit={handleLoadExperiment}>
        <label htmlFor="adaptation-experiment-id">
          UUID del experimento
        </label>

        <input
          id="adaptation-experiment-id"
          type="text"
          value={experimentId}
          onChange={(event) => setExperimentId(event.target.value)}
          autoCapitalize="none"
          spellCheck={false}
          required
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? 'Consultando...' : 'Consultar experimento'}
        </button>
      </form>

      {loading && <p role="status">Consultando experimento...</p>}
      {error && <p role="alert">{error}</p>}

      {experiment && (
        <AdaptationExperimentLive
          key={experiment.id}
          initialExperiment={experiment}
        />
      )}
    </section>
  )
}