from argparse import ArgumentParser
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from app.storage.adaptation_events import list_adaptation_events
from app.storage.adaptation_queries import get_adaptation_experiment
from app.storage.adaptations import adaptation_replays_path


def export_demo(experiment_id: UUID) -> Path:
    experiment = get_adaptation_experiment(experiment_id)
    if any(job.finished_at is None for job in experiment.jobs):
        raise ValueError("El experimento todavía tiene trabajos activos.")

    evaluations = []
    cursor = 0
    while cursor < experiment.last_event_id:
        batch = list_adaptation_events(experiment.id, cursor)
        if not batch:
            raise ValueError("El historial del experimento está incompleto.")

        evaluations.extend(
            event.model_dump(mode="json")
            for event in batch
            if event.id <= experiment.last_event_id
            and event.event_type == "evaluation_completed"
        )
        cursor = batch[-1].id

    files = {
        "experiment.json": {
            "schema_version": 1,
            "experiment": experiment.model_dump(mode="json"),
            "evaluations": evaluations,
        }
    }

    for job in experiment.jobs:
        path = adaptation_replays_path(experiment.id, job.agent)
        pair = json.loads(path.read_text(encoding="utf-8"))
        if (
            not isinstance(pair, dict)
            or pair.get("experiment_id") != experiment.id.hex
            or pair.get("agent") != job.agent
        ):
            raise ValueError(f"El replay de {job.agent} no corresponde al experimento.")

        files[f"{job.agent}.json"] = pair

    public = Path(__file__).resolve().parents[2] / "frontend" / "public"
    destination = public / "demo"
    if destination.exists():
        raise FileExistsError("Ya existe una exportación en frontend/public/demo.")

    with TemporaryDirectory(dir=public, prefix=".demo-") as temporary:
        staging = Path(temporary) / "demo"
        staging.mkdir()
        for name, payload in files.items():
            (staging / name).write_text(
                json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")),
                encoding="utf-8",
            )
        staging.rename(destination)

    print(f"Evaluaciones exportadas: {len(evaluations)}")
    print(f"Pares de replays exportados: {len(experiment.jobs)}")
    return destination


def main() -> None:
    parser = ArgumentParser(description="Exporta un experimento para la demo estática.")
    parser.add_argument("--experiment", type=UUID, required=True)
    args = parser.parse_args()

    try:
        destination = export_demo(args.experiment)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Demo guardada en: {destination}")


if __name__ == "__main__":
    main()