import { z } from 'zod'

import { episodeTrajectorySchema } from './episodes'

export const adaptationAgentIdSchema = z.enum([
  'precision',
  'speed',
  'efficiency',
  'stability',
  'balanced',
])

export const adaptationReplaysSchema = z
  .object({
    schema_version: z.literal(1),
    experiment_id: z.string().regex(/^[a-f0-9]{32}$/),
    agent: adaptationAgentIdSchema,
    extra_training_timesteps: z.number().int().nonnegative(),
    before: episodeTrajectorySchema,
    after: episodeTrajectorySchema,
  })
  .refine((pair) => pair.before.seed === pair.after.seed, {
    message: 'Los dos replays deben usar la misma semilla.',
  })

export type AdaptationReplays = z.infer<typeof adaptationReplaysSchema>

export const adaptationAgentSchema = z.object({
  id: adaptationAgentIdSchema,
  name: z.string().min(1),
  checkpoint_available: z.boolean(),
})

export const adaptationAgentsSchema = z.array(adaptationAgentSchema)

export type AdaptationAgent = z.infer<typeof adaptationAgentSchema>

export const adaptationPhaseSchema = z.enum([
  'evaluating',
  'training',
  'already_adapted',
  'adapted',
  'budget_reached',
])

export const adaptationJobStatusSchema = z.union([
  adaptationPhaseSchema,
  z.enum(['queued', 'running', 'failed', 'cancelled']),
])

const adaptationScenarioSchema = z.object({
  gravity: z.number().gt(-12).lt(0),
  max_episode_steps: z.number().int().positive(),
  fuel_budget: z.number().nonnegative().nullable(),
  platform_width_scale: z.number().min(0.25).max(2),
})

const adaptationConfigSchema = z.object({
  scenario: adaptationScenarioSchema,
  max_additional_timesteps: z.number().int().min(0).max(1024000),
  block_timesteps: z.number().int().min(1).max(102400),
})

export const adaptationEvaluationSchema = z.object({
  evaluation_index: z.number().int().positive(),
  extra_training_timesteps: z.number().int().nonnegative(),
  training_episodes: z.number().int().nonnegative(),
  elapsed_wall_seconds: z.number().nonnegative(),
  episode_count: z.number().int().positive(),
  success_rate: z.number().min(0).max(1),
  mean_original_reward: z.number(),
})

export const adaptationProgressSchema = z.object({
  agent: adaptationAgentIdSchema,
  phase: adaptationPhaseSchema,
  extra_training_timesteps: z.number().int().nonnegative(),
  training_episodes: z.number().int().nonnegative(),
  elapsed_wall_seconds: z.number().nonnegative(),
  evaluation_count: z.number().int().nonnegative(),
  last_evaluation: adaptationEvaluationSchema.nullable(),
  time_to_threshold_steps: z.number().int().nonnegative().nullable(),
})

export const adaptationJobSchema = z.object({
  id: z.uuid(),
  agent: adaptationAgentIdSchema,
  status: adaptationJobStatusSchema,
  created_at: z.iso.datetime({ offset: true }),
  started_at: z.iso.datetime({ offset: true }).nullable(),
  finished_at: z.iso.datetime({ offset: true }).nullable(),
  progress: adaptationProgressSchema.nullable(),
  error: z.string().nullable(),
})

export const adaptationExperimentSchema = z.object({
  id: z.uuid(),
  created_at: z.iso.datetime({ offset: true }),
  config: adaptationConfigSchema,
  cancel_requested: z.boolean(),
  jobs: z.array(adaptationJobSchema).length(5),
  last_event_id: z.number().int().nonnegative(),
})

export type AdaptationExperiment = z.infer<
  typeof adaptationExperimentSchema
>

export type AdaptationJob = z.infer<typeof adaptationJobSchema>

export const adaptationEventSchema = z.object({
  id: z.number().int().positive(),
  experiment_id: z.uuid(),
  job_id: z.uuid().nullable(),
  event_type: z.enum([
    'experiment_created',
    'job_started',
    'job_progress',
    'evaluation_completed',
    'job_stopped',
    'cancel_requested',
  ]),
  created_at: z.iso.datetime({ offset: true }),
  agent: adaptationAgentIdSchema.nullable(),
  status: adaptationJobStatusSchema.nullable(),
  finished_at: z.iso.datetime({ offset: true }).nullable(),
  progress: adaptationProgressSchema.nullable(),
  cancel_requested: z.boolean().nullable(),
  error: z.string().nullable(),
})

export const adaptationStreamEndSchema = z.object({
  last_event_id: z.number().int().nonnegative(),
})

export type AdaptationEvent = z.infer<typeof adaptationEventSchema>

export type AdaptationEvaluationPoint = z.infer<
  typeof adaptationEvaluationSchema
>

export const adaptationExperimentRequestSchema =
  adaptationConfigSchema.extend({
    scenario: adaptationScenarioSchema.extend({
      max_episode_steps: z.number().int().min(1).max(2000),
    }),
    max_additional_timesteps: z
      .number()
      .int()
      .min(0)
      .max(102400)
      .multipleOf(2048),
    block_timesteps: z
      .number()
      .int()
      .min(1)
      .max(10240)
      .multipleOf(2048),
  })

export type AdaptationExperimentRequest = z.infer<
  typeof adaptationExperimentRequestSchema
>