from dataclasses import dataclass
from math import hypot

import gymnasium as gym
from gymnasium.envs.box2d.lunar_lander import LunarLander

from app.rl.landing_metrics import leg_ground_contacts


@dataclass(frozen=True)
class MotionSnapshot:
    speed: float
    abs_angle: float
    angular_speed: float


def lander_motion(lander_env: LunarLander) -> MotionSnapshot:
    lander = lander_env.lander

    if lander is None:
        raise gym.error.ResetNeeded(
            "Ejecuta reset() antes de medir el movimiento."
        )

    velocity = lander.linearVelocity
    return MotionSnapshot(
        speed=hypot(float(velocity.x), float(velocity.y)),
        abs_angle=abs(float(lander.angle)),
        angular_speed=abs(float(lander.angularVelocity)),
    )


class FirstContactTracker:
    def __init__(self, lander_env: LunarLander) -> None:
        self._lander_env = lander_env
        self._previous_motion = lander_motion(lander_env)
        self.pre_contact_motion: MotionSnapshot | None = None

    def observe(self) -> None:
        if self.pre_contact_motion is not None:
            return

        if any(leg_ground_contacts(self._lander_env)):
            self.pre_contact_motion = self._previous_motion
            return

        self._previous_motion = lander_motion(self._lander_env)