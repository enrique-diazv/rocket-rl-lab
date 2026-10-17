from typing import Literal

import gymnasium as gym


def create_lander_env(
    render_mode: Literal["human", "rgb_array"] | None = None,
) -> gym.Env:
    return gym.make("LunarLander-v3", render_mode=render_mode)
