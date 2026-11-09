import type { AdaptationExperiment } from '../schemas/adaptation'
import {
  useAdaptationEvents,
  type AdaptationConnectionStatus,
} from '../hooks/useAdaptationEvents'
import { AdaptationJobCard } from './AdaptationJobCard'
import { lazy, Suspense } from 'react'
import { AdaptationComparisonTable } from './AdaptationComparisonTable'
import { AdaptationCancelButton } from './AdaptationCancelButton'
import { AdaptationReplayComparison } from './AdaptationReplayComparison'
import { AdaptationCriterionChart } from './AdaptationCriterionChart'

const AdaptationChart = lazy(() =>
  import('./AdaptationChart').then((chartModule) => ({
    default: chartModule.AdaptationChart,
  })),
)

const connectionLabels: Record<AdaptationConnectionStatus, string> = {
  connecting: 'Conectando con el progreso...',
  connected: 'Seguimiento en vivo activo.',
  reconnecting: 'Reconectando. Mostrando el último estado recibido.',
  ended: 'Seguimiento finalizado.',
  failed: 'Seguimiento interrumpido.',
}

type AdaptationExperimentLiveProps = {
  initialExperiment: AdaptationExperiment
  operatorToken: string
}

export function AdaptationExperimentLive({
  initialExperiment,
  operatorToken,
}: AdaptationExperimentLiveProps) {
  const {
    experiment,
    connectionStatus,
    error,
    evaluationHistory,
    historyReady,
  } = useAdaptationEvents(initialExperiment)

  const hasEvaluations = experiment.jobs.some(
    (job) => (evaluationHistory[job.id]?.length ?? 0) > 0,
  )

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

      {!experiment.cancel_requested &&
        experiment.jobs.some((job) => job.finished_at === null) && (
          <AdaptationCancelButton
            experimentId={experiment.id}
            operatorToken={operatorToken}
          />
        )}

      {experiment.cancel_requested && (
        <p>Se solicitó la cancelación de este experimento.</p>
      )}

      {experiment.jobs.map((job) => (
        <AdaptationJobCard key={job.id} job={job} />
      ))}

      <section aria-labelledby="adaptation-comparison-title">
        <h2 id="adaptation-comparison-title">
          Comparación de resultados
        </h2>

        <p>
          El tiempo registrado corresponde a cada trabajo y depende
          del equipo.
        </p>

        <AdaptationComparisonTable jobs={experiment.jobs} />

        <AdaptationCriterionChart jobs={experiment.jobs} />

      </section>

      <section aria-labelledby="adaptation-charts-title">
        <h2 id="adaptation-charts-title">Curvas de evaluación</h2>

        <p>
          El criterio exige al menos 90% de éxito en dos evaluaciones
          consecutivas.
        </p>

        {!historyReady && connectionStatus !== 'failed' && (
          <p role="status">Recuperando historial de evaluaciones...</p>
        )}

        {!historyReady && connectionStatus === 'failed' && (
          <p>No se pudo recuperar el historial completo.</p>
        )}

        {historyReady && !hasEvaluations && (
          <p>Todavía no hay evaluaciones para graficar.</p>
        )}

        {historyReady && hasEvaluations && (
          <Suspense fallback={<p role="status">Cargando gráficas...</p>}>
            <AdaptationChart
              jobs={experiment.jobs}
              history={evaluationHistory}
              metric="success_rate"
            />

            <AdaptationChart
              jobs={experiment.jobs}
              history={evaluationHistory}
              metric="mean_original_reward"
            />
          </Suspense>
        )}
      </section>

      <AdaptationReplayComparison
        experimentId={experiment.id}
        jobs={experiment.jobs}
      />

    </div>
  )
}