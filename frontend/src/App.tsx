import { useState } from 'react'
import { checkBackendHealth } from './services/api'
import './App.css'

function App() {
  const [message, setMessage] = useState('Conexión sin comprobar.')
  const [checking, setChecking] = useState(false)

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
    </main>
  )
}

export default App