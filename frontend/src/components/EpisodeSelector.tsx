import { useState } from 'react'
import { getEpisodes } from '../services/api'
import type { EpisodeSummary } from '../schemas/episodes'

type EpisodeSelectorProps = {
  modelId: string
  selectedId: string
  onSelect: (episodeId: string) => void
}

export function EpisodeSelector({
  modelId,
  selectedId,
  onSelect,
}: EpisodeSelectorProps) {
  const [episodes, setEpisodes] = useState<EpisodeSummary[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadEpisodes() {
    setLoading(true)
    setError('')
    setEpisodes(null)
    onSelect('')

    try {
      setEpisodes(await getEpisodes(modelId))
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudieron consultar los episodios.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Episodios grabados</h2>

      <button
        type="button"
        onClick={handleLoadEpisodes}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar episodios'}
      </button>

      {error && <p role="alert">{error}</p>}

      {episodes?.length === 0 && (
        <p>No hay episodios guardados para este modelo.</p>
      )}

      <label>
        Episodio:
        <select
          value={selectedId}
          onChange={(event) => onSelect(event.target.value)}
          disabled={loading || episodes === null || episodes.length === 0}
        >
          <option value="">Selecciona un episodio</option>
          {episodes?.map((episode) => (
            <option key={episode.id} value={episode.id}>
              Seed {episode.seed}: recompensa {episode.total_reward.toFixed(2)}
            </option>
          ))}
        </select>
      </label>
    </section>
  )
}