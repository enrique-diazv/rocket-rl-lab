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
- Creación del simulador centralizada en app/rl/env_factory.py.
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

Con `--time-penalty 0`, `--hover-bonus 0` y `--progress-weight 0`
se conserva la recompensa original.

- `--time-penalty` resta un costo en cada paso.
- `--hover-bonus` agrega un premio en cada paso que cumple la condición de estabilidad.
- `--progress-weight` pondera el cambio de distancia al objetivo, calculado con las coordenadas normalizadas de la observación.

Cada ensayo guarda configuración y métricas en
backend/experiments/training/<id>.
Las recompensas de entrenamiento incluyen el shaping.

Para evaluar el modelo con la recompensa original:

```powershell
& .\.venv\Scripts\python.exe -m app.rl.evaluate --checkpoint checkpoints/mi_experimento.zip
```

## Archivos generados

Los entornos, dependencias, compilaciones, secretos, checkpoints y
resultados de experimentos se excluyen mediante .gitignore.