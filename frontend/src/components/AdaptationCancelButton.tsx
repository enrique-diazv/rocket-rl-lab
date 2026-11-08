import { useState } from 'react'
import { cancelAdaptationExperiment } from '../services/adaptation'

type AdaptationCancelButtonProps = {
  experimentId: string
  operatorToken: string
}

type CancellationStatus = 'idle' | 'sending' | 'requested' | 'finished'

export function AdaptationCancelButton({
  experimentId,
  operatorToken,
}: AdaptationCancelButtonProps) {
  const [status, setStatus] = useState<CancellationStatus>('idle')
  const [error, setError] = useState('')

  async function handleCancel(): Promise<void> {
    setStatus('sending')
    setError('')

    try {
      const snapshot = await cancelAdaptationExperiment(
        experimentId,
        operatorToken,
      )
      setStatus(snapshot.cancel_requested ? 'requested' : 'finished')
    } catch (error: unknown) {
      setError(
        error instanceof Error
          ? error.message
          : 'No se pudo solicitar la cancelación.',
      )
      setStatus('idle')
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={handleCancel}
        disabled={status !== 'idle'}
      >
        {status === 'sending' ? 'Solicitando cancelación...' : 'Cancelar experimento'}
      </button>

      {status === 'requested' && (
        <p role="status">Cancelación solicitada. Esperando la detención de los trabajos.</p>
      )}

      {status === 'finished' && (
        <p role="status">El experimento ya terminó.</p>
      )}

      {error && <p role="alert">{error}</p>}
    </div>
  )
}