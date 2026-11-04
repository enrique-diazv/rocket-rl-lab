import { useEffect, useState } from 'react'
import type { AdaptationExperiment } from '../schemas/adaptation'
import {
  readAdaptationEvent,
  readAdaptationStreamEnd,
} from '../services/adaptationEvents'
import { applyAdaptationEvent } from '../state/adaptation'

export type AdaptationConnectionStatus =
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'ended'
  | 'failed'

export function useAdaptationEvents(
  initialExperiment: AdaptationExperiment,
) {
  const [experiment, setExperiment] = useState(initialExperiment)
  const [connectionStatus, setConnectionStatus] =
    useState<AdaptationConnectionStatus>('connecting')
  const [error, setError] = useState('')

  useEffect(() => {
    let currentExperiment = initialExperiment
    let stopped = false

    setExperiment(initialExperiment)
    setConnectionStatus('connecting')
    setError('')

    const source = new EventSource(
      `/api/adaptation/experiments/${
        encodeURIComponent(initialExperiment.id)
      }/events?after=${initialExperiment.last_event_id}`,
    )

    function fail(message: string) {
      if (stopped) return

      stopped = true
      source.close()
      setError(message)
      setConnectionStatus('failed')
    }

    source.addEventListener('open', () => {
      if (!stopped) {
        setConnectionStatus('connected')
      }
    })

    source.addEventListener('adaptation', (event) => {
      if (stopped) return

      try {
        const update = readAdaptationEvent(event)
        const nextExperiment = applyAdaptationEvent(
          currentExperiment,
          update,
        )

        if (nextExperiment !== currentExperiment) {
          currentExperiment = nextExperiment
          setExperiment(nextExperiment)
        }
      } catch (error: unknown) {
        fail(
          error instanceof Error
            ? error.message
            : 'No se pudo interpretar el progreso recibido.',
        )
      }
    })

    source.addEventListener('end', (event) => {
      if (stopped) return

      try {
        const lastEventId = readAdaptationStreamEnd(event)

        if (
          lastEventId !== currentExperiment.last_event_id ||
          currentExperiment.jobs.some((job) => job.finished_at === null)
        ) {
          throw new Error(
            'La transmisión terminó sin confirmar todos los trabajos.',
          )
        }

        stopped = true
        source.close()
        setConnectionStatus('ended')
      } catch (error: unknown) {
        fail(
          error instanceof Error
            ? error.message
            : 'No se pudo comprobar el cierre de la transmisión.',
        )
      }
    })

    source.addEventListener('stream_error', () => {
      fail('El backend no pudo transmitir el progreso. Vuelve a consultar.')
    })

    source.addEventListener('error', () => {
      if (stopped) return

      if (source.readyState === EventSource.CLOSED) {
        fail('La transmisión se cerró. Vuelve a consultar el experimento.')
      } else {
        setConnectionStatus('reconnecting')
      }
    })

    return () => {
      stopped = true
      source.close()
    }
  }, [initialExperiment])

  return { experiment, connectionStatus, error }
}