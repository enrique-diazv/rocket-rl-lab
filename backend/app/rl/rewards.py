from math import isfinite
from typing import Any

import gymnasium as gym
import numpy as np

HOVER_MAX_ANGLE = 0.1
HOVER_MAX_SPEED = 0.2
ENGINE_COST_BY_ACTION = (0.0, 0.03, 0.30, 0.03)


class RewardShapingWrapper(gym.Wrapper):
    def __init__(
        self,
        env: gym.Env,
        *,
        time_penalty: float = 0.0,
        hover_bonus: float = 0.0,
        progress_weight: float = 0.0,
        horizontal_progress_weight: float = 0.0,
        fuel_penalty: float = 0.0,
        stability_penalty: float = 0.0,
    ) -> None:
        if not isfinite(time_penalty) or time_penalty < 0:
            raise ValueError(
                "La penalización debe ser un número finito mayor o igual a cero."
            )

        if not isfinite(hover_bonus) or hover_bonus < 0:
            raise ValueError(
                "El premio debe ser un número finito mayor o igual a cero."
            )

        if not isfinite(progress_weight) or progress_weight < 0:
            raise ValueError(
                "El peso de progreso debe ser finito y mayor o igual a cero."
            )

        if not isfinite(horizontal_progress_weight) or horizontal_progress_weight < 0:
            raise ValueError(
                "El peso de progreso horizontal debe ser finito "
                "y mayor o igual a cero."
            )

        if not isfinite(fuel_penalty) or fuel_penalty < 0:
            raise ValueError(
                "La penalización por combustible debe ser finita "
                "y mayor o igual a cero."
            )
        if not isfinite(stability_penalty) or stability_penalty < 0:
            raise ValueError(
                "La penalización por inestabilidad debe ser finita "
                "y mayor o igual a cero."
            )
        super().__init__(env)
        self.time_penalty = float(time_penalty)
        self.hover_bonus = float(hover_bonus)
        self.progress_weight = float(progress_weight)
        self.horizontal_progress_weight = float(horizontal_progress_weight)
        self.fuel_penalty = float(fuel_penalty)
        self.stability_penalty = float(stability_penalty)
        self._previous_horizontal_error = 0.0
        self._previous_distance: float | None = None
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
        self._previous_horizontal_error = abs(float(observation[0]))
        self._previous_distance = float(np.hypot(observation[0], observation[1]))
        self._base_return = 0.0
        self._shaping_return = 0.0
        self._total_return = 0.0

        return observation, info

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if self._previous_distance is None:
            raise gym.error.ResetNeeded("Ejecuta reset() antes de step().")

        observation, reward, terminated, truncated, info = self.env.step(action)

        base_reward = float(reward)
        speed = float(np.hypot(observation[2], observation[3]))
        stable = (
            abs(float(observation[4])) <= HOVER_MAX_ANGLE and speed <= HOVER_MAX_SPEED
        )
        hover_reward = self.hover_bonus if stable else 0.0

        distance = float(np.hypot(observation[0], observation[1]))
        progress_reward = self.progress_weight * (self._previous_distance - distance)
        self._previous_distance = distance

        horizontal_error = abs(float(observation[0]))
        horizontal_progress_reward = self.horizontal_progress_weight * (
            self._previous_horizontal_error - horizontal_error
        )
        self._previous_horizontal_error = horizontal_error

        fuel_reward = -self.fuel_penalty * ENGINE_COST_BY_ACTION[action]

        stability_error = sum(
            float(value) ** 2 for value in observation[2:6]
        )
        stability_reward = -self.stability_penalty * stability_error

        shaping_reward = (
            -self.time_penalty
            + hover_reward
            + progress_reward
            + horizontal_progress_reward
            + fuel_reward
            + stability_reward
        )
        total_reward = base_reward + shaping_reward

        self._base_return += base_reward
        self._shaping_return += shaping_reward
        self._total_return += total_reward

        info = {
            **info,
            "reward_components": {
                "base": base_reward,
                "time": -self.time_penalty,
                "hover": hover_reward,
                "progress": progress_reward,
                "horizontal_progress": horizontal_progress_reward,
                "fuel": fuel_reward,
                "stability": stability_reward,
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
