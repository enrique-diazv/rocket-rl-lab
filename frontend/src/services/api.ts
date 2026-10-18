import {episodeSummariesSchema, type EpisodeSummary,} from '../schemas/episodes'

export async function checkBackendHealth(): Promise<void> {
  const response = await fetch('/api/health', {
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()

  if (typeof data !== 'object' || data === null || !('status' in data) ||
      data.status !== 'ok') {
    throw new Error('La respuesta del backend tiene un formato inesperado.')
  }
}

export type CheckpointSummary = {
  id: string
  filename: string
}

function isCheckpointSummary(value: unknown): value is CheckpointSummary {
  return (
      typeof value === 'object' && value !== null && 'id' in value &&
      typeof value.id === 'string' && 'filename' in value &&
      typeof value.filename === 'string')
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

export async function getEpisodes(
  modelId: string,
): Promise<EpisodeSummary[]> {
  const params = new URLSearchParams({ model_id: modelId })
  const response = await fetch(
    `/api/rocket-ai/episodes?${params.toString()}`,
    { signal: AbortSignal.timeout(5000) },
  )

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  const parsed = episodeSummariesSchema.safeParse(data)

  if (!parsed.success) {
    throw new Error('El listado de episodios tiene un formato inesperado.')
  }

  return parsed.data
}