type OperatorTokenInputProps = {
  token: string
  onTokenChange: (token: string) => void
}

export function OperatorTokenInput({
  token,
  onTokenChange,
}: OperatorTokenInputProps) {
  return (
    <section aria-labelledby="operator-access-title">
      <h2 id="operator-access-title">Acceso de operador</h2>

      <p>
        La credencial autoriza las operaciones del experimento.
        La aplicación la mantiene en memoria mientras esta pantalla
        está abierta.
      </p>

      <label htmlFor="operator-token">Credencial de operador</label>

      <input
        id="operator-token"
        type="password"
        value={token}
        onChange={(event) => onTokenChange(event.target.value)}
        autoComplete="off"
        autoCapitalize="none"
        spellCheck={false}
      />

      <button
        type="button"
        onClick={() => onTokenChange('')}
        disabled={token.length === 0}
      >
        Vaciar campo
      </button>
    </section>
  )
}