import { useState } from 'react'
import { checkBackendHealth } from './services/api'
import './App.css'
import { ModelSelector } from './components/ModelSelector'
import { EpisodeSelector } from './components/EpisodeSelector'
import { EpisodePlayer } from './components/EpisodePlayer'
import { EvaluationSelector } from './components/EvaluationSelector'
import { EvaluationResults } from './components/EvaluationResults'

function App() {
  const [message, setMessage] = useState('Conexión sin comprobar.')
  const [selectedEpisodeId, setSelectedEpisodeId] = useState('')
  const [checking, setChecking] = useState(false)
  const [selectedModelId, setSelectedModelId] = useState('')
  const [selectedEvaluationId, setSelectedEvaluationId] = useState('')

  async function handleCheckConnection() {
    setChecking(true)
    setMessage('Comprobando conexión...')

    try {
      await checkBackendHealth()
      setMessage('Backend conectado.')
    } catch (error: unknown) {
      setMessage(
        error instanceof Error
          ? error.message
          : 'No se pudo comprobar la conexión.',
      )
    } finally {
      setChecking(false)
    }
  }

  return (
    <main>
      <h1>Rocket RL Lab</h1>
      <p>Entrenamiento y evaluación de un agente PPO.</p>

      <p role="status">{message}</p>

      <button
        type="button"
        onClick={handleCheckConnection}
        disabled={checking}
      >
        {checking ? 'Comprobando...' : 'Comprobar conexión'}
      </button>

      <ModelSelector
        selectedId={selectedModelId}
        onSelect={(modelId) => {
          setSelectedModelId(modelId)
          setSelectedEpisodeId('')
          setSelectedEvaluationId('')
        }}
      />

      {selectedModelId && (
        <EvaluationSelector
          key={`evaluations-${selectedModelId}`}
          modelId={selectedModelId}
          selectedId={selectedEvaluationId}
          onSelect={setSelectedEvaluationId}
        />
      )}

      {selectedModelId && selectedEvaluationId && (
        <EvaluationResults
          key={`results-${selectedEvaluationId}`}
          evaluationId={selectedEvaluationId}
          modelId={selectedModelId}
        />
      )}

      {selectedModelId && (
        <EpisodeSelector
          key={selectedModelId}
          modelId={selectedModelId}
          selectedId={selectedEpisodeId}
          onSelect={setSelectedEpisodeId}
        />
      )}

      {selectedModelId && selectedEpisodeId && (
        <EpisodePlayer
          key={selectedEpisodeId}
          episodeId={selectedEpisodeId}
          modelId={selectedModelId}
        />
      )}

    </main>
  )
}

export default App