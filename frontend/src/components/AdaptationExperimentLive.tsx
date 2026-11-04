import type { AdaptationExperiment } from '../schemas/adaptation'
import {
  useAdaptationEvents,
  type AdaptationConnectionStatus,
} from '../hooks/useAdaptationEvents'
import { AdaptationJobCard } from './AdaptationJobCard'

const connectionLabels: Record<AdaptationConnectionStatus, string> = {
  connecting: 'Conectando con el progreso...',
  connected: 'Seguimiento en vivo activo.',
  reconnecting: 'Reconectando. Mostrando el último estado recibido.',
  ended: 'Seguimiento finalizado.',
  failed: 'Seguimiento interrumpido.',
}

type AdaptationExperimentLiveProps = {
  initialExperiment: AdaptationExperiment
}

export function AdaptationExperimentLive({
  initialExperiment,
}: AdaptationExperimentLiveProps) {
  const { experiment, connectionStatus, error } =
    useAdaptationEvents(initialExperiment)

  return (
    <div>
      <p role="status">{connectionLabels[connectionStatus]}</p>
      {error && <p role="alert">{error}</p>}

      <p>
        Experimento: <code>{experiment.id}</code>
      </p>

      <p>
        Presupuesto adicional por agente:{' '}
        {experiment.config.max_additional_timesteps.toLocaleString('es-MX')}{' '}
        pasos.
      </p>

      {experiment.cancel_requested && (
        <p>Se solicitó la cancelación de este experimento.</p>
      )}

      {experiment.jobs.map((job) => (
        <AdaptationJobCard key={job.id} job={job} />
      ))}
    </div>
  )
}