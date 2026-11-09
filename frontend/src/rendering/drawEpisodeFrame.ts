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
  // El estado inicial de la nave puede quedar por encima del escenario.
  const scale = Math.min(width / scene.width, height / (scene.height * 1.08))
  const left = (width - scene.width * scale) / 2

  context.save()
  context.setTransform(1, 0, 0, 1, 0, 0)
  context.fillStyle = '#111214'
  context.fillRect(0, 0, width, height)

  context.setTransform(scale, 0, 0, -scale, left, height)
  context.lineWidth = 2 / scale
  context.strokeStyle = '#8b8e95'

  for (const segment of scene.terrain) {
    tracePath(context, segment)
    context.stroke()
  }

  context.strokeStyle = '#ffad64'
  tracePath(context, scene.helipad)
  context.stroke()

  context.strokeStyle = '#f1f2f3'
  context.fillStyle = '#8b8e95'

  for (const leg of frame.legs) {
    tracePath(context, leg, true)
    context.fill()
    context.stroke()
  }

  context.fillStyle = '#ffad64'
  tracePath(context, frame.lander, true)
  context.fill()
  context.stroke()

  context.restore()
}
