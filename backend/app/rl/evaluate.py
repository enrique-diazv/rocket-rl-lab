from pathlib import Path
from statistics import mean, stdev

from stable_baselines3 import PPO

from app.rl.env_factory import create_lander_env
from app.rl.landing_metrics import is_successful_landing
from app.rl.evaluation_metrics import EpisodeEvaluation
from app.storage.evaluations import save_evaluation
from argparse import ArgumentParser

EVALUATION_SEEDS = tuple(range(1_000, 1_010))


def main() -> None:
    parser = ArgumentParser(description="Evalúa un checkpoint PPO.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/neutral_initial.zip"),
    )
    args = parser.parse_args()

    backend_directory = Path(__file__).resolve().parents[2]
    checkpoint_path = backend_directory / args.checkpoint
    print(f"Checkpoint seleccionado: {checkpoint_path}")

    model = PPO.load(checkpoint_path, device="cpu")
    env = create_lander_env()
    episode_rewards: list[float] = []
    episode_results: list[EpisodeEvaluation] = []

    successful_episodes = 0
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
                observation, reward, terminated, truncated, _ = env.step(action.item())
                total_reward += float(reward)
                steps += 1

            success = is_successful_landing(
                env,
                terminated=terminated,
                truncated=truncated,
            )
            successful_episodes += int(success)
            episode_rewards.append(total_reward)

            episode_results.append(
                EpisodeEvaluation(
                    seed=seed,
                    steps=steps,
                    total_reward=total_reward,
                    success=success,
                    terminated=terminated,
                    truncated=truncated,
                )
            )

            print(
                f"Seed {seed}: recompensa={total_reward:.2f}, "
                f"pasos={steps}, success={success}, "
                f"truncated={truncated}"
            )
    finally:
        env.close()

    print(f"Episodios evaluados: {len(episode_rewards)}")
    print(f"Recompensa original media: {mean(episode_rewards):.2f}")
    print(f"Desviacion estandar: {stdev(episode_rewards):.2f}")
    print(f"Aterrizajes exitosos: " f"{successful_episodes}/{len(episode_rewards)}")
    print(f"Tasa de exito: " f"{successful_episodes / len(episode_rewards):.1%}")

    evaluation_path = save_evaluation(
        episode_results,
        checkpoint_path=checkpoint_path,
        training_timesteps=int(model.num_timesteps),
    )
    print(f"Evaluacion guardada en: {evaluation_path}")


if __name__ == "__main__":
    main()
