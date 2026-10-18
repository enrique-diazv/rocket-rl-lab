from dataclasses import asdict
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
from uuid import UUID, uuid4

from app.rl.trajectory import EpisodeTrajectory

EPISODE_DIRECTORY = Path(__file__).resolve().parents[2] / "experiments" / "episodes"


def save_episode(
    episode: EpisodeTrajectory,
    *,
    checkpoint_path: Path,
) -> str:
    episode_id = uuid4().hex

    payload = {
        "schema_version": 1,
        "id": episode_id,
        "model_id": checkpoint_path.stem,
        "checkpoint_sha256": sha256(checkpoint_path.read_bytes()).hexdigest(),
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
        "episode": asdict(episode),
    }

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
    )

    EPISODE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    temporary_path = EPISODE_DIRECTORY / f"{episode_id}.tmp"
    destination = EPISODE_DIRECTORY / f"{episode_id}.json"

    temporary_path.write_text(serialized, encoding="utf-8")
    temporary_path.replace(destination)

    return episode_id


def get_episode_path(episode_id: UUID) -> Path:
    path = EPISODE_DIRECTORY / f"{episode_id.hex}.json"

    if not path.is_file():
        raise FileNotFoundError("El episodio solicitado no existe.")

    return path
