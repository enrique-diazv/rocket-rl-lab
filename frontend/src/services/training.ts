import {
  trainingProgressSchema,
  trainingSummariesSchema,
  type TrainingPoint,
  type TrainingSummary,
} from '../schemas/training'

export async function getTrainingRuns(
  modelId: string,
): Promise<TrainingSummary[]> {
  const params = new URLSearchParams({ model_id: modelId })
  const response = await fetch(
    `/api/rocket-ai/training-runs?${params.toString()}`,
    { signal: AbortSignal.timeout(5000) },
  )

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  const parsed = trainingSummariesSchema.safeParse(data)

  if (!parsed.success) {
    throw new Error(
      'El listado de entrenamientos tiene un formato inesperado.',
    )
  }

  if (parsed.data.some(run => run.model_id !== modelId)) {
    throw new Error('El listado contiene entrenamientos de otro modelo.')
  }

  return parsed.data
}

export async function getTrainingProgress(
  runId: string,
): Promise<TrainingPoint[]> {
  const response = await fetch(
    `/api/rocket-ai/training-runs/${encodeURIComponent(runId)}/progress`,
    { signal: AbortSignal.timeout(5000) },
  )

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  const parsed = trainingProgressSchema.safeParse(data)

  if (!parsed.success) {
    throw new Error(
      'Las métricas de entrenamiento tienen un formato inesperado.',
    )
  }

  return parsed.data
}
