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
    <div className="flight-playback">
      {frame && <EpisodeCanvas scene={episode.scene} frame={frame} />}

      <div className="flight-transport">
        <button type="button" onClick={togglePlayback}>
          {isPlaying ? 'Pausar' : 'Reproducir'}
        </button>

        <label>
          Paso {frameIndex} de {episode.steps}
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
      </div>

      <dl className="flight-stats">
        <div><dt>Semilla</dt><dd>{episode.seed}</dd></div>
        <div><dt>Recompensa</dt><dd>{episode.total_reward.toFixed(2)}</dd></div>
        <div><dt>Pasos</dt><dd>{episode.steps}</dd></div>
        <div><dt>Fotogramas</dt><dd>{episode.frames.length}</dd></div>
        <div><dt>Aterrizaje exitoso</dt><dd>{episode.success ? 'Sí' : 'No'}</dd></div>
      </dl>
    </div>
  )
}
