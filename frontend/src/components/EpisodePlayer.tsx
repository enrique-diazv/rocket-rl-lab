import { useState } from 'react'
import type { EpisodeTrajectory } from '../schemas/episodes'
import { getEpisode } from '../services/api'
import { EpisodePlayback } from './EpisodePlayback'

type EpisodePlayerProps = {
  episodeId: string
  modelId: string
}

export function EpisodePlayer({ episodeId, modelId }: EpisodePlayerProps) {
  const [episode, setEpisode] = useState<EpisodeTrajectory | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadEpisode() {
    setLoading(true)
    setError('')
    setEpisode(null)

    try {
      const result = await getEpisode(episodeId)
      if (result.model_id !== modelId) {
        throw new Error('El episodio no pertenece al modelo seleccionado.')
      }

      setEpisode(result.episode)
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudo cargar la trayectoria.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel flight-panel">
      <header className="panel-heading">
        <h2>Reproducción del episodio</h2>

        <button type="button" onClick={handleLoadEpisode} disabled={loading}>
          {loading ? 'Cargando...' : 'Cargar trayectoria'}
        </button>
      </header>

      {error && <p role="alert">{error}</p>}
      {!episode && !error && !loading && (
        <p>Carga los fotogramas del episodio seleccionado para reproducir el vuelo.</p>
      )}
      {episode && <EpisodePlayback episode={episode} />}
    </section>
  )
}
