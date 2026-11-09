import {
  adaptationAgentsSchema,
  adaptationExperimentRequestSchema,
  adaptationExperimentSchema,
  adaptationReplaysSchema,
  type AdaptationAgent,
  type AdaptationExperiment,
  type AdaptationExperimentRequest,
  type AdaptationReplays,

} from '../schemas/adaptation'
import { demoAssetsPath, staticDemoEnabled } from './demo'

const experimentsPath = '/api/adaptation/experiments'

const mutationErrors: Partial<Record<number, string>> = {
  401: 'Credencial de operador inválida.',
  404: 'Experimento no encontrado.',
  409: 'Ya existe un experimento pendiente o en ejecución.',
  422: 'El backend rechazó los datos de la solicitud.',
  503: 'Las operaciones de escritura no están configuradas.',
}

function parseExperimentId(experimentId: string): string {
  const parsed = adaptationExperimentSchema.shape.id.safeParse(
    experimentId.trim().toLowerCase(),
  )

  if (!parsed.success) {
    throw new Error('Introduce un UUID de experimento válido.')
  }

  return parsed.data
}

async function readExperimentSnapshot(
  response: Response,
  expectedId?: string,
): Promise<AdaptationExperiment> {
  const responseBody: unknown = await response.json()
  const parsed = adaptationExperimentSchema.safeParse(responseBody)

  if (!parsed.success) {
    throw new Error('El estado del experimento tiene un formato inesperado.')
  }

  if (expectedId !== undefined && parsed.data.id !== expectedId) {
    throw new Error('La respuesta no corresponde al experimento solicitado.')
  }

  return parsed.data
}

async function postAdaptationMutation(
  path: string,
  operatorToken: string,
  config?: AdaptationExperimentRequest,
): Promise<Response> {
  const token = operatorToken.trim()

  if (!token) {
    throw new Error('Introduce la credencial de operador.')
  }

  const headers = new Headers({ Authorization: `Bearer ${token}` })
  const request: RequestInit = {
    method: 'POST',
    headers,
    signal: AbortSignal.timeout(10000),
  }

  if (config !== undefined) {
    headers.set('Content-Type', 'application/json')
    request.body = JSON.stringify(config)
  }

  const response = await fetch(path, request)

  if (response.status !== 202) {
    throw new Error(
      mutationErrors[response.status] ??
        `El backend respondió con HTTP ${response.status}.`,
    )
  }

  return response
}

export async function getAdaptationAgents(): Promise<AdaptationAgent[]> {
  const response = await fetch('/api/adaptation/agents', {
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const responseBody: unknown = await response.json()
  const parsed = adaptationAgentsSchema.safeParse(responseBody)

  if (!parsed.success) {
    throw new Error('El catálogo de agentes tiene un formato inesperado.')
  }

  return parsed.data
}

export async function getAdaptationExperiment(
  experimentId: string,
): Promise<AdaptationExperiment> {
  const id = parseExperimentId(experimentId)
  const response = await fetch(`${experimentsPath}/${encodeURIComponent(id)}`, {
    signal: AbortSignal.timeout(5000),
  })

  if (response.status === 404) {
    throw new Error('Experimento no encontrado.')
  }

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  return readExperimentSnapshot(response, id)
}

export async function getAdaptationReplays(
  experimentId: string,
  agent: AdaptationAgent['id'],
): Promise<AdaptationReplays> {
  const id = parseExperimentId(experimentId)
  const path = staticDemoEnabled
    ? `${demoAssetsPath}/${encodeURIComponent(agent)}.json`
    : `${experimentsPath}/${id}/replays/${encodeURIComponent(agent)}`
  const response = await fetch(path, {
    signal: AbortSignal.timeout(10000),
  })

  if (response.status === 404) {
    throw new Error('No hay replays guardados para este agente.')
  }

  if (!response.ok) {
    throw new Error(`El backend respondió con HTTP ${response.status}.`)
  }

  const body: unknown = await response.json()
  const parsed = adaptationReplaysSchema.safeParse(body)
  if (!parsed.success) {
    throw new Error('Los replays tienen un formato inesperado.')
  }

  if (parsed.data.experiment_id !== id.replace(/-/g, '') || parsed.data.agent !== agent) {
    throw new Error('Los replays no corresponden al agente y experimento solicitados.')
  }

  return parsed.data
}

export async function createAdaptationExperiment(
  config: AdaptationExperimentRequest,
  operatorToken: string,
): Promise<AdaptationExperiment> {
  const parsed = adaptationExperimentRequestSchema.safeParse(config)

  if (!parsed.success) {
    throw new Error('La configuración no cumple los límites permitidos.')
  }

  const response = await postAdaptationMutation(
    experimentsPath,
    operatorToken,
    parsed.data,
  )

  return readExperimentSnapshot(response)
}

export async function cancelAdaptationExperiment(
  experimentId: string,
  operatorToken: string,
): Promise<AdaptationExperiment> {
  const id = parseExperimentId(experimentId)
  const response = await postAdaptationMutation(
    `${experimentsPath}/${encodeURIComponent(id)}/cancel`,
    operatorToken,
  )

  return readExperimentSnapshot(response, id)
}