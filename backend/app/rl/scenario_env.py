from typing import Literal

import gymnasium as gym

from app.rl.fuel_wrapper import FiniteFuelWrapper
from app.rl.platform_wrapper import VariablePlatformWrapper
from app.rl.scenario_config import ScenarioConfig


def create_scenario_env(
    config: ScenarioConfig,
    render_mode: Literal["human", "rgb_array"] | None = None,
) -> gym.Env:
    env = gym.make(
        "LunarLander-v3",
        render_mode=render_mode,
        gravity=config.gravity,
        max_episode_steps=config.max_episode_steps,
    )

    if config.platform_width_scale != 1.0:
        env = VariablePlatformWrapper(
            env,
            width_scale=config.platform_width_scale,
        )

    if config.fuel_budget is not None:
        env = FiniteFuelWrapper(
            env,
            fuel_budget=config.fuel_budget,
        )

    return env