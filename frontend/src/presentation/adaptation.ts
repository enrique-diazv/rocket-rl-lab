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