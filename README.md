# Rocket RL Lab

Proyecto educativo de aprendizaje por refuerzo para entrenar un agente
PPO en LunarLander-v3 y estudiar el diseño de recompensas.

Primero desarrollaremos Rocket AI y los experimentos de reward shaping.
Adaptation Challenge será una extensión posterior.

## Entorno de desarrollo

- Windows con PowerShell.
- Python 3.13 de 64 bits.
- Node.js 24 y npm.
- Entrenamiento local con CPU.

## Preparar el proyecto

Ejecutar desde la raíz del repositorio.

### Backend

Crear el entorno e instalar primero PyTorch desde su repositorio de CPU:

```powershell
py -3.13 -m venv backend\.venv
& .\backend\.venv\Scripts\python.exe -m pip install "torch==2.14.1+cpu" --index-url https://download.pytorch.org/whl/cpu
& .\backend\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
& .\backend\.venv\Scripts\python.exe -m pip check
```

### Frontend

Instalar las versiones registradas en package-lock.json y compilar:

```powershell
npm --prefix frontend ci
npm --prefix frontend run build
```

## Estado actual

- Dependencias del backend instaladas y comprobadas.
- Plantilla React con TypeScript compilada.
- Ruta GET /api/health comprobada manualmente.
- Entorno neutro en app/rl/env_factory.py y escenarios configurables en app/rl/scenario_env.py.
- Evaluación reutilizable desde Python, compartida con el comando de consola.
- Funciones para continuar los checkpoints de las especialidades por bloques, con presupuesto limitado y conteo de pasos adicionales y episodios nuevos.
- Agente aleatorio ejecutado durante tres episodios con seeds definidas.
- Checkpoints PPO de 10 240 y 1 024 000 pasos, guardados y cargados.
- Ambos checkpoints evaluados con las mismas diez seeds; resultados en docs/experiment-results.md.
- Evaluación y visualización con selección de checkpoint desde la consola; visualización con seeds configurables.
- Clasificación física de aterrizajes con pruebas de choque, ubicación, truncamiento y apoyo de las patas.
- Frontend conectado con FastAPI mediante el proxy de Vite.
- Inventario de checkpoints locales disponible en GET /api/rocket-ai/models.
- Selector de modelos en React con carga, validación de respuestas y manejo de errores.
- Grabación de trayectorias físicas y persistencia en JSON con identificación del checkpoint y versiones.
- Recuperación de episodios guardados mediante GET /api/rocket-ai/episodes/{episode_id}.
- Comprobación de conexión con estados de espera, éxito y error, y posibilidad de reintentar.
- Consulta de episodios guardados por modelo mediante `GET /api/rocket-ai/episodes`.
- Selector de episodios en React con validación de las respuestas mediante Zod.
- Descarga de trayectorias completas con validación mediante Zod e identificación del episodio y modelo.
- Visualización en Canvas del terreno, plataforma y nave usando las coordenadas grabadas del simulador.
- Reproducción según los FPS del episodio, con pausa, deslizador y reinicio al finalizar.
- Persistencia de evaluaciones con resultados por episodio, pasos de entrenamiento, hash del checkpoint y versiones.
- Consulta del listado de evaluaciones por modelo y recuperación de su detalle mediante la API.
- Selección de evaluaciones por modelo y visualización de sus métricas con validación de datos mediante Zod.
- Gráficas de recompensa original y duración por seed, y porcentaje de aterrizajes exitosos y no exitosos.
- Carga de las gráficas bajo demanda mediante React.lazy y Suspense.
- Wrapper de penalización temporal configurable, con registro separado de recompensa original, adicional y total, validado mediante dos pruebas de integración.
- Entorno local verificado con NumPy 2.3.5, pygame-ce 2.5.6 y Smart App Control activo.
- Entrenamiento configurable por consola, con protección contra sobrescritura de checkpoints.
- Registro de configuración y versiones en JSON, y métricas en CSV con retornos original, adicional y total separados por episodio.
- Métrica de aterrizaje basada en contactos físicos activos de Box2D, con pruebas de regresión y comparación documentada entre referencia y penalización temporal.
- Reward shaping configurable por consola: penalización temporal, premio por estabilidad y recompensa por progreso, con comparación de cuatro configuraciones y replays de éxitos y fallos.
- Consulta de entrenamientos por modelo y lectura de métricas reales desde los CSV de PPO mediante la API.
- Selector de entrenamientos, curvas de recompensa y duración, resumen del último registro y tabla numérica, con validación mediante Zod y carga diferida de las gráficas.
- Cinco perfiles PPO (Precision, Speed, Efficiency, Stability y Balanced) preentrenados en condiciones neutras con un presupuesto común de 1.024.000 pasos; resultados y limitaciones en el [registro de experimentos](docs/experiment-results.md).
- Métricas por episodio de error horizontal final, costo relativo de motores y movimiento previo al contacto, con tabla en la web y compatibilidad con evaluaciones antiguas.

