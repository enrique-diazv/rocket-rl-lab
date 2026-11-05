import { useEffect, useState } from 'react'
import type { AdaptationExperiment } from '../schemas/adaptation'
import {
  readAdaptationEvent,
  readAdaptationStreamEnd,
} from '../services/adaptationEvents'
import {
  applyAdaptationEvent,
  hasCompleteAdaptationHistory,
  recordAdaptationEvaluation,
  type AdaptationEvaluationHistory,
} from '../state/adaptation'

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

  const [evaluationHistory, setEvaluationHistory] =
    useState<AdaptationEvaluationHistory>({})

  useEffect(() => {
    let currentExperiment = initialExperiment
    let currentHistory: AdaptationEvaluationHistory = {}
    let stopped = false

    setExperiment(initialExperiment)
    setConnectionStatus('connecting')
    setError('')
    setEvaluationHistory({})

    const source = new EventSource(
      `/api/adaptation/experiments/${
        encodeURIComponent(initialExperiment.id)
      }/events?after=0`,
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
        const nextHistory = recordAdaptationEvaluation(
          currentHistory,
          update,
        )

        if (nextExperiment !== currentExperiment) {
          currentExperiment = nextExperiment
          setExperiment(nextExperiment)
        }

        if (nextHistory !== currentHistory) {
          currentHistory = nextHistory
          setEvaluationHistory(nextHistory)
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
          currentExperiment.jobs.some((job) => job.finished_at === null) ||
          !hasCompleteAdaptationHistory(currentExperiment, currentHistory)
        ) {
          throw new Error(
            'La transmisión terminó con trabajos o evaluaciones sin confirmar.',
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

  return {
    experiment,
    connectionStatus,
    error,
    evaluationHistory,
    historyReady: hasCompleteAdaptationHistory(
      experiment,
      evaluationHistory,
    ),
  }
}