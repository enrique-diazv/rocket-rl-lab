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

### Persistencia de evaluaciones

Se repitió la evaluación de neutral_baseline con las seeds 1000–1009.
Se conservaron la recompensa original media de 189.20 y los 6/10
aterrizajes exitosos.

Los resultados por episodio se guardaron en JSON junto con el hash
del checkpoint, sus pasos de entrenamiento y las versiones utilizadas.

Se verificaron por HTTP el listado filtrado por modelo y la recuperación
del detalle completo de la evaluación.

### Visualización de la evaluación

Se verificó en la interfaz la evaluación de neutral_baseline:
10 episodios, recompensa original media de 189.20 y 6/10
aterrizajes exitosos.

Las gráficas muestran la recompensa original y la duración por seed,
junto con un 60 % de episodios exitosos y un 40 % no exitosos.
Corresponden a los diez episodios evaluados del checkpoint.

Las comprobaciones de lint y compilación del frontend finalizaron
correctamente.

## Verificación del entorno y del wrapper temporal

Smart App Control bloqueó una extensión nativa de NumPy 2.5.4.
Se instaló NumPy 2.3.5 manteniendo esa protección activa.

Pasaron seis pruebas: cuatro de clasificación de aterrizajes y dos
de integración del wrapper, con penalizaciones temporales de 0 y 0.05.
Estas últimas verifican que se conservan las observaciones, las condiciones
de finalización y el acceso a la recompensa original.

Se reevaluó neutral_baseline con las seeds 1000–1009:
- Recompensa original media: 189.20.
- Desviación estándar muestral: 106.54.
- Aterrizajes exitosos: 6/10.

Las recompensas mostradas, los pasos y las clasificaciones coincidieron
con la evaluación anterior.

## Ensayo 003: validación del entrenamiento con penalización temporal

### Configuración

- Modelo nuevo entrenado desde cero, usando CPU.
- Seed: 42.
- Pasos entrenados: 10 240.
- Penalización temporal: 0.05 por paso.
- Arquitectura: [64, 64].
- Pasos por bloque: 2048.
- Tamaño de minibatch: 64.
- NumPy: 2.3.5.
- Checkpoint: backend/checkpoints/neutral_time_penalty_smoke.zip.
- Identificador del entrenamiento: 9dc9eae83fe54a22b6ecd9bb7dc7c569.

Se verificaron config.json, progress.csv y episodes.monitor.csv.
El último registro de recompensa media de entrenamiento fue -150.88,
incluyendo la penalización temporal.

### Evaluación con recompensa original

- Seeds: 1000–1009, con acciones deterministas.
- Recompensa original media: -470.19.
- Desviación estándar muestral: 309.25.
- Aterrizajes exitosos: 0/10.
- Episodios truncados: 0/10.
- Identificador de evaluación: 481a91ef4fe749e69df7d7f428e4a9b5.

El objetivo de este ensayo fue comprobar entrenamiento, registro,
guardado y carga del modelo. La comparación del efecto de la penalización
utilizará el mismo presupuesto y dependencias para ambos modelos.

### Dependencia gráfica

Durante el entrenamiento apareció un bloqueo de pygame.pixelcopy
con pygame-ce 2.5.8. Después se instaló pygame-ce 2.5.6 y se verificó
su importación, manteniendo Smart App Control activo.

La comprobación final terminó con seis pruebas aprobadas.

## Verificación del registro de retornos por episodio

- Experimento: `967eafd99f8a492f9efab49c46113209`.
- Entrenamiento técnico de 2.048 pasos con penalización temporal de 0.05.
- Se verificaron las columnas `base_return`, `shaping_return` y `total_return` en `episodes.monitor.csv`.
- La penalización acumulada corresponde a `-0.05 × pasos`; el retorno total coincide con la suma de sus componentes.
- Las pruebas del wrapper verifican los acumuladores durante dos episodios consecutivos.
- Esta ejecución valida el registro; no permite concluir si la penalización mejora el aprendizaje.

## Comparación controlada: referencia y penalización temporal

