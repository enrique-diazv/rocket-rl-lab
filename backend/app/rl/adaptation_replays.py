from uuid import UUID

from stable_baselines3 import PPO

from app.rl.recording import record_episode
from app.rl.scenario_config import ScenarioConfig
from app.rl.trajectory import EpisodeTrajectory
from app.storage.adaptations import adaptation_checkpoint_path


def record_adaptation_replays(
    *,
    experiment_id: UUID,
    agent: str,
    scenario: ScenarioConfig,
    extra_training_timesteps: int,
    seed: int,
) -> tuple[EpisodeTrajectory, EpisodeTrajectory]:
    initial_checkpoint = adaptation_checkpoint_path(experiment_id, agent, 0)
    final_checkpoint = adaptation_checkpoint_path(
        experiment_id, agent, extra_training_timesteps
    )

    initial_model = PPO.load(initial_checkpoint, device="cpu")
    before = record_episode(initial_model, seed=seed, scenario=scenario)

    if final_checkpoint == initial_checkpoint:
        return before, before

    final_model = PPO.load(final_checkpoint, device="cpu")
    after = record_episode(final_model, seed=seed, scenario=scenario)
    return before, after