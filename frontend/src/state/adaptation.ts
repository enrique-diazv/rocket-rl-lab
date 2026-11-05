import type {AdaptationEvaluationPoint, AdaptationEvent, AdaptationExperiment, AdaptationJob,} from '../schemas/adaptation'

function updateJobFromEvent(
    job: AdaptationJob,
    event: AdaptationEvent,
    ): AdaptationJob {
  if (event.agent !== job.agent ||
      (event.progress !== null && event.progress.agent !== job.agent)) {
    throw new Error('El evento no corresponde al agente del trabajo.')
  }

  if (event.status === null) {
    throw new Error('El evento del trabajo no incluye su estado.')
  }

  return {
    ...job, status: event.status, progress: event.progress ?? job.progress,
        finished_at: event.finished_at ?? job.finished_at,
        error: event.error ?? job.error,
  }
}

export function applyAdaptationEvent(
    experiment: AdaptationExperiment,
    event: AdaptationEvent,
    ): AdaptationExperiment {
  if (event.experiment_id !== experiment.id) {
    throw new Error('El evento pertenece a otro experimento.')
  }


  let jobs = experiment.jobs

  if (event.job_id !== null) {
    const matchingJob = jobs.find((job) => job.id === event.job_id)

    if (matchingJob === undefined) {
      throw new Error('El evento pertenece a un trabajo desconocido.')
    }

    const updatedJob = updateJobFromEvent(matchingJob, event)

    jobs = jobs.map(
        (job) => job.id === updatedJob.id ? updatedJob : job,
    )
  }

  if (event.id <= experiment.last_event_id) {
    return experiment
  }

  return {
    ...experiment, jobs,
        cancel_requested: event.cancel_requested ?? experiment.cancel_requested,
        last_event_id: event.id,
  }
}

export type AdaptationEvaluationHistory =
    Partial<Record<string, AdaptationEvaluationPoint[]>>

    export function recordAdaptationEvaluation(
        history: AdaptationEvaluationHistory,
        event: AdaptationEvent,
        ):
        AdaptationEvaluationHistory {
          if (event.event_type !== 'evaluation_completed') {
            return history
          }

          const progress = event.progress

          if (event.job_id === null || progress === null ||
              progress.last_evaluation === null ||
              event.agent !== progress.agent) {
            throw new Error('El evento no contiene una evaluación válida.')
          }

          const evaluation = progress.last_evaluation

          if (evaluation.evaluation_index !== progress.evaluation_count) {
            throw new Error(
                'El número de evaluación no coincide con el progreso.')
          }

          const previousPoints = history[event.job_id] ??
              []

              if (previousPoints.some(
                      (point) => point.evaluation_index ===
                          evaluation.evaluation_index,
                      )) {
            return history
          }

          const nextPoints = [...previousPoints, evaluation].sort(
              (first, second) =>
                  first.evaluation_index - second.evaluation_index,
          )

          return {
            ...history, [event.job_id]: nextPoints,
          }
        }

export function hasCompleteAdaptationHistory(
    experiment: AdaptationExperiment,
    history: AdaptationEvaluationHistory,
    ): boolean {
  return experiment.jobs.every(
      (job) => (history[job.id]?.length ?? 0) ===
          (job.progress?.evaluation_count ?? 0),
  )
}