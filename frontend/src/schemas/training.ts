import { z } from 'zod'
import { episodeSummarySchema } from './episodes'

export const trainingSummarySchema = z.object({
  id: episodeSummarySchema.shape.id,
  model_id: episodeSummarySchema.shape.model_id,
  created_at: z.iso.datetime({ offset: true }),
  requested_timesteps: z.number().int().positive(),
  reward_mode: z.string().min(1),
})

export const trainingSummariesSchema = z.array(trainingSummarySchema)

export const trainingPointSchema = z.object({
  timesteps: z.number().int().positive(),
  mean_episode_reward: z.number(),
  mean_episode_length: z.number().positive(),
})

export const trainingProgressSchema = z.array(trainingPointSchema).refine(
  points => {
    let previousTimesteps = 0

    for (const point of points) {
      if (point.timesteps <= previousTimesteps) {
        return false
      }

      previousTimesteps = point.timesteps
    }

    return true
  },
  {
    message: 'Los pasos del entrenamiento deben avanzar sin repetirse.',
  },
)

export type TrainingSummary = z.infer<typeof trainingSummarySchema>
export type TrainingPoint = z.infer<typeof trainingPointSchema>