import type { AdaptationJob } from '../schemas/adaptation'

export const adaptationStatusLabels: Record<
  AdaptationJob['status'],
  string
> = {
  queued: 'En cola',
  running: 'Iniciando',
  evaluating: 'Evaluando',
  training: 'Entrenando',
  already_adapted: 'Ya cumplía el criterio',
  adapted: 'Criterio alcanzado',
  budget_reached: 'Presupuesto agotado',
  failed: 'Error',
  cancelled: 'Cancelado',
}

export function formatThresholdSteps(job: AdaptationJob): string {
  const steps = job.progress?.time_to_threshold_steps
  if (steps != null) {
    return steps.toLocaleString('es-MX')
  }

  return job.status === 'budget_reached'
    ? 'No alcanzado'
    : 'Sin confirmar'
}