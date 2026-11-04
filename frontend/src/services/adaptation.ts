import {
  adaptationAgentsSchema,
  type AdaptationAgent,
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