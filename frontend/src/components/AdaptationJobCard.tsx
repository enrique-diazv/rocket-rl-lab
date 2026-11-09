import type { AdaptationJob } from '../schemas/adaptation'
import { adaptationStatusLabels } from '../presentation/adaptation'

type AdaptationJobCardProps = {
  job: AdaptationJob
}

export function AdaptationJobCard({ job }: AdaptationJobCardProps) {
  const progress = job.progress
  const evaluation = progress?.last_evaluation

  return (
    <article className="agent-job">
      <h3>{job.agent}</h3>
      <p className="agent-job__status" data-status={job.status}>
        {adaptationStatusLabels[job.status]}
      </p>

      {progress ? (
        <dl>
          <dt>Pasos adicionales de entrenamiento</dt>
          <dd>
            {progress.extra_training_timesteps.toLocaleString('es-MX')}
          </dd>

          <dt>Episodios de entrenamiento</dt>
          <dd>{progress.training_episodes.toLocaleString('es-MX')}</dd>

          <dt>Tiempo registrado</dt>
          <dd>{progress.elapsed_wall_seconds.toFixed(1)} segundos</dd>

          <dt>Evaluaciones completadas</dt>
          <dd>{progress.evaluation_count}</dd>
        </dl>
      ) : (
        <p>Todavía no hay progreso registrado.</p>
      )}

      {evaluation ? (
        <div className="agent-job__evaluation">
          <h4>Última evaluación</h4>
          <p>Episodios evaluados: {evaluation.episode_count}</p>
          <p>
            Tasa de éxito: {(evaluation.success_rate * 100).toFixed(1)}%
          </p>
          <p>
            Recompensa original media:{' '}
            {evaluation.mean_original_reward.toFixed(2)}
          </p>
        </div>
      ) : (
        <p>Todavía no hay una evaluación registrada.</p>
      )}

      {job.error && <p role="alert">{job.error}</p>}
    </article>
  )
}
