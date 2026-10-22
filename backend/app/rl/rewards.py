from math import isfinite
from typing import Any

import gymnasium as gym
import numpy as np


HOVER_MAX_ANGLE = 0.1
HOVER_MAX_SPEED = 0.2


class RewardShapingWrapper(gym.Wrapper):
    def __init__(
        self,
        env: gym.Env,
        *,
        time_penalty: float = 0.0,
        hover_bonus: float = 0.0,
    ) -> None:
        if not isfinite(time_penalty) or time_penalty < 0:
            raise ValueError(
                "La penalización debe ser un número finito mayor o igual a cero."
            )

        if not isfinite(hover_bonus) or hover_bonus < 0:
            raise ValueError(
                "El premio debe ser un número finito mayor o igual a cero."
            )

        super().__init__(env)
        self.time_penalty = float(time_penalty)
        self.hover_bonus = float(hover_bonus)
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
        speed = float(np.hypot(observation[2], observation[3]))
        stable = (
            abs(float(observation[4])) <= HOVER_MAX_ANGLE
            and speed <= HOVER_MAX_SPEED
        )
        hover_reward = self.hover_bonus if stable else 0.0

        shaping_reward = -self.time_penalty + hover_reward
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