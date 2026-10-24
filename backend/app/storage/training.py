from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
from platform import python_version
from uuid import UUID, uuid4
from csv import DictReader
from math import isfinite

TRAINING_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "experiments" / "training"
)


def create_training_run(config: dict[str, object]) -> Path:
    run_id = uuid4().hex
    run_directory = TRAINING_DIRECTORY / run_id

    payload = {
        "schema_version": 1,
        "id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "python_version": python_version(),
        "versions": {
            name: version(name)
            for name in (
                "gymnasium",
                "Box2D",
                "numpy",
                "stable-baselines3",
                "torch",
            )
        },
        "config": config,
    }

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        indent=2,
    )

    run_directory.mkdir(parents=True)
    temporary_path = run_directory / "config.tmp"
    destination = run_directory / "config.json"

    temporary_path.write_text(serialized, encoding="utf-8")
    temporary_path.replace(destination)

    return run_directory

@dataclass(frozen=True)
class TrainingSummary:
    id: str
    model_id: str
    created_at: str
    requested_timesteps: int
    reward_mode: str


def list_training_runs(*, model_id: str) -> list[TrainingSummary]:
    runs: list[TrainingSummary] = []

    for config_path in TRAINING_DIRECTORY.glob("*/config.json"):
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        config = payload["config"]
        recorded_model_id = Path(config["checkpoint_path"]).stem

        if recorded_model_id != model_id:
            continue

        runs.append(
            TrainingSummary(
                id=payload["id"],
                model_id=recorded_model_id,
                created_at=payload["created_at"],
                requested_timesteps=config["requested_timesteps"],
                reward_mode=config["reward"]["mode"],
            )
        )

    return sorted(
        runs,
        key=lambda run: run.created_at,
        reverse=True,
    )

@dataclass(frozen=True)
class TrainingPoint:
    timesteps: int
    mean_episode_reward: float
    mean_episode_length: float


def get_training_progress(run_id: UUID) -> list[TrainingPoint]:
    path = TRAINING_DIRECTORY / run_id.hex / "progress.csv"

    if not path.is_file():
        raise FileNotFoundError("No hay métricas para este entrenamiento.")

    columns = {
        "time/total_timesteps",
        "rollout/ep_rew_mean",
        "rollout/ep_len_mean",
    }
    points: list[TrainingPoint] = []

    with path.open(encoding="utf-8", newline="") as file:
        reader = DictReader(file)

        if not columns.issubset(reader.fieldnames or []):
            raise ValueError("El CSV no contiene las columnas requeridas.")

        for row in reader:
            if any(
                row[column] is None or not row[column].strip()
                for column in columns
            ):
                continue

            timesteps = int(row["time/total_timesteps"])
            reward = float(row["rollout/ep_rew_mean"])
            length = float(row["rollout/ep_len_mean"])

            if (
                timesteps <= 0
                or not isfinite(reward)
                or not isfinite(length)
                or length <= 0
            ):
                raise ValueError("El CSV contiene métricas inválidas.")

            if points and timesteps <= points[-1].timesteps:
                raise ValueError("Los pasos del entrenamiento no avanzan.")

            points.append(
                TrainingPoint(
                    timesteps=timesteps,
                    mean_episode_reward=reward,
                    mean_episode_length=length,
                )
            )

    return points