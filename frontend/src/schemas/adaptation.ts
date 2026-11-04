import { z } from 'zod'

export const adaptationAgentIdSchema = z.enum([
  'precision',
  'speed',
  'efficiency',
  'stability',
  'balanced',
])

export const adaptationAgentSchema = z.object({
  id: adaptationAgentIdSchema,
  name: z.string().min(1),
  checkpoint_available: z.boolean(),
})

export const adaptationAgentsSchema = z.array(adaptationAgentSchema)

export type AdaptationAgent = z.infer<typeof adaptationAgentSchema>