from argparse import ArgumentParser
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from app.rl.adaptation_config import AdaptationConfig
from app.rl.adaptation_metrics import AdaptationProgress
from app.rl.adaptation_runner import AdaptationSession
from app.rl.agent_profiles import AGENT_PROFILES
from app.storage.adaptations import adaptation_checkpoint_path


def _print_progress(progress: AdaptationProgress) -> None:
    print(
        f"[{progress.agent}] {progress.phase}; "
        f"pasos extra={progress.extra_training_timesteps}; "
        f"episodios={progress.training_episodes}; "
        f"evaluaciones={progress.evaluation_count}; "
        f"tiempo={progress.elapsed_wall_seconds:.1f}s",
        flush=True,
    )

    if progress.evaluation is not None:
        print(
            f"Exito={progress.evaluation.success_rate:.1%}; "
            f"recompensa original media="
            f"{progress.evaluation.mean_original_reward:.2f}",
            flush=True,
        )


def main() -> None:
    parser = ArgumentParser(
        description="Adapta una especialidad PPO a un escenario."
    )
    parser.add_argument(
        "--agent",
        choices=sorted(AGENT_PROFILES),
        required=True,
    )
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    backend_directory = Path(__file__).resolve().parents[2]
    config_path = backend_directory / args.config

    try:
        config = AdaptationConfig.model_validate_json(
            config_path.read_text(encoding="utf-8-sig")
        )
    except (OSError, UnicodeDecodeError, ValidationError) as error:
        parser.error(f"No se pudo cargar la configuracion: {error}")

    experiment_id = uuid4()
    print(f"Experimento: {experiment_id.hex}", flush=True)
    print(
        f"Presupuesto de pasos adicionales: "
        f"{config.max_additional_timesteps}",
        flush=True,
    )

    result = AdaptationSession(
        args.agent,
        config,
        experiment_id,
        on_progress=_print_progress,
    ).run()

    directory = adaptation_checkpoint_path(
        experiment_id,
        args.agent,
        0,
    ).parent

    print(f"Estado final: {result.status}")
    print(
        "Pasos hasta el criterio: "
        f"{result.time_to_threshold_steps if result.time_to_threshold_steps is not None else 'no alcanzado'}"
    )
    print(f"Archivos guardados en: {directory}")


if __name__ == "__main__":
    main()