## Ejecutar en desarrollo

Mantener ambos servidores activos en terminales separadas.

### Backend

Desde la carpeta backend:

```powershell
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Frontend

Desde la carpeta frontend:

```powershell
npm run dev
```

Abrir http://127.0.0.1:5173 y pulsar «Comprobar conexión».
El proxy de desarrollo reenvía las rutas /api a FastAPI en el puerto 8000.

## Entrenamiento por consola

Desde la carpeta backend, utilizando un nombre de checkpoint nuevo:

```powershell
& .\.venv\Scripts\python.exe -m app.rl.train --checkpoint checkpoints/mi_experimento.zip --timesteps 10240 --time-penalty 0.05
```

Los pasos deben ser positivos y múltiplos de 2048.

Con `--time-penalty 0`, `--hover-bonus 0`, `--progress-weight 0`,
`--horizontal-progress-weight 0`, `--fuel-penalty 0`
y `--stability-penalty 0` se conserva la recompensa original.
- `--time-penalty` resta un costo en cada paso.
- `--hover-bonus` agrega un premio en cada paso que cumple la condición de estabilidad.
- `--progress-weight` pondera el cambio de distancia al objetivo, calculado con las coordenadas normalizadas de la observación.
- `--horizontal-progress-weight` pondera la reducción del error horizontal respecto al centro: `abs(x anterior) - abs(x actual)`. Acercarse suma, alejarse resta y mantener el mismo error aporta cero.
- `--fuel-penalty` multiplica un costo adicional por uso de motores: `0` sin propulsión, `0.03` para un lateral y `0.30` para el principal. Estos costos relativos no representan un tanque de combustible finito.
- `--stability-penalty` multiplica un costo por paso calculado como la suma de cuadrados de las velocidades horizontal y vertical, la inclinación y el giro de la observación (`observation[2:6]`). Las velocidades utilizan las escalas de Gymnasium.
`--agent` selecciona un perfil inicial: `precision`, `speed`,
`efficiency`, `stability` o `balanced`. Sus pesos se definen en
`backend/app/rl/agent_profiles.py`.

Los parámetros de recompensa proporcionados explícitamente reemplazan
los valores del perfil, incluso cuando su valor es cero.
Sin `--agent`, los pesos omitidos se resuelven a cero.

Cada experimento registra el perfil seleccionado en `agent_profile`
y los pesos efectivos en `reward`. Los perfiles son configuraciones
exploratorias; sus nombres no demuestran comportamientos aprendidos.

Cada ensayo guarda configuración y métricas en
backend/experiments/training/<id>.
Las recompensas de entrenamiento incluyen el shaping.

Para evaluar el modelo con la recompensa original:

```powershell
& .\.venv\Scripts\python.exe -m app.rl.evaluate --checkpoint checkpoints/mi_experimento.zip
```
## Evaluación con escenario configurable

Desde la carpeta backend, usando un checkpoint existente:

```powershell
& .\.venv\Scripts\python.exe -m app.rl.evaluate `
    --checkpoint checkpoints/stability.zip `
    --gravity -5 `
    --max-episode-steps 5
```

