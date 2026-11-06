import {type AdaptationAgent, adaptationAgentsSchema, type AdaptationExperiment, type AdaptationExperimentRequest, adaptationExperimentRequestSchema, adaptationExperimentSchema,} from '../schemas/adaptation'

const adaptationMutationErrors: Partial<Record<number, string>> = {
  401: 'Credencial de operador inválida.',
  409: 'Ya existe un experimento pendiente o en ejecución.',
  422: 'El backend rechazó los datos de la solicitud.',
  503: 'Las operaciones de escritura no están configuradas.',
}
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
      {signal: AbortSignal.timeout(5000)},
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

export async function createAdaptationExperiment(
  config: AdaptationExperimentRequest,
  operatorToken: string,
): Promise<AdaptationExperiment> {
  const parsedRequest = adaptationExperimentRequestSchema.safeParse(config)

  if (!parsedRequest.success) {
    throw new Error('La configuración no cumple los límites permitidos.')
  }

  const token = operatorToken.trim()

  if (!token) {
    throw new Error('Introduce la credencial de operador.')
  }

  const response = await fetch('/api/adaptation/experiments', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(parsedRequest.data),
    signal: AbortSignal.timeout(10000),
  })

  if (response.status !== 202) {
    throw new Error(
      adaptationMutationErrors[response.status] ??
        `El backend respondió con HTTP ${response.status}.`,
    )
  }

  const responseBody: unknown = await response.json()
  const parsedExperiment =
    adaptationExperimentSchema.safeParse(responseBody)

  if (!parsedExperiment.success) {
    throw new Error(
      'La respuesta de creación tiene un formato inesperado.',
    )
  }

  return parsedExperiment.data
}