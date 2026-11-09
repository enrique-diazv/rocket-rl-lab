import { useState } from 'react'
import NeutralLab from './NeutralLab'
import AdaptationChallenge from './AdaptationChallenge'
import './App.css'

function App() {
  const [mode, setMode] = useState<'neutral' | 'adaptation'>('neutral')

  return (
    <>
      <header className="app-header">
        <div className="app-header__inner">
          <div className="app-brand">
            <img src={`${import.meta.env.BASE_URL}favicon.svg`} width={30} height={30} alt="" />
            <span>Rocket RL Lab</span>
          </div>

          <nav className="app-nav" aria-label="Modos del laboratorio">
            <button
              type="button"
              aria-pressed={mode === 'neutral'}
              onClick={() => setMode('neutral')}
            >
              <span>Laboratorio neutral</span>
            </button>
            <button
              type="button"
              aria-pressed={mode === 'adaptation'}
              onClick={() => setMode('adaptation')}
            >
              <span>Desafío de adaptación</span>
            </button>
          </nav>

          <span className="app-scope">LunarLander-v3</span>
        </div>
      </header>

      {mode === 'neutral' ? (
        <NeutralLab />
      ) : (
        <AdaptationChallenge />
      )}
    </>
  )
}

export default App
