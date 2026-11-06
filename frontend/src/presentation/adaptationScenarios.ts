export type AdaptationScenarioDraft = {
  gravity: string
  platformWidthScale: string
  maxEpisodeSteps: string
  fuelBudget: string
}

const neutralScenarioDraft: AdaptationScenarioDraft = {
  gravity: '-10',
  platformWidthScale: '1',
  maxEpisodeSteps: '1000',
  fuelBudget: '',
}

export const adaptationScenarioPresets = {
  neutral: {
    label: 'Neutral',
    draft: neutralScenarioDraft,
  },
  low_gravity: {
    label: 'Gravedad reducida',
    draft: { ...neutralScenarioDraft, gravity: '-5' },
  },
  tight_pad: {
    label: 'Plataforma estrecha',
    draft: { ...neutralScenarioDraft, platformWidthScale: '0.5' },
  },
  low_fuel: {
    label: 'Combustible limitado',
    draft: { ...neutralScenarioDraft, fuelBudget: '30' },
  },
  time_pressure: {
    label: 'Tiempo limitado',
    draft: { ...neutralScenarioDraft, maxEpisodeSteps: '300' },
  },
} satisfies Record<
  string,
  { label: string; draft: AdaptationScenarioDraft }
>

export type AdaptationScenarioPreset =
  keyof typeof adaptationScenarioPresets