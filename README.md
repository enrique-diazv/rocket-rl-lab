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
- Clasificación física de aterrizajes y cuatro casos críticos cubiertos por pruebas automatizadas.
- Frontend conectado con FastAPI mediante el proxy de Vite.
- Inventario de checkpoints locales disponible en GET /api/rocket-ai/models.
- Selector de modelos en React con carga, validación de respuestas y manejo de errores.
- Grabación de trayectorias físicas y persistencia en JSON con identificación del checkpoint y versiones.
- Recuperación de episodios guardados mediante GET /api/rocket-ai/episodes/{episode_id}.
- Comprobación de conexión con estados de espera, éxito y error, y posibilidad de reintentar.

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

## Archivos generados

Los entornos, dependencias, compilaciones, secretos, checkpoints y
resultados de experimentos se excluyen mediante .gitignore.