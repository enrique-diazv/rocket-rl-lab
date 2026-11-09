import { useState } from 'react'
import { checkBackendHealth } from './services/api'
import { ModelSelector } from './components/ModelSelector'
import { EpisodeSelector } from './components/EpisodeSelector'
import { EpisodePlayer } from './components/EpisodePlayer'
import { EvaluationSelector } from './components/EvaluationSelector'
import { EvaluationResults } from './components/EvaluationResults'
import { TrainingSelector } from './components/TrainingSelector'
import { TrainingProgress } from './components/TrainingProgress'

function NeutralLab() {
  const [message, setMessage] = useState('Conexión sin comprobar.')
  const [selectedEpisodeId, setSelectedEpisodeId] = useState('')
  const [checking, setChecking] = useState(false)
  const [selectedModelId, setSelectedModelId] = useState('')
  const [selectedEvaluationId, setSelectedEvaluationId] = useState('')
  const [selectedTrainingId, setSelectedTrainingId] = useState('')

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
    <main className="workspace">
      <header className="workspace-heading">
        <div>
          <h1>Laboratorio neutral</h1>
          <p>Reproduce aterrizajes y consulta el entrenamiento de los modelos PPO.</p>
        </div>
        <div className="connection-check">
          <p role="status">{message}</p>
          <button type="button" onClick={handleCheckConnection} disabled={checking}>
            {checking ? 'Comprobando...' : 'Comprobar conexión'}
          </button>
        </div>
      </header>

      <div className="flight-desk">
        <aside className="flight-controls" aria-label="Selección de modelo y vuelo">
          <ModelSelector
            selectedId={selectedModelId}
            onSelect={(modelId) => {
              setSelectedModelId(modelId)
              setSelectedEpisodeId('')
              setSelectedEvaluationId('')
              setSelectedTrainingId('')
            }}
          />
          {selectedModelId ? (
            <EpisodeSelector
              key={selectedModelId}
              modelId={selectedModelId}
              selectedId={selectedEpisodeId}
              onSelect={setSelectedEpisodeId}
            />
          ) : (
            <section>
              <h2>Episodios grabados</h2>
              <p>Selecciona un modelo para consultar sus vuelos.</p>
            </section>
          )}
        </aside>

        {selectedModelId && selectedEpisodeId ? (
          <EpisodePlayer
            key={selectedEpisodeId}
            episodeId={selectedEpisodeId}
            modelId={selectedModelId}
          />
        ) : (
          <section className="panel flight-panel" aria-labelledby="flight-preview-title">
            <h2 id="flight-preview-title">Vista de vuelo</h2>
            <figure className="flight-placeholder">
              <img
                src={`${import.meta.env.BASE_URL}flight-schematic.svg`}
                alt="Esquema de la cabina, los apoyos y la plataforma de aterrizaje"
                width={620}
                height={270}
              />
              <figcaption>
                <strong>Sin trayectoria cargada</strong>
                <span>Selecciona un episodio grabado para ver el vuelo.</span>
              </figcaption>
            </figure>
          </section>
        )}
      </div>

      <div className="neutral-records">
        <div className="panel record-panel">
          {selectedModelId ? (
            <TrainingSelector
              key={`training-${selectedModelId}`}
              modelId={selectedModelId}
              selectedId={selectedTrainingId}
              onSelect={setSelectedTrainingId}
            />
          ) : (
            <section>
              <h2>Entrenamientos</h2>
              <p>Consulta la recompensa y la duración de los episodios durante el aprendizaje.</p>
            </section>
          )}
          {selectedModelId && selectedTrainingId && (
            <TrainingProgress key={selectedTrainingId} runId={selectedTrainingId} />
          )}
        </div>

        <div className="panel record-panel">
          {selectedModelId ? (
            <EvaluationSelector
              key={`evaluations-${selectedModelId}`}
              modelId={selectedModelId}
              selectedId={selectedEvaluationId}
              onSelect={setSelectedEvaluationId}
            />
          ) : (
            <section>
              <h2>Evaluaciones</h2>
              <p>Consulta los aterrizajes exitosos y la recompensa original por episodio.</p>
            </section>
          )}
          {selectedModelId && selectedEvaluationId && (
            <EvaluationResults
              key={selectedEvaluationId}
              evaluationId={selectedEvaluationId}
              modelId={selectedModelId}
            />
          )}
        </div>
      </div>
    </main>
  )
}

export default NeutralLab
