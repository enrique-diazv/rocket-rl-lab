import type {
  FrameSnapshot,
  Point,
  SceneSnapshot,
} from '../schemas/episodes'

function tracePath(
  context: CanvasRenderingContext2D,
  points: Point[],
  closed = false,
): void {
  context.beginPath()

  points.forEach(([x, y], index) => {
    if (index === 0) {
      context.moveTo(x, y)
    } else {
      context.lineTo(x, y)
    }
  })

  if (closed) {
    context.closePath()
  }
}

export function drawEpisodeFrame(
  context: CanvasRenderingContext2D,
  scene: SceneSnapshot,
  frame: FrameSnapshot,
): void {
  const { width, height } = context.canvas

  context.save()
  context.setTransform(1, 0, 0, 1, 0, 0)
  context.fillStyle = '#0b1220'
  context.fillRect(0, 0, width, height)

  context.setTransform(
    width / scene.width,
    0,
    0,
    -height / scene.height,
    0,
    height,
  )
  context.lineWidth = 2 * scene.width / width
  context.strokeStyle = '#94a3b8'

  for (const segment of scene.terrain) {
    tracePath(context, segment)
    context.stroke()
  }

  context.strokeStyle = '#4ade80'
  tracePath(context, scene.helipad)
  context.stroke()

  context.strokeStyle = '#f8fafc'
  context.fillStyle = '#94a3b8'

  for (const leg of frame.legs) {
    tracePath(context, leg, true)
    context.fill()
    context.stroke()
  }

  context.fillStyle = '#fb923c'
  tracePath(context, frame.lander, true)
  context.fill()
  context.stroke()

  context.restore()
}