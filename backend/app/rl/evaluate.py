from pathlib import Path
from statistics import mean, stdev

from stable_baselines3 import PPO

from app.rl.env_factory import create_lander_env


EVALUATION_SEEDS = tuple(range(1_000, 1_010))


def main() -> None:
    backend_directory = Path(__file__).resolve().parents[2]
    checkpoint_path = (
        backend_directory / "checkpoints" / "neutral_initial.zip"
    )

    model = PPO.load(checkpoint_path, device="cpu")
    env = create_lander_env()
    episode_rewards: list[float] = []

    try:
        for seed in EVALUATION_SEEDS:
            observation, _ = env.reset(seed=seed)
            total_reward = 0.0
            steps = 0
            terminated = False
            truncated = False

            while not (terminated or truncated):
                action, _ = model.predict(
                    observation,
                    deterministic=True,
                )
                observation, reward, terminated, truncated, _ = (
                    env.step(action.item())
                )
                total_reward += float(reward)
                steps += 1

            episode_rewards.append(total_reward)
            print(
                f"Seed {seed}: recompensa={total_reward:.2f}, "
                f"pasos={steps}, truncated={truncated}"
            )
    finally:
        env.close()

    print(f"Episodios evaluados: {len(episode_rewards)}")
    print(f"Recompensa original media: {mean(episode_rewards):.2f}")
    print(f"Desviacion estandar: {stdev(episode_rewards):.2f}")


if __name__ == "__main__":
    main()