Ambos modelos se entrenaron desde cero durante 1.024.000 pasos, con
semilla 42, la misma configuración de PPO y las mismas versiones de
dependencias. La evaluación utiliza recompensa original, política
determinista y semillas 1000 a 1009.

| Métrica | Referencia | Penalización de 0.05 por paso |
| --- | ---: | ---: |
| Recompensa original media | 189.20 | 252.90 |
| Desviación estándar | 106.54 | 24.80 |
| Aterrizajes exitosos | 6/10 | 10/10 |
| Tasa de éxito | 60 % | 100 % |
| Pasos medios por episodio | 296.4 | 333.4 |

### Corrección de la métrica de aterrizaje

Los indicadores `ground_contact` de Gymnasium produjeron cuatro falsos
negativos en el modelo con penalización: las patas conservaban contactos
físicos activos aunque sus indicadores estuvieran en False.

La métrica ahora consulta los contactos activos de Box2D con el terreno.
Conserva los requisitos de ambas patas apoyadas, ausencia de choque,
cuerpo en reposo, centro dentro de la plataforma y final sin truncamiento.

Las pruebas incluyen apoyo físico con indicadores incorrectos y rechazo
cuando solamente una pata tiene contacto.

### Registros

- Referencia: `neutral_baseline_logged.zip`.
- Entrenamiento de referencia: `bc5fb6334f8f4f8c8d8240879bd3e756`.
- Evaluación corregida de referencia: `a5d9db38c06d45ba9e46a3a29316fb45`.
- Penalización: `neutral_time_penalty.zip`.
- Entrenamiento con penalización: `f5c3c85412d946309d59b1d2639066df`.
- Evaluación corregida con penalización: `ca0ca51ef20a44978f654d378c8fc746`.
- La evaluación anterior `c169b65639f1470d8a37d66fe73fdc38`
  subestimaba el éxito; se conserva como antecedente.

### Interpretación

En estas diez semillas, la penalización obtuvo mayor recompensa y más
aterrizajes exitosos, pero no redujo la duración media de los episodios.
La comparación utiliza una sola semilla de entrenamiento por configuración;
el 100 % observado no garantiza éxito en otros escenarios o semillas.

## Reward hacking: premio por estabilidad sin progreso

### Configuración

- Checkpoint: `neutral_hover_bonus.zip`.
- Entrenamiento desde cero: 1.024.000 pasos, semilla 42.
- Misma configuración de PPO que las comparaciones anteriores.
- Premio: +1 por paso con inclinación absoluta <= 0.1 radianes
  y norma de velocidad de la observación <= 0.2.
- Sin penalización temporal.
- El premio exige estabilidad, pero no progreso hacia el aterrizaje.
- Entrenamiento: `d3af15affe3a4f009ebad4f4d069fb58`.

### Resultados

Último registro de entrenamiento, con el premio adicional incluido:

- Recompensa media de episodios: aproximadamente 762.
- Duración media de episodios: aproximadamente 914 pasos.

Evaluación con recompensa original y semillas 1000 a 1009:

- Recompensa media: -39.90.
- Desviación estándar: 23.85.
- Aterrizajes exitosos: 0/10.
- Los diez episodios alcanzaron el límite de 1.000 pasos.
- Evaluación: `0d6b3f97336349318584674161f9027a`.

### Evidencia del comportamiento

En la seed 1000, los últimos 500 pasos transcurrieron sin contacto
físico de las patas con el terreno. La altura del cuerpo respecto
a la plataforma estuvo entre 1.823 y 4.834 unidades del mundo.

- Recompensa original de ese episodio: -62.65.
- Replay: `844a1b67b89a4a098e5c2533a5bb6ba9`.

### Interpretación

El premio permite acumular recompensa por permanecer estable sin
aterrizar. La política aprendida prolonga el vuelo y agota el tiempo:
la recompensa diseñada favorece un comportamiento distinto del objetivo.

Este resultado corresponde a una ejecución de entrenamiento.
La siguiente comparación sustituirá el premio por permanencia por
una señal de progreso y un costo temporal.

## Corrección: progreso hacia el objetivo y costo temporal

### Configuración

