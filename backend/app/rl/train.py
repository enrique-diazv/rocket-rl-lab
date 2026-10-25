from argparse import ArgumentParser
from pathlib import Path
from dataclasses import asdict
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from app.rl.env_factory import create_lander_env
from app.rl.agent_profiles import AGENT_PROFILES, RewardWeights
from app.rl.engine_config import ENGINE_COST_BY_ACTION
from app.rl.rewards import (
    HOVER_MAX_ANGLE,
    HOVER_MAX_SPEED,
    RewardShapingWrapper,
)

from stable_baselines3.common.logger import Logger, configure
from app.storage.training import create_training_run

SEED = 42
TOTAL_TIMESTEPS = 1_024_000
ROLLOUT_STEPS = 2_048


def main() -> None:
    parser = ArgumentParser(
        description="Entrena un PPO nuevo con reward shaping configurable."
    )
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--timesteps", type=int, default=TOTAL_TIMESTEPS)
    parser.add_argument("--time-penalty", type=float, default=None)
    parser.add_argument("--hover-bonus", type=float, default=None)
    parser.add_argument("--progress-weight", type=float, default=None)
    parser.add_argument("--horizontal-progress-weight", type=float, default=None)
    parser.add_argument("--fuel-penalty", type=float, default=None)
    parser.add_argument("--stability-penalty", type=float, default=None)
    parser.add_argument(
        "--agent",
        choices=sorted(AGENT_PROFILES),
        help="Perfil inicial de recompensas de una especialidad.",
    )
    args = parser.parse_args()

    profile_weights = (
        AGENT_PROFILES[args.agent] if args.agent is not None else RewardWeights()
    )
    for weight_name, default_weight in asdict(profile_weights).items():
        if getattr(args, weight_name) is None:
            setattr(args, weight_name, default_weight)

    if args.timesteps <= 0 or args.timesteps % ROLLOUT_STEPS != 0:
        parser.error(f"--timesteps debe ser positivo y múltiplo de {ROLLOUT_STEPS}.")

    backend_directory = Path(__file__).resolve().parents[2]
    checkpoint_path = (backend_directory / args.checkpoint).resolve()

    if checkpoint_path.suffix != ".zip":
        parser.error("--checkpoint debe terminar en .zip.")

    if checkpoint_path.exists():
        parser.error(f"El checkpoint ya existe: {checkpoint_path}")

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    env = create_lander_env()
    training_logger: Logger | None = None

    try:
        env = RewardShapingWrapper(
            env,
            time_penalty=args.time_penalty,
            hover_bonus=args.hover_bonus,
            progress_weight=args.progress_weight,
            horizontal_progress_weight=args.horizontal_progress_weight,
            fuel_penalty=args.fuel_penalty,
            stability_penalty=args.stability_penalty,
        )

        ppo_config = {
            "policy": "MlpPolicy",
            "policy_kwargs": {"net_arch": [64, 64]},
            "n_steps": ROLLOUT_STEPS,
            "batch_size": 64,
            "seed": SEED,
            "device": "cpu",
            "verbose": 1,
        }

        run_directory = create_training_run(
            {
                "environment_id": "LunarLander-v3",
                "agent_profile": args.agent,
                "checkpoint_path": str(checkpoint_path),
                "requested_timesteps": args.timesteps,
                "reward": {
                    "mode": (
                        "shaped"
                        if (
                            args.time_penalty > 0
                            or args.hover_bonus > 0
                            or args.progress_weight > 0
                            or args.horizontal_progress_weight > 0
                            or args.fuel_penalty > 0
                            or args.stability_penalty > 0
                        )
                        else "baseline"
                    ),
                    "time_penalty": args.time_penalty,
                    "hover_bonus": args.hover_bonus,
                    "hover_max_angle_radians": HOVER_MAX_ANGLE,
                    "hover_max_normalized_speed": HOVER_MAX_SPEED,
                    "progress_weight": args.progress_weight,
                    "progress_distance": "normalized_xy_euclidean",
                    "progress_formula": "previous_distance - current_distance",
                    "horizontal_progress_weight": args.horizontal_progress_weight,
                    "horizontal_progress_formula": ("abs(previous_x) - abs(current_x)"),
                    "fuel_penalty": args.fuel_penalty,
                    "engine_cost_by_action": ENGINE_COST_BY_ACTION,
                    "stability_penalty": args.stability_penalty,
                    "stability_formula": (
                        "sum(float(value) ** 2 for value in observation[2:6])"
                    ),
                },
                "ppo": ppo_config,
            }
        )

        env = Monitor(
            env,
            filename=str(run_directory / "episodes.monitor.csv"),
            info_keywords=(
                "base_return",
                "shaping_return",
                "total_return",
            ),
        )

        print(f"Penalizacion por paso: {args.time_penalty}")
        print(f"Premio por paso estable: {args.hover_bonus}")
        print(f"Peso del progreso: {args.progress_weight}")
        print("Peso del progreso horizontal: " f"{args.horizontal_progress_weight}")
        print(f"Penalizacion adicional por combustible: {args.fuel_penalty}")
        print(f"Penalizacion por inestabilidad: {args.stability_penalty}")
        print(f"Checkpoint de salida: {checkpoint_path}")

        model = PPO(env=env, **ppo_config)
        training_logger = configure(
            str(run_directory),
            ["stdout", "csv"],
        )
        model.set_logger(training_logger)

        model.learn(total_timesteps=args.timesteps)
        model.save(checkpoint_path)

        print(f"Pasos entrenados: {model.num_timesteps}")
        print(f"Modelo guardado en: {checkpoint_path}")
        print(f"Experimento registrado en: {run_directory}")
    finally:
        env.close()

        if training_logger is not None:
            training_logger.close()


if __name__ == "__main__":
    main()
