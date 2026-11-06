const budgetOptions = [0, 2048, 4096, 10240, 20480, 51200, 102400]
const blockOptions = [2048, 4096, 6144, 8192, 10240]

type AdaptationTrainingFieldsProps = {
  maxAdditionalTimesteps: number
  blockTimesteps: number
  disabled: boolean
  onBudgetChange: (timesteps: number) => void
  onBlockChange: (timesteps: number) => void
}

export function AdaptationTrainingFields({
  maxAdditionalTimesteps,
  blockTimesteps,
  disabled,
  onBudgetChange,
  onBlockChange,
}: AdaptationTrainingFieldsProps) {
  return (
    <fieldset disabled={disabled}>
      <legend>Presupuesto de adaptación</legend>

      <div>
        <label htmlFor="adaptation-training-budget">
          Máximo de pasos adicionales por agente
        </label>

        <select
          id="adaptation-training-budget"
          value={maxAdditionalTimesteps}
          onChange={(event) =>
            onBudgetChange(Number(event.target.value))
          }
        >
          {budgetOptions.map((timesteps) => (
            <option key={timesteps} value={timesteps}>
              {timesteps === 0
                ? 'Solo evaluación (0 pasos adicionales)'
                : `${timesteps.toLocaleString('es-MX')} pasos`}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="adaptation-block-size">
          Tamaño del bloque de entrenamiento
        </label>

        <select
          id="adaptation-block-size"
          value={blockTimesteps}
          onChange={(event) =>
            onBlockChange(Number(event.target.value))
          }
          disabled={maxAdditionalTimesteps === 0}
        >
          {blockOptions.map((timesteps) => (
            <option key={timesteps} value={timesteps}>
              {timesteps.toLocaleString('es-MX')} pasos
            </option>
          ))}
        </select>
      </div>

      <p>
        El presupuesto se aplica a cada uno de los cinco agentes.
        Los bloques pequeños permiten evaluar con más frecuencia.
        El último bloque se ajusta al presupuesto restante.
      </p>
    </fieldset>
  )
}