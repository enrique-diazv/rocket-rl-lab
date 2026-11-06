import type { AdaptationScenarioDraft } from '../presentation/adaptationScenarios'

type AdaptationScenarioFieldsProps = {
  draft: AdaptationScenarioDraft
  disabled: boolean
  onDraftChange: (draft: AdaptationScenarioDraft) => void
}

export function AdaptationScenarioFields({
  draft,
  disabled,
  onDraftChange,
}: AdaptationScenarioFieldsProps) {
  function updateDraftField(
    field: keyof AdaptationScenarioDraft,
    value: string,
  ) {
    onDraftChange({ ...draft, [field]: value })
  }

  return (
    <fieldset disabled={disabled}>
      <legend>Escenario</legend>

      <div>
        <label htmlFor="adaptation-gravity">Gravedad</label>
        <input
          id="adaptation-gravity"
          type="number"
          value={draft.gravity}
          onChange={(event) =>
            updateDraftField('gravity', event.target.value)
          }
          min={-12}
          max={0}
          step="any"
          required
          aria-describedby="adaptation-gravity-help"
        />
        <p id="adaptation-gravity-help">
          Mayor que -12 y menor que 0.
        </p>
      </div>

      <div>
        <label htmlFor="adaptation-platform-width">
          Escala del ancho de plataforma
        </label>
        <input
          id="adaptation-platform-width"
          type="number"
          value={draft.platformWidthScale}
          onChange={(event) =>
            updateDraftField('platformWidthScale', event.target.value)
          }
          min={0.25}
          max={2}
          step="any"
          required
        />
      </div>

      <div>
        <label htmlFor="adaptation-max-steps">
          Máximo de pasos por episodio
        </label>
        <input
          id="adaptation-max-steps"
          type="number"
          value={draft.maxEpisodeSteps}
          onChange={(event) =>
            updateDraftField('maxEpisodeSteps', event.target.value)
          }
          min={1}
          max={2000}
          step={1}
          required
        />
      </div>

      <div>
        <label htmlFor="adaptation-fuel-budget">
          Combustible disponible (unidades relativas)
        </label>
        <input
          id="adaptation-fuel-budget"
          type="number"
          value={draft.fuelBudget}
          onChange={(event) =>
            updateDraftField('fuelBudget', event.target.value)
          }
          min={0}
          step="any"
          aria-describedby="adaptation-fuel-help"
        />
        <p id="adaptation-fuel-help">
          Vacío significa ilimitado. Cero impide la propulsión.
        </p>
      </div>
    </fieldset>
  )
}