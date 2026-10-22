from argparse import ArgumentParser
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from app.rl.env_factory import create_lander_env
from app.rl.rewards import RewardShapingWrapper

from stable_baselines3.common.logger import Logger, configure
from app.storage.training import create_training_run

SEED = 42
TOTAL_TIMESTEPS = 1_024_000
ROLLOUT_STEPS = 2_048


def main() -> None:
    parser = ArgumentParser(
        description="Entrena un PPO nuevo con penalización temporal."
    )
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--timesteps", type=int, default=TOTAL_TIMESTEPS)
    parser.add_argument("--time-penalty", type=float, default=0.0)
    args = parser.parse_args()

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
                "checkpoint_path": str(checkpoint_path),
                "requested_timesteps": args.timesteps,
                "reward": {
                    "mode": ("baseline" if args.time_penalty == 0 else "time_penalty"),
                    "time_penalty": args.time_penalty,
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
