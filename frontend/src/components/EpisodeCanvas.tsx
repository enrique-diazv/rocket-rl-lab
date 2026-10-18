import { useEffect, useRef } from 'react'
import type {
  FrameSnapshot,
  SceneSnapshot,
} from '../schemas/episodes'
import { drawEpisodeFrame } from '../rendering/drawEpisodeFrame'

type EpisodeCanvasProps = {
  scene: SceneSnapshot
  frame: FrameSnapshot
}

export function EpisodeCanvas({
  scene,
  frame,
}: EpisodeCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const context = canvasRef.current?.getContext('2d')

    if (context) {
      drawEpisodeFrame(context, scene, frame)
    }
  }, [scene, frame])

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={400}
      role="img"
      aria-label="Escenario y posición de la nave en el episodio grabado"
      style={{
        display: 'block',
        width: '100%',
        maxWidth: 600,
        height: 'auto',
      }}
    >
      Tu navegador necesita soporte para Canvas.
    </canvas>
  )
}