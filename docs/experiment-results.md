# Resultados de experimentos

## Ensayo 001: entrenamiento inicial de PPO Neutral

### Objetivo

Comprobar el entrenamiento, guardado, carga y evaluación de un modelo PPO.

### Configuración

- Entorno: LunarLander-v3, parámetros estándar y recompensa original.
- Gymnasium: 1.4.0.
- Stable-Baselines3: 2.9.0.
- PyTorch: 2.14.1+cpu.
- Dispositivo: CPU.
- Política: MlpPolicy, arquitectura configurada como [64, 64].
- Seed de entrenamiento: 42.
- Pasos de entrenamiento: 10 240.
- Pasos por bloque: 2048.
- Tamaño de minibatch: 64.
- Checkpoint: backend/checkpoints/neutral_initial.zip.

### Evaluación

- Diez episodios con seeds de 1000 a 1009.
- Acciones deterministas.
- Recompensa original media: -385.04.
- Desviación estándar muestral: 53.50.
- Episodios truncados: 0 de 10.

### Interpretación

El ciclo de entrenamiento y evaluación funciona.
El desempeño sigue siendo bajo y no demuestra aterrizajes consistentes.

Esta ejecución es una comprobación inicial con entrenamiento breve.
Todavía no se ha implementado una medición explícita de aterrizajes exitosos.

### Reproducción del checkpoint

El módulo app.rl.play cargó el checkpoint y reprodujo tres episodios
con acciones deterministas. Las recompensas coincidieron con la evaluación:

| Seed | Recompensa |
| --- | ---: |
| 1000 | -367.69 |
| 1001 | -281.72 |
| 1002 | -393.75 |