- Checkpoint: `neutral_hover_fixed.zip`.
- Entrenamiento desde cero: 1.024.000 pasos, semilla 42.
- Misma configuración de PPO que los experimentos anteriores.
- Premio por estabilidad deshabilitado.
- Penalización temporal: 0.05 por paso.
- Peso del progreso: 10.
- Distancia: norma euclidiana de las coordenadas normalizadas x e y.
- Shaping: `10 × (distancia anterior − distancia actual) − 0.05`.
- Entrenamiento: `be2d8220ad274c71b4bd98d3db67e45f`.

La prueba del progreso comprueba acercamiento, alejamiento, recorridos
cerrados y reinicio de la distancia entre episodios.

### Comparación con recompensa original

Todos los modelos se evaluaron con política determinista, semillas
1000 a 1009 y la métrica de contactos físicos activos.

| Configuración | Recompensa media | Desviación estándar | Éxitos | Pasos medios | Truncamientos |
| --- | ---: | ---: | ---: | ---: | ---: |
| Referencia | 189.20 | 106.54 | 6/10 | 296.4 | 0 |
| Costo temporal | 252.90 | 24.80 | 10/10 | 333.4 | 0 |
| Premio por estabilidad | -39.90 | 23.85 | 0/10 | 1000.0 | 10 |
| Progreso + costo temporal | 212.53 | 92.32 | 6/10 | 411.6 | 2 |

Evaluación de la corrección: `2bbaf1e289134254b533fbc519d05262`.

### Fallos de la configuración corregida

- Seeds 1001 y 1006: límite de tiempo alcanzado.
- Seed 1004: reposo y ambas patas apoyadas, pero centro fuera
  de la plataforma: x=7.4821 frente al intervalo [8, 12].
- Seed 1009: choque del cuerpo, aunque ambas patas tenían contacto.

### Replays guardados

- Seed 1000: éxito, recompensa 286.97, 283 pasos.
  Replay: `1fe46619516c4333a8c544d49405401c`.
- Seed 1001: truncamiento, recompensa 119.74, 1000 pasos.
  Replay: `af5f49169529430f8e9be7127920b4af`.

### Conclusiones

Sustituir el premio por permanencia por progreso y costo temporal
recuperó aterrizajes exitosos y redujo los truncamientos en esta ejecución.

La configuración con solo costo temporal obtuvo el mejor resultado
observado: 10/10 éxitos. Agregar progreso no la superó.

Los truncamientos indican que no se completó el aterrizaje a tiempo;
por sí solos no demuestran el mismo mecanismo de reward hacking.

Estos resultados utilizan una sola semilla de entrenamiento y diez
episodios de evaluación por configuración. No garantizan el mismo
desempeño en otras semillas o escenarios.

## Precision: verificación inicial del progreso horizontal

- Checkpoint: `precision_smoke.zip`.
- Entrenamiento desde cero: 2.048 pasos, semilla 42.
- Entorno estándar `LunarLander-v3`.
- Peso del progreso horizontal: 10.
- Penalización temporal: 0.05 por paso.
- Premio por estabilidad y progreso euclidiano deshabilitados.
- Shaping: `10 × (abs(x anterior) − abs(x actual)) − 0.05`.
- Entrenamiento: `74f0950bbb4943dfafeaa44fa0fef71a`.

La ejecución completó el presupuesto y guardó el checkpoint,
la configuración y las métricas. Esta prueba verifica la integración;
no permite concluir que Precision haya aprendido a aterrizar.
No se realizó una evaluación de rendimiento de este checkpoint.

## Efficiency: comprobación inicial del costo de motores

Se verificaron las cuatro acciones del entorno estándar con
`fuel_penalty=1.0`, reiniciando con semilla 42 antes de cada acción.

| Acción | Ajuste adicional |
| --- | ---: |
| 0: sin propulsión | 0.00 |
| 1: motor lateral | -0.03 |
| 2: motor principal | -0.30 |
| 3: motor lateral | -0.03 |

La comprobación valida el componente de penalización por motores.
Todavía no se entrenó ni evaluó una política Efficiency.

## Stability: verificación inicial de integración

