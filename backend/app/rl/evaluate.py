from pathlib import Path
from statistics import mean, stdev

from stable_baselines3 import PPO

from app.rl.contact_metrics import FirstContactTracker
from app.rl.env_factory import create_lander_env
from app.rl.landing_metrics import is_successful_landing
from app.rl.evaluation_metrics import EpisodeEvaluation
from app.rl.rewards import ENGINE_COST_BY_ACTION
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
            contact_tracker = FirstContactTracker(env.unwrapped)
            total_reward = 0.0
            steps = 0
            engine_usage_cost = 0.0
            terminated = False
            truncated = False

            while not (terminated or truncated):
                action, _ = model.predict(
                    observation,
                    deterministic=True,
                )
                action_id = int(action.item())
                observation, reward, terminated, truncated, _ = env.step(action_id)
                contact_tracker.observe()
                total_reward += float(reward)
                engine_usage_cost += ENGINE_COST_BY_ACTION[action_id]
                steps += 1

            success = is_successful_landing(
                env,
                terminated=terminated,
                truncated=truncated,
            )
            lander_env = env.unwrapped
            pad_center = (lander_env.helipad_x1 + lander_env.helipad_x2) / 2.0
            final_horizontal_error = abs(
                float(lander_env.lander.position.x) - pad_center
            )
            successful_episodes += int(success)
            episode_rewards.append(total_reward)
            contact_motion = contact_tracker.pre_contact_motion
            episode_results.append(
                EpisodeEvaluation(
                    seed=seed,
                    steps=steps,
                    total_reward=total_reward,
                    success=success,
                    terminated=terminated,
                    truncated=truncated,
                    final_horizontal_error=final_horizontal_error,
                    engine_usage_cost=engine_usage_cost,
                    pre_contact_speed=(
                        contact_motion.speed
                        if contact_motion is not None
                        else None
                    ),
                    pre_contact_abs_angle=(
                        contact_motion.abs_angle
                        if contact_motion is not None
                        else None
                    ),
                    pre_contact_angular_speed=(
                        contact_motion.angular_speed
                        if contact_motion is not None
                        else None
                    ),
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
