import { useEpisodePlayback } from '../hooks/useEpisodePlayback'
import { useState } from 'react'
import { getEpisode } from '../services/api'
import type { EpisodeRecord } from '../schemas/episodes'
import { EpisodeCanvas } from './EpisodeCanvas'

type EpisodePlayerProps = {
  episodeId: string
  modelId: string
}

export function EpisodePlayer({
  episodeId,
  modelId,
}: EpisodePlayerProps) {
  const [record, setRecord] = useState<EpisodeRecord | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [frameIndex, setFrameIndex] = useState(0)
  const episode = record?.episode
  const frame = episode?.frames[frameIndex]

  const { isPlaying, play, pause } = useEpisodePlayback(
    episode?.scene.fps ?? 1,
    episode?.steps ?? 0,
    setFrameIndex,
  )

  async function handleLoadEpisode() {
    pause()
    setLoading(true)
    setError('')
    setRecord(null)
    setFrameIndex(0)

    try {
      const result = await getEpisode(episodeId)

      if (result.model_id !== modelId) {
        throw new Error('El episodio no pertenece al modelo seleccionado.')
      }

      setRecord(result)
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
    <section>
      <h2>Reproducción del episodio</h2>

      <button
        type="button"
        onClick={handleLoadEpisode}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar trayectoria'}
      </button>

      {error && <p role="alert">{error}</p>}

      {episode && (
        <div>
          <p>Seed: {episode.seed}</p>
          <p>Recompensa: {episode.total_reward.toFixed(2)}</p>
          <p>Pasos: {episode.steps}</p>
          <p>Fotogramas: {episode.frames.length}</p>
          <p>Aterrizaje exitoso: {episode.success ? 'Sí' : 'No'}</p>

          <button
            type="button"
            onClick={() => {
              if (isPlaying) {
                pause()
              } else {
                play(frameIndex)
              }
            }}
          >
            {isPlaying ? 'Pausar' : 'Reproducir'}
          </button>

          <label>
            Paso: {frameIndex} de {episode.steps}
            <input
              type="range"
              min={0}
              max={episode.steps}
              step={1}
              value={frameIndex}
              onChange={event => {
                pause()
                setFrameIndex(Number(event.target.value))
              }}
            />
          </label>

          {frame && (
            <EpisodeCanvas
              scene={episode.scene}
              frame={frame}
            />
          )}
        </div>
      )}

    </section>
  )
}