- Checkpoint: `stability_smoke.zip`.
- Entrenamiento desde cero: 2.048 pasos, semilla 42.
- Entorno estándar `LunarLander-v3`.
- Penalización temporal: 0.05 por paso.
- Peso del progreso euclidiano: 10.
- Penalización por inestabilidad: 0.1.
- Premio por estabilidad, progreso horizontal y costo adicional
  de motores deshabilitados.
- Inestabilidad: suma de cuadrados de `observation[2:6]`.
- Entrenamiento: `da6deccbe38c4c06b99618de296a2155`.

La ejecución completó el presupuesto y guardó el checkpoint,
la configuración y las métricas. Esta comprobación valida la integración;
todavía no demuestra una mejora en la estabilidad de los aterrizajes.
No se realizó una evaluación de rendimiento de este checkpoint.

## Perfiles: integración y prioridad de parámetros

- Checkpoint: `balanced_profile_smoke.zip`.
- Entrenamiento desde cero: 2.048 pasos, semilla 42.
- Perfil inicial: `balanced`.
- Sobrescritura explícita: `--fuel-penalty 0`.
- Pesos efectivos: tiempo 0.05, progreso euclidiano 5,
  progreso horizontal 5, combustible 0 e inestabilidad 0.05.
- Premio por estabilidad deshabilitado.
- Entrenamiento: `eec46eebf5c543cabb3b4eebba129fc3`.

La ejecución confirmó que el perfil aporta los valores iniciales
y que un cero explícito reemplaza el costo de combustible del perfil.
El checkpoint, la configuración y las métricas quedaron guardados.
No se evaluó el rendimiento de esta política.

## Especialidades en condiciones neutras

### Precision

- Perfil: `precision`, sin sobrescrituras.
- Checkpoint: `precision.zip`.
- Entrenamiento desde cero: 1.024.000 pasos, semilla 42.
- Penalización temporal: 0.05.
- Peso del progreso horizontal: 10.
- Entrenamiento: `9736a5602d9f4af7b569b47b4b60ea5c`.
- Evaluación: `db4f1db9115647d28ad1df1cec84534a`.

Evaluación determinista con recompensa original y semillas 1000–1009:

| Métrica | Resultado |
| --- | ---: |
| Recompensa media | 249.29 |
| Desviación estándar | 35.28 |
| Aterrizajes exitosos | 8/10 |
| Pasos medios por episodio | 391.8 |
| Truncamientos | 1 |

Fallos observados:

- Seed 1004: alcanzó el límite de 1.000 pasos.
- Seed 1006: sin choque, en reposo y con ambas patas apoyadas,
  pero con el centro fuera de la plataforma:
  x=7.9529 frente al intervalo [8, 12].

El resultado demuestra ocho aterrizajes válidos en esta evaluación.
Todavía no demuestra una mayor precisión que las otras especialidades:
falta comparar sus errores horizontales con un protocolo común.

### Speed

- Perfil: `speed`, sin sobrescrituras.
- Checkpoint: `speed.zip`.
- Entrenamiento desde cero: 1.024.000 pasos, semilla 42.
- Penalización temporal: 0.10 por paso.
- Los demás ajustes adicionales están deshabilitados.
- Entrenamiento: `cbc77a3f477847558c5be065ea813bc2`.
- Evaluación: `bf42258dda634a9db8792117e406357d`.

Evaluación determinista con recompensa original y semillas 1000–1009:

| Métrica | Resultado |
| --- | ---: |
| Recompensa media | 234.17 |
| Desviación estándar | 51.82 |
| Aterrizajes exitosos | 6/10 |
| Pasos medios por episodio | 376.9 |
| Truncamientos | 1 |

Fallos observados:

- Seeds 1000, 1004 y 1006: sin choque, en reposo y con ambas patas
  apoyadas, pero fuera de la plataforma [8, 12].
  Sus posiciones finales fueron 6.4538, 1.9782 y 5.4019, respectivamente.
- Seed 1008: alcanzó el límite de 1.000 pasos.

La duración media incluye episodios fallidos. Su valor inferior al
de Precision no basta para concluir que Speed aterriza más rápido:
obtuvo menos aterrizajes válidos en esta evaluación.

### Efficiency

