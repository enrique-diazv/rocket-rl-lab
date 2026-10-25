from typing import Literal

import gymnasium as gym

from app.rl.scenario_config import ScenarioConfig


def create_scenario_env(
    config: ScenarioConfig,
    render_mode: Literal["human", "rgb_array"] | None = None,
) -> gym.Env:
    return gym.make(
        "LunarLander-v3",
        render_mode=render_mode,
        gravity=config.gravity,
        max_episode_steps=config.max_episode_steps,
    )