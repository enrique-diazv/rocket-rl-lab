from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict

from stable_baselines3 import PPO

from app.rl.adaptation_callbacks import TrainingEpisodeCounter
from app.rl.adaptation_config import AdaptationConfig
from app.rl.agent_profiles import AGENT_PROFILES
from app.rl.rewards import RewardShapingWrapper
from app.rl.scenario_env import create_scenario_env
from app.storage.checkpoints import CHECKPOINT_DIRECTORY


def validate_adaptation_budget(
    model: PPO,
    config: AdaptationConfig,
) -> None:
    rollout_timesteps = model.n_steps * model.n_envs

    for field_name, timesteps in (
        ("block_timesteps", config.block_timesteps),
        ("max_additional_timesteps", config.max_additional_timesteps),
    ):
        if timesteps % rollout_timesteps != 0:
            raise ValueError(
                f"{field_name} debe ser múltiplo de {rollout_timesteps}."
            )


@contextmanager
def adaptation_model(
    agent: str,
    config: AdaptationConfig,
) -> Iterator[PPO]:
    if agent not in AGENT_PROFILES:
        raise ValueError(f"Agente desconocido: {agent}")

    env = create_scenario_env(config.scenario)

    try:
        env = RewardShapingWrapper(
            env,
            **asdict(AGENT_PROFILES[agent]),
        )
        model = PPO.load(
            CHECKPOINT_DIRECTORY / f"{agent}.zip",
            env=env,
            device="cpu",
        )
        validate_adaptation_budget(model, config)
        yield model
    finally:
        env.close()

def train_adaptation_block(
    model: PPO,
    config: AdaptationConfig,
    episode_counter: TrainingEpisodeCounter,
    *,
    initial_timesteps: int,
) -> int:
    completed = int(model.num_timesteps) - initial_timesteps
    remaining = config.max_additional_timesteps - completed

    if remaining <= 0:
        return 0

    requested_steps = min(config.block_timesteps, remaining)
    previous_timesteps = int(model.num_timesteps)

    model.learn(
        total_timesteps=requested_steps,
        callback=episode_counter,
        reset_num_timesteps=False,
    )

    trained_steps = int(model.num_timesteps) - previous_timesteps

    if trained_steps != requested_steps:
        raise RuntimeError(
            f"PPO ejecutó {trained_steps} pasos; "
            f"se solicitaron {requested_steps}."
        )

    return trained_steps