import {
  adaptationExperimentRequestSchema,
  type AdaptationExperimentRequest,
} from '../schemas/adaptation'
import type { AdaptationScenarioDraft } from './adaptationScenarios'

function readRequiredNumber(text: string): number {
  const trimmed = text.trim()
  return trimmed === '' ? Number.NaN : Number(trimmed)
}

export function buildAdaptationExperimentRequest(
  draft: AdaptationScenarioDraft,
  maxAdditionalTimesteps: number,
  blockTimesteps: number,
): AdaptationExperimentRequest {
  const parsed = adaptationExperimentRequestSchema.safeParse({
    scenario: {
      gravity: readRequiredNumber(draft.gravity),
      platform_width_scale: readRequiredNumber(draft.platformWidthScale),
      max_episode_steps: readRequiredNumber(draft.maxEpisodeSteps),
      fuel_budget:
        draft.fuelBudget.trim() === ''
          ? null
          : readRequiredNumber(draft.fuelBudget),
    },
    max_additional_timesteps: maxAdditionalTimesteps,
    block_timesteps: blockTimesteps,
  })

  if (!parsed.success) {
    throw new Error(
      'Revisa los valores del escenario y el presupuesto permitido.',
    )
  }

  return parsed.data
}