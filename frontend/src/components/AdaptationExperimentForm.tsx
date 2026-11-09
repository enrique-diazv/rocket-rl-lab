import { useState, type ReactNode, type SubmitEvent } from 'react'
import type { AdaptationExperimentRequest } from '../schemas/adaptation'
import {
  adaptationScenarioPresets,
  type AdaptationScenarioDraft,
  type AdaptationScenarioPreset,
} from '../presentation/adaptationScenarios'
import { buildAdaptationExperimentRequest } from '../presentation/adaptationRequest'
import { AdaptationScenarioFields } from './AdaptationScenarioFields'
import { AdaptationTrainingFields } from './AdaptationTrainingFields'

type AdaptationExperimentFormProps = {
  disabled: boolean
  creating: boolean
  onCreate: (config: AdaptationExperimentRequest) => Promise<void>
  operatorAccess: ReactNode
}

export function AdaptationExperimentForm({
  disabled,
  creating,
  onCreate,
  operatorAccess,
}: AdaptationExperimentFormProps) {
  const [draft, setDraft] = useState<AdaptationScenarioDraft>({
    ...adaptationScenarioPresets.neutral.draft,
  })
  const [preset, setPreset] =
    useState<AdaptationScenarioPreset | 'custom'>('neutral')
  const [maxAdditionalTimesteps, setMaxAdditionalTimesteps] = useState(2048)
  const [blockTimesteps, setBlockTimesteps] = useState(2048)
  const [validationError, setValidationError] = useState('')

  function handlePresetChange(value: string) {
    if (!Object.hasOwn(adaptationScenarioPresets, value)) return

    const presetId = value as AdaptationScenarioPreset

    setPreset(presetId)
    setDraft({ ...adaptationScenarioPresets[presetId].draft })
    setValidationError('')
  }

  function handleDraftChange(nextDraft: AdaptationScenarioDraft) {
    setDraft(nextDraft)
    setPreset('custom')
    setValidationError('')
  }

  function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    if (disabled) return

    setValidationError('')

    try {
      const config = buildAdaptationExperimentRequest(
        draft,
        maxAdditionalTimesteps,
        blockTimesteps,
      )
      void onCreate(config)
    } catch (error: unknown) {
      setValidationError(
        error instanceof Error
          ? error.message
          : 'No se pudo validar la configuración.',
      )
    }
  }

  return (
    <section className="panel command-form" aria-busy={creating}>
      <h2>Nuevo experimento</h2>
      <p>Se creará un trabajo para cada uno de los cinco agentes.</p>

      <form id="adaptation-create-form" onSubmit={handleSubmit}>
        <div className="scenario-preset">
          <div>
            <label htmlFor="adaptation-scenario-preset">
              Configuración del escenario
            </label>

            <select
              id="adaptation-scenario-preset"
              value={preset}
              onChange={(event) => handlePresetChange(event.target.value)}
              disabled={disabled}
            >
              {Object.entries(adaptationScenarioPresets).map(
                ([presetId, definition]) => (
                  <option key={presetId} value={presetId}>
                    {definition.label}
                  </option>
                ),
              )}
              <option value="custom" disabled>
                Personalizado
              </option>
            </select>
          </div>

          <button
            type="button"
            onClick={() => handlePresetChange('neutral')}
            disabled={disabled}
          >
            Restablecer escenario
          </button>
        </div>

        <AdaptationScenarioFields
          draft={draft}
          disabled={disabled}
          onDraftChange={handleDraftChange}
        />

        <AdaptationTrainingFields
          maxAdditionalTimesteps={maxAdditionalTimesteps}
          blockTimesteps={blockTimesteps}
          disabled={disabled}
          onBudgetChange={setMaxAdditionalTimesteps}
          onBlockChange={setBlockTimesteps}
        />

        {validationError && <p role="alert">{validationError}</p>}
      </form>

      {operatorAccess}

      <button className="primary-button" type="submit" form="adaptation-create-form" disabled={disabled}>
        {creating ? 'Creando...' : 'Crear experimento'}
      </button>
    </section>
  )
}
