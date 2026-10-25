from typing import Any

import gymnasium as gym
import numpy as np

from app.rl.platform_geometry import resize_platform


class VariablePlatformWrapper(gym.Wrapper):
    def __init__(self, env: gym.Env, *, width_scale: float) -> None:
        super().__init__(env)
        self._width_scale = width_scale

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        observation, info = self.env.reset(seed=seed, options=options)
        resize_platform(self.env.unwrapped, self._width_scale)

        if self.render_mode == "human":
            self.env.render()

        return observation, info