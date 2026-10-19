from math import isfinite
from typing import Any

import gymnasium as gym
import numpy as np


class RewardShapingWrapper(gym.Wrapper):
    def __init__(
        self,
        env: gym.Env,
        *,
        time_penalty: float = 0.0,
    ) -> None:
        if not isfinite(time_penalty) or time_penalty < 0:
            raise ValueError(
                "La penalización debe ser un número finito mayor o igual a cero."
            )

        super().__init__(env)
        self.time_penalty = float(time_penalty)

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        observation, reward, terminated, truncated, info = self.env.step(action)

        base_reward = float(reward)
        shaping_reward = -self.time_penalty
        total_reward = base_reward + shaping_reward

        info = {
            **info,
            "reward_components": {
                "base": base_reward,
                "shaping": shaping_reward,
                "total": total_reward,
            },
        }

        return observation, total_reward, terminated, truncated, info