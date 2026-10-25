import {z} from 'zod'

import {episodeSummarySchema} from './episodes'

const evaluatedEpisodeSchema =
    episodeSummarySchema.omit({id: true, model_id: true}).extend({
      terminated: z.boolean(),
      truncated: z.boolean(),
      final_horizontal_error: z.number().nonnegative().nullable().optional(),
      engine_usage_cost: z.number().nonnegative().nullable().optional(),
      pre_contact_speed: z.number().nonnegative().nullable().optional(),
      pre_contact_abs_angle: z.number().nonnegative().nullable().optional(),
      pre_contact_angular_speed: z.number().nonnegative().nullable().optional(),
    })

export const evaluationSummarySchema = z.object({
  id: episodeSummarySchema.shape.id,
  model_id: episodeSummarySchema.shape.model_id,
  created_at: z.iso.datetime({offset: true}),
  training_timesteps: z.number().int().nonnegative(),
  episode_count: z.number().int().positive(),
})

export const evaluationSummariesSchema = z.array(
    evaluationSummarySchema,
)

export const evaluationRecordSchema =
    evaluationSummarySchema.omit({episode_count: true}).extend({
      schema_version: z.literal(1),
      checkpoint_sha256: z.string().regex(/^[a-f0-9]{64}$/),
      environment_id: z.literal('LunarLander-v3'),
      scenario: z.object({
                   gravity: z.number().gt(-12).lt(0),
                   max_episode_steps: z.number().int().positive(),
                   fuel_budget: z.number().nonnegative().nullable().optional(),
                   platform_width_scale: z.number().min(0.25).max(2).optional(),
                 }).optional(),
      reward_mode: z.literal('original'),
      deterministic: z.literal(true),
      versions: z.record(z.string(), z.string()),
      episodes: z.array(evaluatedEpisodeSchema).min(1),
    })

export type EvaluationSummary = z.infer<typeof evaluationSummarySchema>

                                export type EvaluationRecord =
    z.infer<typeof evaluationRecordSchema>