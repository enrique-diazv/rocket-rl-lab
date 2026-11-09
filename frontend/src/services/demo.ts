import { z } from 'zod'
import {
  adaptationEventSchema,
  adaptationExperimentSchema,
  type AdaptationExperiment,
} from '../schemas/adaptation'
import {
  applyAdaptationEvent,
  hasCompleteAdaptationHistory,
  recordAdaptationEvaluation,
  type AdaptationEvaluationHistory,
} from '../state/adaptation'

export const staticDemoEnabled = import.meta.env.VITE_STATIC_DEMO === 'true'
export const demoAssetsPath = `${import.meta.env.BASE_URL}demo`

const demoManifestSchema = z.object({
  schema_version: z.literal(1),
  experiment: adaptationExperimentSchema,
  evaluations: z.array(adaptationEventSchema).min(1),
})

export type DemoReport = {
  experiment: AdaptationExperiment
  evaluationHistory: AdaptationEvaluationHistory
}

export async function getDemoReport(): Promise<DemoReport> {
  const response = await fetch(`${demoAssetsPath}/experiment.json`, {
    signal: AbortSignal.timeout(5000),
  })
  if (!response.ok) {
    throw new Error(`No se pudo cargar la demo. HTTP ${response.status}.`)
  }

  const body: unknown = await response.json()
  const parsed = demoManifestSchema.safeParse(body)
  if (!parsed.success) {
    throw new Error('El archivo de la demo tiene un formato inesperado.')
  }

  const { experiment, evaluations } = parsed.data
  let evaluationHistory: AdaptationEvaluationHistory = {}

  for (const event of evaluations) {
    if (event.event_type !== 'evaluation_completed' || event.id > experiment.last_event_id) {
      throw new Error('La demo contiene un evento fuera del historial guardado.')
    }

    applyAdaptationEvent(experiment, event)
    evaluationHistory = recordAdaptationEvaluation(evaluationHistory, event)
  }

  if (
    experiment.jobs.some((job) => job.finished_at === null) ||
    !hasCompleteAdaptationHistory(experiment, evaluationHistory)
  ) {
    throw new Error('El experimento grabado está incompleto.')
  }

  return { experiment, evaluationHistory }
}