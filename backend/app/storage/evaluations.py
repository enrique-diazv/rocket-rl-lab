from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
from uuid import UUID, uuid4
from app.rl.evaluation_metrics import EpisodeEvaluation
from app.rl.scenario_config import ScenarioConfig

EVALUATION_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "experiments" / "evaluations"
)


def save_evaluation(
    episodes: list[EpisodeEvaluation],
    *,
    checkpoint_path: Path,
    training_timesteps: int,
    scenario: ScenarioConfig,
) -> Path:
    if not episodes:
        raise ValueError("La evaluación debe contener episodios.")

    evaluation_id = uuid4().hex

    payload = {
        "schema_version": 1,
        "id": evaluation_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": checkpoint_path.stem,
        "checkpoint_sha256": sha256(checkpoint_path.read_bytes()).hexdigest(),
        "training_timesteps": training_timesteps,
        "environment_id": "LunarLander-v3",
        "scenario": scenario.model_dump(),
        "reward_mode": "original",
        "deterministic": True,
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
        "episodes": [asdict(episode) for episode in episodes],
    }

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
    )

    EVALUATION_DIRECTORY.mkdir(parents=True, exist_ok=True)
    temporary_path = EVALUATION_DIRECTORY / f"{evaluation_id}.tmp"
    destination = EVALUATION_DIRECTORY / f"{evaluation_id}.json"

    temporary_path.write_text(serialized, encoding="utf-8")
    temporary_path.replace(destination)

    return destination


def get_evaluation_path(evaluation_id: UUID) -> Path:
    path = EVALUATION_DIRECTORY / f"{evaluation_id.hex}.json"

    if not path.is_file():
        raise FileNotFoundError("La evaluación solicitada no existe.")

    return path


@dataclass(frozen=True)
class EvaluationSummary:
    id: str
    model_id: str
    created_at: str
    training_timesteps: int
    episode_count: int


def list_evaluations(*, model_id: str) -> list[EvaluationSummary]:
    evaluations: list[EvaluationSummary] = []

    for path in EVALUATION_DIRECTORY.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))

        if payload["model_id"] != model_id:
            continue

        evaluations.append(
            EvaluationSummary(
                id=payload["id"],
                model_id=payload["model_id"],
                created_at=payload["created_at"],
                training_timesteps=payload["training_timesteps"],
                episode_count=len(payload["episodes"]),
            )
        )

    return sorted(
        evaluations,
        key=lambda evaluation: evaluation.created_at,
        reverse=True,
    )
