import { useState } from 'react'
import { checkBackendHealth } from './services/api'
import './App.css'
import { ModelSelector } from './components/ModelSelector'

function App() {
  const [message, setMessage] = useState('Conexión sin comprobar.')
  const [checking, setChecking] = useState(false)
  const [selectedModelId, setSelectedModelId] = useState('')

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
        onSelect={setSelectedModelId}
      />

    </main>
  )
}

export default App