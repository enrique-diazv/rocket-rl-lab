from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
from platform import python_version
from uuid import uuid4

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