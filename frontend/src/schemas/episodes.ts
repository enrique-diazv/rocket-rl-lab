import { z } from 'zod'

export const episodeSummarySchema = z.object({
  id: z.string().regex(/^[a-f0-9]{32}$/),
  model_id: z.string().min(1),
  seed: z.number().int().nonnegative(),
  steps: z.number().int().nonnegative(),
  total_reward: z.number(),
  success: z.boolean(),
})

const pointSchema = z.tuple([z.number(), z.number()])
const segmentSchema = z.tuple([pointSchema, pointSchema])
const polygonSchema = z.array(pointSchema).min(3)

const sceneSnapshotSchema = z.object({
  width: z.number().positive(),
  height: z.number().positive(),
  fps: z.number().int().positive(),
  terrain: z.array(segmentSchema).min(1),
  helipad: segmentSchema,
})

const frameSnapshotSchema = z.object({
  lander: polygonSchema,
  legs: z.tuple([polygonSchema, polygonSchema]),
})

const episodeTrajectorySchema = episodeSummarySchema
  .omit({ id: true, model_id: true })
  .extend({
    terminated: z.boolean(),
    truncated: z.boolean(),
    scene: sceneSnapshotSchema,
    frames: z.array(frameSnapshotSchema).min(1),
  })
  .refine(
    episode => episode.frames.length === episode.steps + 1,
    {
      message: 'La trayectoria debe incluir el estado inicial y cada paso.',
      path: ['frames'],
    },
  )

export const episodeRecordSchema = z.object({
  schema_version: z.literal(1),
  id: episodeSummarySchema.shape.id,
  model_id: episodeSummarySchema.shape.model_id,
  checkpoint_sha256: z.string().regex(/^[a-f0-9]{64}$/),
  versions: z.record(z.string(), z.string()),
  episode: episodeTrajectorySchema,
})

export type Point = z.infer<typeof pointSchema>
export type SceneSnapshot = z.infer<typeof sceneSnapshotSchema>
export type FrameSnapshot = z.infer<typeof frameSnapshotSchema>
export type EpisodeRecord = z.infer<typeof episodeRecordSchema>

export const episodeSummariesSchema = z.array(episodeSummarySchema)

export type EpisodeSummary = z.infer<typeof episodeSummarySchema>