Este ejemplo verifica el corte del episodio a los cinco pasos;
no ofrece tiempo suficiente para aterrizar.

- `--gravity` acepta valores finitos mayores que -12 y menores que 0.
- `--max-episode-steps` acepta enteros positivos.
- Sin estos parámetros se utilizan gravedad -10 y límite de 1000 pasos.
- La evaluación utiliza la recompensa original del escenario elegido,
  sin agregar reward shaping ni entrenar el modelo.
- Cada nuevo resultado guarda su configuración en `scenario`.
  La web muestra esos valores y señala cuando un registro antiguo
  no incluye la configuración.

### Combustible finito

El evaluador acepta `--fuel-budget` con una capacidad finita,
mayor o igual a cero. Omitirlo conserva combustible ilimitado.

El consumo por paso utiliza unidades relativas:
0 sin propulsión, 0.03 para un lateral y 0.30 para el principal.
No representa litros ni una magnitud física calibrada.

Si no alcanza para la acción solicitada, se ejecuta ese paso
sin propulsión y sin consumir combustible. No hay encendidos
parciales. El vuelo continúa hasta su final físico o límite
temporal; quedarse sin combustible no termina el episodio.
Cada reset recarga el tanque.

Ejemplo desde backend, con un checkpoint existente:

```powershell
& .\.venv\Scripts\python.exe -m app.rl.evaluate `
    --checkpoint checkpoints/stability.zip `
    --fuel-budget 0 `
    --max-episode-steps 5
```

El consumo registrado y la penalización adicional por combustible
utilizan las acciones efectivamente ejecutadas. `--fuel-penalty`
modifica la recompensa; `--fuel-budget` limita la propulsión.

La web distingue capacidad numérica, combustible ilimitado
y capacidad no registrada en evaluaciones anteriores.

### Plataforma variable

`--platform-width-scale` acepta valores finitos entre 0.25 y 2.0,
incluidos ambos extremos. Su valor predeterminado es 1.0.

La escala cambia el ancho conservando el centro y las alturas.
Se reconstruyen los segmentos de colisión y el terreno dibujado.
Cada reset aplica la escala sobre el terreno recién generado;
la escala 1.0 conserva el entorno original.

Ejemplo desde backend, con un checkpoint existente:

```powershell
& .\.venv\Scripts\python.exe -m app.rl.evaluate `
    --checkpoint checkpoints/stability.zip `
    --platform-width-scale 0.5
```
La configuración se guarda en `scenario.platform_width_scale`
y se muestra junto a los resultados de evaluación.

Se conservan las ocho observaciones originales. Los parámetros
del escenario no se incorporan directamente a la observación.

## Adaptación por consola

Desde backend, con el checkpoint de la especialidad disponible:

```powershell
& .\.venv\Scripts\python.exe -m app.rl.adapt `
    --agent stability `
    --config configs/narrow_pad.json
```

La configuración de ejemplo permite 20.480 pasos adicionales,
en bloques de 10.240, sobre una plataforma con la mitad del ancho.

Se evalúa antes de entrenar y después de cada bloque, usando
30 semillas fijas. El criterio exige al menos 90% de éxito
en dos evaluaciones consecutivas. Si supera el control inicial,
se confirma con otras 30 semillas antes de marcar `already_adapted`.

Cada ejecución guarda configuración, checkpoints, evaluaciones
y resultado en `backend/experiments/adaptations/<id>/<agente>/`.

Los estados finales son `already_adapted`, `adapted` y
`budget_reached`. Agotar el presupuesto no implica alcanzar
el criterio. El checkpoint original se conserva.

## Archivos generados

Los entornos, dependencias, compilaciones, secretos, checkpoints y
resultados de experimentos se excluyen mediante .gitignore.