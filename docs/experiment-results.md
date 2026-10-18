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

## Ensayo 002: PPO Neutral con mayor presupuesto

### Configuración

Se conservaron el entorno, las versiones, la arquitectura, la seed 42
y los parámetros PPO del ensayo 001.

- Modelo nuevo entrenado desde cero.
- Pasos de entrenamiento: 1 024 000.
- Checkpoint: backend/checkpoints/neutral_baseline.zip.
- Recompensa media reciente de entrenamiento en el último log: 191.
- Tiempo reportado en el último log: 1252 segundos.

### Evaluación

Diez episodios con las mismas seeds y acciones deterministas del ensayo 001.

| Seed | Recompensa | Pasos |
| --- | ---: | ---: |
| 1000 | 263.58 | 331 |
| 1001 | 238.34 | 256 |
| 1002 | 238.39 | 335 |
| 1003 | 264.07 | 322 |
| 1004 | -9.46 | 327 |
| 1005 | 220.18 | 266 |
| 1006 | -11.10 | 305 |
| 1007 | 229.04 | 254 |
| 1008 | 249.50 | 297 |
| 1009 | 209.43 | 271 |

- Recompensa original media: 189.20.
- Desviación estándar muestral: 106.54.
- Episodios truncados: 0 de 10.

### Interpretación y reproducción

La media aumentó respecto al ensayo inicial, evaluado con las mismas seeds.
Persisten dos episodios con recompensas negativas.
La reproducción de las seeds 1000, 1004 y 1006 coincidió con las recompensas
de evaluación.

### Clasificación física del aterrizaje

Se considera exitoso un episodio terminado sin truncamiento, sin choque
del cuerpo, con el cohete en reposo, ambas patas en contacto con el suelo
y su centro horizontal dentro de los límites de la plataforma.

- Aterrizajes exitosos: 6 de 10 (60 %).
- Choques del cuerpo: seeds 1004 y 1006.
- Reposo fuera de la plataforma: seeds 1007 y 1009.
- Plataforma: intervalo horizontal [8, 12].

Las seeds 1007 y 1009 superaron 200 puntos sin cumplir el criterio físico.
La recompensa y la tasa de éxito representan métricas diferentes.

Cuatro casos automatizados verifican el criterio: aterrizaje válido,
choque, posición fuera de plataforma y truncamiento.
Resultado: 4 pruebas aprobadas.

### Registro de trayectoria

Se registró el episodio del checkpoint neutral_baseline con seed 1000.

- Pasos: 331.
- Fotogramas: 332, incluyendo el estado inicial.
- Frecuencia de simulación: 50 FPS.
- Recompensa original: 263.58.
- Aterrizaje exitoso según el criterio físico: sí.

La trayectoria contiene la geometría del cohete, las patas y el escenario.
Se guarda como JSON junto con un UUID, el hash SHA-256 del checkpoint
y las versiones de las bibliotecas.

Se comprobó su recuperación mediante GET /api/rocket-ai/episodes/{episode_id}.
Los archivos generados permanecen excluidos de Git.