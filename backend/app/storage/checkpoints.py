from dataclasses import dataclass
from pathlib import Path


CHECKPOINT_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "checkpoints"
)


@dataclass(frozen=True)
class CheckpointSummary:
    id: str
    filename: str


def list_checkpoints() -> list[CheckpointSummary]:
    return [
        CheckpointSummary(
            id=path.stem,
            filename=path.name,
        )
        for path in sorted(CHECKPOINT_DIRECTORY.glob("*.zip"))
        if path.is_file()
    ]