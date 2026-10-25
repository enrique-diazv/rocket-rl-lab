from pathlib import Path
from statistics import mean, stdev

from stable_baselines3 import PPO

from app.rl.policy_evaluation import evaluate_episode
from app.rl.evaluation_metrics import EpisodeEvaluation
from app.rl.scenario_config import ScenarioConfig
from app.storage.evaluations import save_evaluation
from argparse import ArgumentParser

from pydantic import ValidationError

from app.rl.scenario_env import create_scenario_env

EVALUATION_SEEDS = tuple(range(1_000, 1_010))


def main() -> None:
    defaults = ScenarioConfig()
    parser = ArgumentParser(description="Evalúa un checkpoint PPO.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/neutral_initial.zip"),
    )
    parser.add_argument(
        "--gravity",
        type=float,
        default=defaults.gravity,
    )
    parser.add_argument(
        "--max-episode-steps",
        type=int,
        default=defaults.max_episode_steps,
    )

    parser.add_argument(
        "--fuel-budget",
        type=float,
        default=defaults.fuel_budget,
    )

    parser.add_argument(
        "--platform-width-scale",
        type=float,
        default=defaults.platform_width_scale,
    )

    args = parser.parse_args()

    try:
        scenario = ScenarioConfig(
            gravity=args.gravity,
            max_episode_steps=args.max_episode_steps,
            fuel_budget=args.fuel_budget,
            platform_width_scale=args.platform_width_scale,
        )
    except ValidationError as error:
        parser.error(str(error))

    backend_directory = Path(__file__).resolve().parents[2]
    checkpoint_path = backend_directory / args.checkpoint
    print(f"Checkpoint seleccionado: {checkpoint_path}")
    print(f"Gravedad: {scenario.gravity}")
    print(f"Limite del episodio: {scenario.max_episode_steps} pasos")

    print(
        "Combustible: ilimitado"
        if scenario.fuel_budget is None
        else f"Combustible: {scenario.fuel_budget} unidades relativas"
    )

    print(f"Escala de plataforma: {scenario.platform_width_scale}")
    model = PPO.load(checkpoint_path, device="cpu")
    env = create_scenario_env(scenario)
    episode_rewards: list[float] = []
    episode_results: list[EpisodeEvaluation] = []

    successful_episodes = 0
    try:
        for seed in EVALUATION_SEEDS:
            episode = evaluate_episode(model, env, seed=seed)
            successful_episodes += int(episode.success)
            episode_rewards.append(episode.total_reward)
            episode_results.append(episode)

            print(
                f"Seed {episode.seed}: recompensa={episode.total_reward:.2f}, "
                f"pasos={episode.steps}, success={episode.success}, "
                f"truncated={episode.truncated}"
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
        scenario=scenario,
    )
    print(f"Evaluacion guardada en: {evaluation_path}")


if __name__ == "__main__":
    main()
