import numpy as np
import pytest

from app.rl.env_factory import create_lander_env
from app.rl.rewards import RewardShapingWrapper


@pytest.mark.parametrize("time_penalty", [0.0, 0.05])
def test_shaping_preserves_simulation(time_penalty: float) -> None:
    base_env = create_lander_env()
    shaped_env = RewardShapingWrapper(
        create_lander_env(),
        time_penalty=time_penalty,
    )

    try:
        for seed in (42, 43):
            base_obs, _ = base_env.reset(seed=seed)
            obs, _ = shaped_env.reset(seed=seed)
            base_env.action_space.seed(seed)

            expected_base_return = 0.0
            expected_total_return = 0.0
            steps = 0

            np.testing.assert_array_equal(obs, base_obs)

            while True:
                action = int(base_env.action_space.sample())

                base_obs, base_reward, base_terminated, base_truncated, _ = (
                    base_env.step(action)
                )
                obs, reward, terminated, truncated, info = shaped_env.step(action)

                steps += 1
                expected_base_return += float(base_reward)
                expected_total_return += reward

                np.testing.assert_array_equal(obs, base_obs)
                assert (terminated, truncated) == (
                    base_terminated,
                    base_truncated,
                )

                components = info["reward_components"]
                assert components["base"] == pytest.approx(float(base_reward))
                assert components["shaping"] == pytest.approx(-time_penalty)
                assert components["total"] == pytest.approx(reward)
                assert reward == pytest.approx(float(base_reward) - time_penalty)

                if terminated or truncated:
                    assert info["base_return"] == pytest.approx(
                        expected_base_return
                    )
                    assert info["shaping_return"] == pytest.approx(
                        -time_penalty * steps
                    )
                    assert info["total_return"] == pytest.approx(
                        expected_total_return
                    )
                    assert info["total_return"] == pytest.approx(
                        info["base_return"] + info["shaping_return"]
                    )
                    break
    finally:
        base_env.close()
        shaped_env.close()