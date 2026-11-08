import { useState } from 'react'
import { useEpisodePlayback } from '../hooks/useEpisodePlayback'
import type { EpisodeTrajectory } from '../schemas/episodes'
import { EpisodeCanvas } from './EpisodeCanvas'

type EpisodePlaybackProps = {
  episode: EpisodeTrajectory
}

export function EpisodePlayback({ episode }: EpisodePlaybackProps) {
  const [frameIndex, setFrameIndex] = useState(0)
  const frame = episode.frames[frameIndex]
  const { isPlaying, play, pause } = useEpisodePlayback(
    episode.scene.fps,
    episode.steps,
    setFrameIndex,
  )

  function togglePlayback() {
    if (isPlaying) {
      pause()
    } else {
      play(frameIndex)
    }
  }

  return (
    <div>
      <p>Seed: {episode.seed}</p>
      <p>Recompensa: {episode.total_reward.toFixed(2)}</p>
      <p>Pasos: {episode.steps}</p>
      <p>Fotogramas: {episode.frames.length}</p>
      <p>Aterrizaje exitoso: {episode.success ? 'Sí' : 'No'}</p>

      <button type="button" onClick={togglePlayback}>
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
          onChange={(event) => {
            pause()
            setFrameIndex(Number(event.target.value))
          }}
        />
      </label>

      {frame && <EpisodeCanvas scene={episode.scene} frame={frame} />}
    </div>
  )
}