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
        self._base_return = 0.0
        self._shaping_return = 0.0
        self._total_return = 0.0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        observation, info = self.env.reset(seed=seed, options=options)

        self._base_return = 0.0
        self._shaping_return = 0.0
        self._total_return = 0.0

        return observation, info

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        observation, reward, terminated, truncated, info = self.env.step(action)

        base_reward = float(reward)
        shaping_reward = -self.time_penalty
        total_reward = base_reward + shaping_reward

        self._base_return += base_reward
        self._shaping_return += shaping_reward
        self._total_return += total_reward

        info = {
            **info,
            "reward_components": {
                "base": base_reward,
                "shaping": shaping_reward,
                "total": total_reward,
            },
        }

        if terminated or truncated:
            info.update(
                {
                    "base_return": self._base_return,
                    "shaping_return": self._shaping_return,
                    "total_return": self._total_return,
                }
            )

        return observation, total_reward, terminated, truncated, info