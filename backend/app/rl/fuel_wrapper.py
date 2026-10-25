from decimal import Decimal
from typing import Any

import gymnasium as gym
import numpy as np

from app.rl.engine_config import ENGINE_COST_BY_ACTION


_FUEL_COST_BY_ACTION = tuple(
    Decimal(str(cost)) for cost in ENGINE_COST_BY_ACTION
)


class FiniteFuelWrapper(gym.Wrapper):
    def __init__(self, env: gym.Env, *, fuel_budget: float) -> None:
        super().__init__(env)
        self._capacity = Decimal(str(fuel_budget))
        self._fuel_remaining: Decimal | None = None

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        observation, info = self.env.reset(seed=seed, options=options)
        self._fuel_remaining = self._capacity

        return observation, {
            **info,
            "fuel_remaining": float(self._fuel_remaining),
        }

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if self._fuel_remaining is None:
            raise gym.error.ResetNeeded("Ejecuta reset() antes de step().")

        if not self.action_space.contains(action):
            raise ValueError(f"Acción inválida: {action}")

        requested_action = int(action)
        requested_cost = _FUEL_COST_BY_ACTION[requested_action]
        executed_action = (
            requested_action
            if requested_cost <= self._fuel_remaining
            else 0
        )
        consumed = _FUEL_COST_BY_ACTION[executed_action]

        observation, reward, terminated, truncated, info = self.env.step(
            executed_action
        )
        self._fuel_remaining -= consumed

        return observation, float(reward), terminated, truncated, {
            **info,
            "requested_action": requested_action,
            "executed_action": executed_action,
            "fuel_consumed": float(consumed),
            "fuel_remaining": float(self._fuel_remaining),
        }