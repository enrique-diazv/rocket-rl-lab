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

- Instalación de Gymnasium, Box2D, Stable-Baselines3 y PyTorch comprobada.
- Creación de LunarLander-v3 y ejecución de un paso comprobadas.
- Plantilla React con TypeScript compilada.
- Dependencias de FastAPI y pruebas instaladas.
- API, entrenamiento y pruebas propias pendientes de implementar.

## Archivos generados

Los entornos, dependencias, compilaciones, secretos, checkpoints y
resultados de experimentos se excluyen mediante .gitignore.