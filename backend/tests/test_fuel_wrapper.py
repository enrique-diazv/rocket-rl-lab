import numpy as np
import pytest

from app.rl.env_factory import create_lander_env
from app.rl.scenario_config import ScenarioConfig
from app.rl.scenario_env import create_scenario_env
from app.rl.rewards import RewardShapingWrapper

@pytest.mark.parametrize(
    ("fuel_budget", "action_sequence"),
    [
        (
            0.0,
            [
                (2, 0, 0.0, 0.0),
                (1, 0, 0.0, 0.0),
                (3, 0, 0.0, 0.0),
            ],
        ),
        (
            0.36,
            [
                (2, 2, 0.30, 0.06),
                (2, 0, 0.0, 0.06),
                (1, 1, 0.03, 0.03),
                (3, 3, 0.03, 0.0),
                (2, 0, 0.0, 0.0),
            ],
        ),
    ],
)
def test_fuel_limits_propulsion_and_refills_on_reset(
    fuel_budget: float,
    action_sequence: list[tuple[int, int, float, float]],
) -> None:
    reference_env = create_lander_env()
    fuel_env = RewardShapingWrapper(
        create_scenario_env(
            ScenarioConfig(fuel_budget=fuel_budget)
        ),
        fuel_penalty=1.0,
    )

    try:
        for seed in (42, 43):
            reference_env.reset(seed=seed)
            _, reset_info = fuel_env.reset(seed=seed)
            assert reset_info["fuel_remaining"] == pytest.approx(fuel_budget)

            for requested, executed, consumed, remaining in action_sequence:
                expected_obs, expected_reward, expected_end, expected_cut, _ = (
                    reference_env.step(executed)
                )
                observation, reward, terminated, truncated, info = (
                    fuel_env.step(requested)
                )

                np.testing.assert_array_equal(observation, expected_obs)
                assert reward == pytest.approx(
                    float(expected_reward) - consumed
                )
                assert (terminated, truncated) == (expected_end, expected_cut)
                assert info["requested_action"] == requested
                assert info["executed_action"] == executed
                assert info["fuel_consumed"] == pytest.approx(consumed)
                assert info["fuel_remaining"] == pytest.approx(remaining)
    finally:
        reference_env.close()
        fuel_env.close()