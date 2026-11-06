import { useState } from 'react'
import type {
  AdaptationExperiment,
  AdaptationExperimentRequest,
} from './schemas/adaptation'
import {
  createAdaptationExperiment,
  getAdaptationExperiment,
} from './services/adaptation'
import { AdaptationAgents } from './components/AdaptationAgents'
import { AdaptationExperimentForm } from './components/AdaptationExperimentForm'
import { AdaptationExperimentViewer } from './components/AdaptationExperimentViewer'
import { AdaptationExperimentLive } from './components/AdaptationExperimentLive'
import { OperatorTokenInput } from './components/OperatorTokenInput'

function AdaptationChallenge() {
  const [experiment, setExperiment] =
    useState<AdaptationExperiment | null>(null)
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  const [operatorToken, setOperatorToken] = useState('')

  const busy = loading || creating

  async function handleLoadExperiment(experimentId: string): Promise<void> {
    if (busy) return

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

  async function handleCreateExperiment(
    config: AdaptationExperimentRequest,
  ): Promise<void> {
    if (busy) return

    setCreating(true)
    setError('')

    try {
      const createdExperiment = await createAdaptationExperiment(
        config,
        operatorToken,
      )
      setExperiment(createdExperiment)
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudo crear el experimento.',
      )
    } finally {
      setCreating(false)
    }
  }

  return (
    <main>
      <h1>Desafío de adaptación</h1>
      <p>
        Configura un escenario y sigue la adaptación de los cinco agentes.
      </p>

      <AdaptationAgents />

      <OperatorTokenInput
        token={operatorToken}
        onTokenChange={setOperatorToken}
      />

      <AdaptationExperimentForm
        disabled={busy}
        creating={creating}
        onCreate={handleCreateExperiment}
      />

      <AdaptationExperimentViewer
        loading={loading}
        disabled={busy}
        onLoad={handleLoadExperiment}
      />

      {error && <p role="alert">{error}</p>}

      {experiment && (
        <AdaptationExperimentLive
          key={experiment.id}
          initialExperiment={experiment}
        />
      )}
    </main>
  )
}

export default AdaptationChallenge