- Perfil: `efficiency`, sin sobrescrituras.
- Checkpoint: `efficiency.zip`.
- Entrenamiento desde cero: 1.024.000 pasos, semilla 42.
- Penalización temporal: 0.05 por paso.
- Multiplicador del costo adicional de motores: 1.0.
- Los demás ajustes adicionales están deshabilitados.
- Entrenamiento: `478cec8d09be42ffba0608c73d01cfdc`.
- Evaluación: `b26237abe6be44a3ae892b673378beb4`.

Evaluación determinista con recompensa original y semillas 1000–1009:

| Métrica | Resultado |
| --- | ---: |
| Recompensa media | 179.44 |
| Desviación estándar | 114.94 |
| Aterrizajes exitosos | 6/10 |
| Pasos medios por episodio | 438.7 |
| Truncamientos | 2 |

Fallos observados:

- Seeds 1001 y 1009: choque y cuerpo sin reposo, aunque ambas patas
  tenían contacto. Sus posiciones finales fueron 12.1870 y 12.5923,
  fuera de la plataforma [8, 12].
- Seeds 1004 y 1007: alcanzaron el límite de 1.000 pasos.

Todavía no se midió el uso de motores durante la evaluación.
Estos resultados no permiten concluir que Efficiency ahorre más
combustible que las otras especialidades.

### Stability

- Perfil: `stability`, sin sobrescrituras.
- Checkpoint: `stability.zip`.
- Entrenamiento desde cero: 1.024.000 pasos, semilla 42.
- Penalización temporal: 0.05 por paso.
- Peso del progreso euclidiano: 10.
- Penalización por inestabilidad: 0.10.
- Los demás ajustes adicionales están deshabilitados.
- Entrenamiento: `81d13ac42ffa470f87c837ef327b962e`.
- Evaluación: `01737c1c4ccf402297c2e4335d2a258e`.

Evaluación determinista con recompensa original y semillas 1000–1009:

| Métrica | Resultado |
| --- | ---: |
| Recompensa media | 279.77 |
| Desviación estándar | 17.00 |
| Aterrizajes exitosos | 10/10 |
| Pasos medios por episodio | 222.1 |
| Truncamientos | 0 |

Los diez episodios cumplieron el criterio físico de aterrizaje.
El 100% corresponde únicamente a esta muestra de evaluación.

Falta medir velocidad, inclinación y giro con un protocolo común
para determinar si Stability presenta un comportamiento más estable
que las otras especialidades.

### Balanced

- Perfil: `balanced`, sin sobrescrituras.
- Checkpoint: `balanced.zip`.
- Entrenamiento desde cero: 1.024.000 pasos, semilla 42.
- Penalización temporal: 0.05 por paso.
- Progreso euclidiano y horizontal: peso 5 cada uno.
- Multiplicador del costo adicional de motores: 0.5.
- Penalización por inestabilidad: 0.05.
- Premio por estabilidad deshabilitado.
- Entrenamiento: `ad61d95973ba436e89e0f5ea1d9eedda`.
- Evaluación: `db5b82bed4ce4e298f8e65625ea2c76e`.

Evaluación determinista con recompensa original y semillas 1000–1009:

| Métrica | Resultado |
| --- | ---: |
| Recompensa media | 211.80 |
| Desviación estándar | 101.74 |
| Aterrizajes exitosos | 6/10 |
| Pasos medios por episodio | 328.5 |
| Truncamientos | 0 |

Fallos observados:

- Seeds 1001, 1005 y 1007: sin choque, en reposo y con ambas patas
  apoyadas, pero fuera de la plataforma [8, 12].
  Sus posiciones finales fueron 17.3394, 12.0673 y 15.7187,
  respectivamente.
- Seed 1009: choque y cuerpo sin reposo, con ambas patas en contacto.
  Su posición final fue 12.7264, también fuera de la plataforma.

Combinar los objetivos produjo seis aterrizajes válidos en esta
evaluación. Falta medir precisión, uso de motores y estabilidad
para comparar las especialidades según sus objetivos.

## Ampliación de la evaluación: métricas de comportamiento

Se repitieron las evaluaciones de los cinco checkpoints sobre las
semillas 1000–1009, sin entrenamiento adicional. Se conservaron
las recompensas, duraciones y clasificaciones anteriores.

