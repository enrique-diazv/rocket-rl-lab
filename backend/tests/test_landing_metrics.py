import pytest

from app.rl.env_factory import create_lander_env
from app.rl.landing_metrics import is_successful_landing


@pytest.mark.parametrize(
    "x, crashed, truncated, expected",
    [
        (10.0, False, False, True),
        (10.0, True, False, False),
        (12.970118, False, False, False),
        (10.0, False, True, False),
    ],
)
def test_landing_classification(
    x: float,
    crashed: bool,
    truncated: bool,
    expected: bool,
) -> None:
    env = create_lander_env()

    try:
        env.reset(seed=42)
        physical_env = env.unwrapped

        physical_env.game_over = crashed
        physical_env.lander.position = (
            x,
            physical_env.lander.position.y,
        )
        physical_env.lander.awake = False

        for leg in physical_env.legs:
            leg.ground_contact = True

        result = is_successful_landing(
            env,
            terminated=True,
            truncated=truncated,
        )

        assert result is expected
    finally:
        env.close()