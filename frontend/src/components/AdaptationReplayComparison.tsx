import { useState } from 'react'
import type { AdaptationJob, AdaptationReplays } from '../schemas/adaptation'
import { getAdaptationReplays } from '../services/adaptation'
import { EpisodePlayback } from './EpisodePlayback'

type AdaptationReplayComparisonProps = {
  experimentId: string
  jobs: AdaptationJob[]
}

export function AdaptationReplayComparison({
  experimentId,
  jobs,
}: AdaptationReplayComparisonProps) {
  const [agent, setAgent] = useState('')
  const [pair, setPair] = useState<AdaptationReplays | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const completedJobs = jobs.filter(
    (job) =>
      job.status === 'already_adapted' ||
      job.status === 'adapted' ||
      job.status === 'budget_reached',
  )
  const selectedJob = completedJobs.find((job) => job.agent === agent)

  async function handleLoadReplays() {
    if (!selectedJob) return

    setLoading(true)
    setError('')
    setPair(null)

    try {
      setPair(await getAdaptationReplays(experimentId, selectedJob.agent))
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : 'No se pudieron cargar los replays.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section aria-labelledby="adaptation-replays-title">
      <h2 id="adaptation-replays-title">Replays de adaptación</h2>

      {completedJobs.length === 0 ? (
        <p>Todavía no hay agentes con una adaptación finalizada.</p>
      ) : (
        <>
          <label>
            Agente
            <select
              value={agent}
              disabled={loading}
              onChange={(event) => {
                setAgent(event.target.value)
                setPair(null)
                setError('')
              }}
            >
              <option value="">Selecciona un agente</option>
              {completedJobs.map((job) => (
                <option key={job.id} value={job.agent}>
                  {job.agent}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={handleLoadReplays}
            disabled={!selectedJob || loading}
          >
            {loading ? 'Cargando replays...' : 'Cargar replays'}
          </button>
        </>
      )}

      {error && <p role="alert">{error}</p>}

      {pair && (
        <>
          <p>
            Ambas trayectorias usan la semilla {pair.before.seed} y el mismo escenario.
          </p>
          {pair.extra_training_timesteps === 0 && (
            <p>Ambas trayectorias corresponden al mismo checkpoint.</p>
          )}

          <div>
            <h3>Antes de la adaptación</h3>
            <EpisodePlayback episode={pair.before} />
          </div>
          <div>
            <h3>Después de la adaptación</h3>
            <EpisodePlayback episode={pair.after} />
          </div>
        </>
      )}
    </section>
  )
}