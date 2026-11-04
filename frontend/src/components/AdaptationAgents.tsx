import { useState } from 'react'
import type { AdaptationAgent } from '../schemas/adaptation'
import { getAdaptationAgents } from '../services/adaptation'

export function AdaptationAgents() {
  const [agents, setAgents] = useState<AdaptationAgent[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadAgents() {
    setLoading(true)
    setError('')

    try {
      const availableAgents = await getAdaptationAgents()
      setAgents(availableAgents)
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudieron consultar los agentes.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section aria-labelledby="adaptation-agents-title">
      <h2 id="adaptation-agents-title">Agentes de adaptación</h2>

      <button
        type="button"
        onClick={handleLoadAgents}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar agentes'}
      </button>

      {error && <p role="alert">{error}</p>}

      {agents?.length === 0 && (
        <p>No hay agentes disponibles.</p>
      )}

      {agents !== null && agents.length > 0 && (
        <ul>
          {agents.map((agent) => (
            <li key={agent.id}>
              <strong>{agent.name}</strong>
              {' — '}
              {agent.checkpoint_available
                ? 'Checkpoint disponible'
                : 'Checkpoint no disponible'}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}