Esta ampliación cubre las mediciones pendientes de las evaluaciones
iniciales:

- Error horizontal final: distancia absoluta entre el centro del
  cuerpo y el centro de la plataforma, en unidades del mundo.
- Costo de motores: suma de los costos relativos por acción
  `[0, 0.03, 0.30, 0.03]`, independiente del shaping de cada perfil.
- Movimiento previo al contacto: instantánea del paso anterior
  al primer contacto de las patas detectado mediante Box2D.
  Es una aproximación, no la medición exacta del instante del impacto.
- Velocidad en unidades del mundo por segundo; inclinación absoluta
  en radianes y velocidad angular absoluta en radianes por segundo.
- Los registros antiguos muestran «No medido» en la tabla de la web.

Evaluaciones ampliadas:

- Precision: `61b0a8408b67451f8b56670326395452`.
- Speed: `bd70e1680ce243b591389c678a419ec0`.
- Efficiency: `171198cdb10b41eb90f7798d010445c9`.
- Stability: `e28b270cab22460aaf314988ebe99832`.
- Balanced: `2cae1d82a1f14c099e0999a0018f94ae`.

### Comparación sobre aterrizajes válidos compartidos

Solo las semillas 1002 y 1003 fueron exitosas para los cinco perfiles.
Las siguientes cifras son medias sobre esos dos episodios por perfil.
Velocidad, inclinación y giro corresponden al movimiento previo
al contacto.

| Perfil | Pasos | Error final | Costo motores | Velocidad | Inclinación | Giro |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Precision | 288.0 | 0.385 | 39.720 | 2.046 | 0.016 | 0.069 |
| Speed | 310.0 | 0.808 | 37.920 | 1.342 | 0.022 | 0.030 |
| Efficiency | 332.0 | 0.782 | 43.290 | 1.338 | 0.021 | 0.031 |
| Stability | 224.5 | 0.402 | 28.110 | 1.172 | 0.045 | 0.085 |
| Balanced | 340.0 | 0.438 | 40.560 | 1.473 | 0.057 | 0.061 |

En este subconjunto, Precision obtuvo el menor error horizontal;
Stability necesitó menos pasos y menor costo de motores, pero no
presentó la menor inclinación ni el menor giro.

Los nombres de los perfiles expresan objetivos de entrenamiento,
no garantías de comportamiento. La comparación es exploratoria:
utiliza una sola semilla de entrenamiento y únicamente dos semillas
de evaluación exitosas compartidas.

## Escenarios: gravedad y límite de pasos

Prueba de integración con `stability.zip`, sin entrenamiento adicional:

- Gravedad: -5.
- Límite: 5 pasos por episodio.
- Evaluación determinista con semillas 1000–1009.
- Evaluación: `c94a9d935ab143aeaecfaa3bc7d64863`.
- Recompensa original media: 1.20.
- Desviación estándar: 2.22.
- Aterrizajes exitosos: 0/10.
- Los diez episodios alcanzaron cinco pasos y finalizaron
  con `terminated=False` y `truncated=True`.
- El JSON registra ambos parámetros dentro de `scenario`.

Esta prueba comprueba la integración y el límite temporal.
No mide adaptación ni permite atribuir el resultado a la gravedad,
porque también se redujo el tiempo disponible.

## Escenarios: combustible finito

Prueba de integración con `stability.zip`, sin entrenamiento adicional:

- Gravedad: -10.
- Límite: 5 pasos por episodio.
- Capacidad inicial de combustible: 0.
- Evaluación determinista con semillas 1000–1009.
- Evaluación: `24674f29d8ff405286dc31def5486a85`.
- Recompensa original media: -1.14.
- Desviación estándar: 5.44.
- Aterrizajes exitosos: 0/10.
- Diez episodios truncados a los cinco pasos.
- Costo de motores: cero en todos los episodios.

Dos casos automatizados comprueban tanque vacío y agotamiento,
comparando la física con las acciones esperadas. También verifican
recarga mediante reset y penalización por consumo efectivo.

Esta ejecución breve verifica la integración del tanque,
no la capacidad de adaptación del modelo.