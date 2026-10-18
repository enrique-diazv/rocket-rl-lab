export async function checkBackendHealth(): Promise<void> {
  const response = await fetch('/api/health', {
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()

  if (
    typeof data !== 'object' ||
    data === null ||
    !('status' in data) ||
    data.status !== 'ok'
  ) {
    throw new Error('La respuesta del backend tiene un formato inesperado.')
  }
}

export type CheckpointSummary = {
  id: string
  filename: string
}

function isCheckpointSummary(value: unknown): value is CheckpointSummary {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    typeof value.id === 'string' &&
    'filename' in value &&
    typeof value.filename === 'string'
  )
}

export async function getModels(): Promise<CheckpointSummary[]> {
  const response = await fetch('/api/rocket-ai/models', {
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()

  if (!Array.isArray(data) || !data.every(isCheckpointSummary)) {
    throw new Error('El inventario de modelos tiene un formato inesperado.')
  }

  return data
}