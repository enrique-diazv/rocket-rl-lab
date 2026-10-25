import numpy as np
import pytest

from app.rl.env_factory import create_lander_env
from app.rl.scenario_config import ScenarioConfig
from app.rl.scenario_env import create_scenario_env
from app.rl.trajectory import capture_scene


@pytest.mark.parametrize(
    ("width_scale", "expected_bounds"),
    [
        (0.5, (9.0, 11.0)),
        (1.0, (8.0, 12.0)),
        (2.0, (6.0, 14.0)),
    ],
)
def test_platform_width_changes_collisions_and_survives_reset(
    width_scale: float,
    expected_bounds: tuple[float, float],
) -> None:
    reference_env = create_lander_env()
    scenario_env = create_scenario_env(
        ScenarioConfig(platform_width_scale=width_scale)
    )

    try:
        for seed in (42, 43):
            reference_obs, _ = reference_env.reset(seed=seed)
            observation, _ = scenario_env.reset(seed=seed)

            np.testing.assert_array_equal(observation, reference_obs)

            physical_env = scenario_env.unwrapped
            assert (
                physical_env.helipad_x1,
                physical_env.helipad_x2,
            ) == pytest.approx(expected_bounds)

            physical_segments = [
                fixture.shape.vertices
                for fixture in physical_env.moon.fixtures
            ]
            flat_x = [
                x
                for segment in physical_segments
                if segment[0][1] == segment[1][1]
                and segment[0][1] > 0
                for x, _ in segment
            ]

            assert flat_x
            assert (min(flat_x), max(flat_x)) == pytest.approx(
                expected_bounds
            )

            scene = capture_scene(scenario_env)
            assert tuple(x for x, _ in scene.helipad) == pytest.approx(
                expected_bounds
            )

            for segment in scene.terrain:
                assert any(
                    np.allclose(segment, physical_segment)
                    for physical_segment in physical_segments
                ), f"Segmento dibujado sin colisión correspondiente: {segment}"
    finally:
        reference_env.close()
        scenario_env.close()