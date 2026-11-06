import { useState, type SubmitEvent } from 'react'

type AdaptationExperimentViewerProps = {
  loading: boolean
  disabled: boolean
  onLoad: (experimentId: string) => Promise<void>
}

export function AdaptationExperimentViewer({
  loading,
  disabled,
  onLoad,
}: AdaptationExperimentViewerProps) {
  const [experimentId, setExperimentId] = useState('')

  function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    if (disabled) return

    void onLoad(experimentId)
  }

  return (
    <section aria-busy={loading}>
      <h2>Consultar experimento</h2>

      <form onSubmit={handleSubmit}>
        <label htmlFor="adaptation-experiment-id">
          UUID del experimento
        </label>

        <input
          id="adaptation-experiment-id"
          type="text"
          value={experimentId}
          onChange={(event) => setExperimentId(event.target.value)}
          autoCapitalize="none"
          spellCheck={false}
          required
          disabled={disabled}
        />

        <button type="submit" disabled={disabled}>
          {loading ? 'Consultando...' : 'Consultar experimento'}
        </button>
      </form>

      {loading && <p role="status">Consultando experimento...</p>}
    </section>
  )
}