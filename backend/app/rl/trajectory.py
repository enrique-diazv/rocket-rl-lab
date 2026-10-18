from dataclasses import dataclass

import Box2D
import gymnasium as gym
from gymnasium.envs.box2d.lunar_lander import (
    FPS,
    SCALE,
    VIEWPORT_H,
    VIEWPORT_W,
    LunarLander,
)


@dataclass(frozen=True)
class FrameSnapshot:
    lander: list[tuple[float, float]]
    legs: list[list[tuple[float, float]]]


@dataclass(frozen=True)
class SceneSnapshot:
    width: float
    height: float
    fps: int
    terrain: list[list[tuple[float, float]]]
    helipad: list[tuple[float, float]]

@dataclass(frozen=True)
class EpisodeTrajectory:
    seed: int
    steps: int
    total_reward: float
    success: bool
    terminated: bool
    truncated: bool
    scene: SceneSnapshot
    frames: list[FrameSnapshot]

def _body_vertices(body: Box2D.b2Body) -> list[tuple[float, float]]:
    vertices = []

    for vertex in body.fixtures[0].shape.vertices:
        point = body.GetWorldPoint(vertex)
        vertices.append((float(point.x), float(point.y)))

    return vertices


def capture_frame(env: gym.Env) -> FrameSnapshot:
    physical_env = env.unwrapped

    if not isinstance(physical_env, LunarLander):
        raise TypeError("La captura requiere un entorno LunarLander.")

    if physical_env.lander is None:
        raise ValueError("Ejecuta reset antes de capturar un fotograma.")

    return FrameSnapshot(
        lander=_body_vertices(physical_env.lander),
        legs=[_body_vertices(leg) for leg in physical_env.legs],
    )


def capture_scene(env: gym.Env) -> SceneSnapshot:
    physical_env = env.unwrapped

    if not isinstance(physical_env, LunarLander):
        raise TypeError("La captura requiere un entorno LunarLander.")

    if physical_env.lander is None:
        raise ValueError("Ejecuta reset antes de capturar el escenario.")

    return SceneSnapshot(
        width=VIEWPORT_W / SCALE,
        height=VIEWPORT_H / SCALE,
        fps=FPS,
        terrain=[
            [(float(x), float(y)) for x, y in polygon[:2]]
            for polygon in physical_env.sky_polys
        ],
        helipad=[
            (
                float(physical_env.helipad_x1),
                float(physical_env.helipad_y),
            ),
            (
                float(physical_env.helipad_x2),
                float(physical_env.helipad_y),
            ),
        ],
    )
