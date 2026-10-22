import pytest

from app.rl.env_factory import create_lander_env
from app.rl.landing_metrics import is_successful_landing


@pytest.mark.parametrize(
    "x, crashed, truncated, supported_legs, expected",
    [
        (10.0, False, False, (True, True), True),
        (10.0, True, False, (True, True), False),
        (12.970118, False, False, (True, True), False),
        (10.0, False, True, (True, True), False),
        (10.0, False, False, (True, False), False),
    ],
)
def test_landing_classification(
    x: float,
    crashed: bool,
    truncated: bool,
    supported_legs: tuple[bool, bool],
    expected: bool,
) -> None:
    env = create_lander_env()

    try:
        physical_env = env.unwrapped
        world = physical_env.world

        physical_env.moon = world.CreateStaticBody(
            position=(10.0, -0.1)
        )
        physical_env.moon.CreatePolygonFixture(
            box=(10.0, 0.1)
        )

        physical_env.lander = world.CreateDynamicBody(
            position=(x, 1.0)
        )
        physical_env.helipad_x1 = 8.0
        physical_env.helipad_x2 = 12.0
        physical_env.legs = []

        for offset, supported in zip((-0.25, 0.25), supported_legs):
            leg = world.CreateDynamicBody(
                position=(x + offset, 0.09 if supported else 2.0)
            )
            leg.CreatePolygonFixture(
                box=(0.1, 0.1),
                density=1.0,
            )
            leg.ground_contact = False
            physical_env.legs.append(leg)

        world.Step(1.0 / 50.0, 6, 2)

        physical_env.game_over = crashed
        physical_env.lander.awake = False

        result = is_successful_landing(
            env,
            terminated=True,
            truncated=truncated,
        )

        assert result is expected
    finally:
        env.close()