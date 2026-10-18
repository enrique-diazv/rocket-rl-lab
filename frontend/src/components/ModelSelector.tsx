import { useState } from 'react'
import { getModels, type CheckpointSummary } from '../services/api'

type ModelSelectorProps = {
  selectedId: string
  onSelect: (modelId: string) => void
}

export function ModelSelector({
  selectedId,
  onSelect,
}: ModelSelectorProps) {
  const [models, setModels] = useState<CheckpointSummary[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoadModels() {
    setLoading(true)
    setError('')

    try {
      const availableModels = await getModels()
      setModels(availableModels)

      if (!availableModels.some((model) => model.id === selectedId)) {
        onSelect('')
      }
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudieron consultar los modelos.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Modelo PPO</h2>

      <button
        type="button"
        onClick={handleLoadModels}
        disabled={loading}
      >
        {loading ? 'Cargando...' : 'Cargar modelos'}
      </button>

      {error && <p role="alert">{error}</p>}

      {models?.length === 0 && (
        <p>No hay checkpoints disponibles.</p>
      )}

      <label>
        Modelo:
        <select
          value={selectedId}
          onChange={(event) => onSelect(event.target.value)}
          disabled={loading || models === null || models.length === 0}
        >
          <option value="">Selecciona un modelo</option>
          {models?.map((model) => (
            <option key={model.id} value={model.id}>
              {model.id}
            </option>
          ))}
        </select>
      </label>
    </section>
  )
}