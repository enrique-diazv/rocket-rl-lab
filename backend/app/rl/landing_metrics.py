import gymnasium as gym
from gymnasium.envs.box2d.lunar_lander import LunarLander


def is_successful_landing(
    env: gym.Env,
    *,
    terminated: bool,
    truncated: bool,
) -> bool:
    if not terminated or truncated:
        return False

    lander_env = env.unwrapped

    if not isinstance(lander_env, LunarLander):
        raise TypeError("La métrica requiere un entorno LunarLander.")

    lander = lander_env.lander

    if lander is None:
        return False

    inside_pad = (
        lander_env.helipad_x1
        <= lander.position.x
        <= lander_env.helipad_x2
    )
    both_legs_contact = all(
        leg.ground_contact for leg in lander_env.legs
    )

    return bool(
        not lander_env.game_over
        and not lander.awake
        and both_legs_contact
        and inside_pad
    )