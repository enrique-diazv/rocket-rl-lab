import { useState } from 'react'
import NeutralLab from './NeutralLab'
import AdaptationChallenge from './AdaptationChallenge'

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
        <AdaptationChallenge />
      )}
    </>
  )
}

export default App