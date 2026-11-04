import {
  adaptationEventSchema,
  adaptationStreamEndSchema,
  type AdaptationEvent,
} from '../schemas/adaptation'

function requireTextMessage(event: Event): MessageEvent<string> {
  if (
    !(event instanceof MessageEvent) ||
    typeof event.data !== 'string'
  ) {
    throw new Error('La transmisión recibió un mensaje inesperado.')
  }

  return event
}

export function readAdaptationEvent(event: Event): AdaptationEvent {
  const message = requireTextMessage(event)
  const payload: unknown = JSON.parse(message.data)
  const parsed = adaptationEventSchema.safeParse(payload)

  if (!parsed.success) {
    throw new Error('El evento de adaptación tiene un formato inesperado.')
  }

  if (message.lastEventId !== String(parsed.data.id)) {
    throw new Error('El identificador del mensaje no coincide con el evento.')
  }

  return parsed.data
}

export function readAdaptationStreamEnd(event: Event): number {
  const message = requireTextMessage(event)
  const payload: unknown = JSON.parse(message.data)
  const parsed = adaptationStreamEndSchema.safeParse(payload)

  if (!parsed.success) {
    throw new Error('El cierre de la transmisión tiene un formato inesperado.')
  }

  return parsed.data.last_event_id
}