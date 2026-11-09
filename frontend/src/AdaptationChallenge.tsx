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
    <main className="workspace">
      <header className="workspace-heading">
        <div>
          <h1>Desafío de adaptación</h1>
          <p>Compara cómo cinco agentes PPO se adaptan al mismo escenario de aterrizaje.</p>
        </div>
        <a className="lookup-shortcut" href="#saved-experiment">Consultar un experimento guardado</a>
      </header>

      <div className="command-desk">
        <AdaptationExperimentForm
          disabled={busy}
          creating={creating}
          onCreate={handleCreateExperiment}
          operatorAccess={
            <OperatorTokenInput token={operatorToken} onTokenChange={setOperatorToken} />
          }
        />

        <aside className="command-sidebar" aria-label="Consultas de adaptación">
          <AdaptationExperimentViewer
            loading={loading}
            disabled={busy}
            onLoad={handleLoadExperiment}
          />
          <AdaptationAgents />
        </aside>
      </div>

      {error && <p role="alert">{error}</p>}

      {experiment && (
        <AdaptationExperimentLive
          key={experiment.id}
          initialExperiment={experiment}
          operatorToken={operatorToken}
        />
      )}
    </main>
  )
}

export default AdaptationChallenge
