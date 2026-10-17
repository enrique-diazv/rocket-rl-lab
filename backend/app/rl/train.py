from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from app.rl.env_factory import create_lander_env

SEED = 42
TOTAL_TIMESTEPS = 1_024_000


def main() -> None:
    backend_directory = Path(__file__).resolve().parents[2]
    checkpoint_path = (
        backend_directory / "checkpoints" / "neutral_baseline.zip"
    )
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    env = Monitor(create_lander_env())

    try:
        model = PPO(
            "MlpPolicy",
            env,
            policy_kwargs={"net_arch": [64, 64]},
            n_steps=2_048,
            batch_size=64,
            seed=SEED,
            device="cpu",
            verbose=1,
        )
        model.learn(total_timesteps=TOTAL_TIMESTEPS)
        model.save(checkpoint_path)

        print(f"Pasos entrenados: {model.num_timesteps}")
        print(f"Modelo guardado en: {checkpoint_path}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
