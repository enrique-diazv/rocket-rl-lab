import { z } from 'zod'

export const episodeSummarySchema = z.object({
  id: z.string().regex(/^[a-f0-9]{32}$/),
  model_id: z.string().min(1),
  seed: z.number().int().nonnegative(),
  steps: z.number().int().nonnegative(),
  total_reward: z.number(),
  success: z.boolean(),
})

export const episodeSummariesSchema = z.array(episodeSummarySchema)

export type EpisodeSummary = z.infer<typeof episodeSummarySchema>