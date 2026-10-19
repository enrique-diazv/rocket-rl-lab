import {
  evaluationRecordSchema,
  evaluationSummariesSchema,
  type EvaluationRecord,
  type EvaluationSummary,
} from '../schemas/evaluations'

export async function getEvaluations(
  modelId: string,
): Promise<EvaluationSummary[]> {
  const params = new URLSearchParams({ model_id: modelId })
  const response = await fetch(
    `/api/rocket-ai/evaluations?${params.toString()}`,
    { signal: AbortSignal.timeout(5000) },
  )

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  const parsed = evaluationSummariesSchema.safeParse(data)

  if (!parsed.success) {
    throw new Error(
      'El listado de evaluaciones tiene un formato inesperado.',
    )
  }

  if (parsed.data.some(evaluation => evaluation.model_id !== modelId)) {
    throw new Error('El listado contiene evaluaciones de otro modelo.')
  }

  return parsed.data
}

export async function getEvaluation(
  evaluationId: string,
): Promise<EvaluationRecord> {
  const response = await fetch(
    `/api/rocket-ai/evaluations/${encodeURIComponent(evaluationId)}`,
    { signal: AbortSignal.timeout(5000) },
  )

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  const parsed = evaluationRecordSchema.safeParse(data)

  if (!parsed.success) {
    throw new Error(
      'El detalle de la evaluación tiene un formato inesperado.',
    )
  }

  if (parsed.data.id !== evaluationId) {
    throw new Error(
      'La evaluación recibida no corresponde a la solicitada.',
    )
  }

  return parsed.data
}