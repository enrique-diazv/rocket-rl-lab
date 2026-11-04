import type {
  AdaptationEvent,
  AdaptationExperiment,
  AdaptationJob,
} from '../schemas/adaptation'

function updateJobFromEvent(
  job: AdaptationJob,
  event: AdaptationEvent,
): AdaptationJob {
  if (
    event.agent !== job.agent ||
    (event.progress !== null && event.progress.agent !== job.agent)
  ) {
    throw new Error('El evento no corresponde al agente del trabajo.')
  }

  if (event.status === null) {
    throw new Error('El evento del trabajo no incluye su estado.')
  }

  return {
    ...job,
    status: event.status,
    progress: event.progress ?? job.progress,
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

  if (event.id <= experiment.last_event_id) {
    return experiment
  }

  let jobs = experiment.jobs

  if (event.job_id !== null) {
    const matchingJob = jobs.find((job) => job.id === event.job_id)

    if (matchingJob === undefined) {
      throw new Error('El evento pertenece a un trabajo desconocido.')
    }

    const updatedJob = updateJobFromEvent(matchingJob, event)

    jobs = jobs.map((job) =>
      job.id === updatedJob.id ? updatedJob : job,
    )
  }

  return {
    ...experiment,
    jobs,
    cancel_requested:
      event.cancel_requested ?? experiment.cancel_requested,
    last_event_id: event.id,
  }
}