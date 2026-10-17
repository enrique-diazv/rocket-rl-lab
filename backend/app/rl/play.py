from pathlib import Path

from stable_baselines3 import PPO

from app.rl.env_factory import create_lander_env

from argparse import ArgumentParser

PLAYBACK_SEEDS = (1_000, 1_001, 1_002)


def main() -> None:
    parser = ArgumentParser(description="Visualiza un checkpoint PPO.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/neutral_initial.zip"),
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=PLAYBACK_SEEDS,
    )
    args = parser.parse_args()

    backend_directory = Path(__file__).resolve().parents[2]
    checkpoint_path = backend_directory / args.checkpoint

    model = PPO.load(checkpoint_path, device="cpu")
    env = create_lander_env(render_mode="human")

    try:
        for seed in args.seeds:
            observation, _ = env.reset(seed=seed)
            total_reward = 0.0
            terminated = False
            truncated = False

            while not (terminated or truncated):
                action, _ = model.predict(
                    observation,
                    deterministic=True,
                )
                observation, reward, terminated, truncated, _ = env.step(action.item())
                total_reward += float(reward)

            print(f"Seed {seed}: recompensa={total_reward:.2f}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
