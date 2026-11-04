import {
  adaptationAgentsSchema,
  adaptationExperimentSchema,
  type AdaptationAgent,
  type AdaptationExperiment,
} from '../schemas/adaptation'

export async function getAdaptationAgents(): Promise<AdaptationAgent[]> {
  const response = await fetch('/api/adaptation/agents', {
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  const parsed = adaptationAgentsSchema.safeParse(data)

  if (!parsed.success) {
    throw new Error(
      'El catálogo de agentes tiene un formato inesperado.',
    )
  }

  return parsed.data
}

export async function getAdaptationExperiment(
  experimentId: string,
): Promise<AdaptationExperiment> {
  const parsedId = adaptationExperimentSchema.shape.id.safeParse(
    experimentId.trim().toLowerCase(),
  )

  if (!parsedId.success) {
    throw new Error('Introduce un UUID de experimento válido.')
  }

  const response = await fetch(
    `/api/adaptation/experiments/${encodeURIComponent(parsedId.data)}`,
    { signal: AbortSignal.timeout(5000) },
  )

  if (response.status === 404) {
    throw new Error('Experimento no encontrado.')
  }

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  const parsed = adaptationExperimentSchema.safeParse(data)

  if (!parsed.success) {
    throw new Error(
      'El estado del experimento tiene un formato inesperado.',
    )
  }

  if (parsed.data.id !== parsedId.data) {
    throw new Error(
      'La respuesta no corresponde al experimento solicitado.',
    )
  }

  return parsed.data
}