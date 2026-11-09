import { useEffect, useState } from 'react'
import { AdaptationExperimentReport } from './components/AdaptationExperimentLive'
import { getDemoReport, type DemoReport } from './services/demo'

export default function StaticDemo() {
  const [report, setReport] = useState<DemoReport | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    void getDemoReport()
      .then((result) => {
        if (active) setReport(result)
      })
      .catch((cause: unknown) => {
        if (active) {
          setError(cause instanceof Error ? cause.message : 'No se pudo cargar la demo.')
        }
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <main className="workspace">
      <header className="workspace-heading">
        <div>
          <h1>Desafío de adaptación</h1>
          <p>Demo de solo lectura con métricas y vuelos reales de cinco agentes PPO.</p>
        </div>
      </header>

      {error && <p role="alert">{error}</p>}
      {!report && !error && <p role="status">Cargando el experimento grabado...</p>}

      {report && (
        <>
          <section className="panel" aria-labelledby="demo-scenario-title">
            <h2 id="demo-scenario-title">Escenario del experimento</h2>
            <p>
              Plataforma al {report.experiment.config.scenario.platform_width_scale * 100} %
              {' · '}Gravedad {report.experiment.config.scenario.gravity}
              {' · '}Hasta {report.experiment.config.scenario.max_episode_steps} pasos por episodio
            </p>
          </section>

          <AdaptationExperimentReport
            experiment={report.experiment}
            evaluationHistory={report.evaluationHistory}
            connectionStatus="recorded"
            error=""
            historyReady
          />
        </>
      )}
    </main>
  )
}