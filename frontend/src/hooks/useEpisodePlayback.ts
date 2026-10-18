import { useEffect, useRef, useState } from 'react'

export function useEpisodePlayback(
  fps: number,
  lastFrame: number,
  onFrame: (index: number) => void,
) {
  const [isPlaying, setIsPlaying] = useState(false)
  const animationRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [])

  function pause(): void {
    if (animationRef.current !== null) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }

    setIsPlaying(false)
  }

  function play(fromFrame: number): void {
    pause()

    const startFrame = fromFrame >= lastFrame ? 0 : fromFrame
    const startTime = performance.now()

    onFrame(startFrame)
    setIsPlaying(true)

    function animate(now: number): void {
      const elapsedFrames = Math.floor(
        (now - startTime) * fps / 1000,
      )
      const nextFrame = Math.min(
        startFrame + elapsedFrames,
        lastFrame,
      )

      onFrame(nextFrame)

      if (nextFrame >= lastFrame) {
        animationRef.current = null
        setIsPlaying(false)
        return
      }

      animationRef.current = requestAnimationFrame(animate)
    }

    animationRef.current = requestAnimationFrame(animate)
  }

  return { isPlaying, play, pause }
}