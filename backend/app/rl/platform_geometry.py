from collections.abc import Iterable

import numpy as np
from gymnasium.envs.box2d.lunar_lander import (
    SCALE,
    VIEWPORT_W,
    LunarLander,
)


def _remap_vertices(
    vertices: Iterable[tuple[float, float]],
    original_x: tuple[float, ...],
    resized_x: tuple[float, ...],
) -> list[tuple[float, float]]:
    return [
        (float(np.interp(x, original_x, resized_x)), float(y))
        for x, y in vertices
    ]


def _resize_collision_edges(
    lander_env: LunarLander,
    original_x: tuple[float, ...],
    resized_x: tuple[float, ...],
) -> None:
    moon = lander_env.moon

    for fixture in list(moon.fixtures):
        vertices = _remap_vertices(
            fixture.shape.vertices,
            original_x,
            resized_x,
        )
        density = fixture.density
        friction = fixture.friction
        restitution = fixture.restitution

        moon.DestroyFixture(fixture)
        moon.CreateEdgeFixture(
            vertices=vertices,
            density=density,
            friction=friction,
            restitution=restitution,
        )


def resize_platform(
    lander_env: LunarLander,
    width_scale: float,
) -> None:
    world_width = VIEWPORT_W / SCALE
    original_x = (
        0.0,
        float(lander_env.helipad_x1),
        float(lander_env.helipad_x2),
        world_width,
    )
    center = (original_x[1] + original_x[2]) / 2.0
    half_width = (original_x[2] - original_x[1]) * width_scale / 2.0
    resized_x = (0.0, center - half_width, center + half_width, world_width)

    _resize_collision_edges(lander_env, original_x, resized_x)
    lander_env.sky_polys = [
        _remap_vertices(polygon, original_x, resized_x)
        for polygon in lander_env.sky_polys
    ]
    lander_env.helipad_x1, lander_env.helipad_x2 = resized_x[1:3]