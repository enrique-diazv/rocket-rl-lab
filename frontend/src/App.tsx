import { useState } from 'react'
import NeutralLab from './NeutralLab'
import { AdaptationAgents } from './components/AdaptationAgents'

function App() {
  const [mode, setMode] = useState<'neutral' | 'adaptation'>('neutral')

  return (
    <>
      <nav aria-label="Modos del laboratorio">
        <button
          type="button"
          aria-pressed={mode === 'neutral'}
          onClick={() => setMode('neutral')}
        >
          Laboratorio neutral
        </button>

        <button
          type="button"
          aria-pressed={mode === 'adaptation'}
          onClick={() => setMode('adaptation')}
        >
          Desafío de adaptación
        </button>
      </nav>

      {mode === 'neutral' ? (
        <NeutralLab />
      ) : (
        <main>
          <h1>Desafío de adaptación</h1>
          <p>Consulta los cinco agentes entrenados.</p>
          <AdaptationAgents />
        </main>
      )}
    </>
  )
}

export default App