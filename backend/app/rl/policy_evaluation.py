from collections.abc import Sequence

from app.rl.scenario_config import ScenarioConfig
from app.rl.scenario_env import create_scenario_env

import gymnasium as gym
from stable_baselines3 import PPO

from app.rl.contact_metrics import FirstContactTracker
from app.rl.engine_config import ENGINE_COST_BY_ACTION
from app.rl.evaluation_metrics import EpisodeEvaluation
from app.rl.landing_metrics import is_successful_landing


def evaluate_episode(
    model: PPO,
    env: gym.Env,
    *,
    seed: int,
) -> EpisodeEvaluation:
    observation, _ = env.reset(seed=seed)
    contact_tracker = FirstContactTracker(env.unwrapped)
    total_reward = 0.0
    engine_usage_cost = 0.0
    steps = 0
    terminated = False
    truncated = False

    while not (terminated or truncated):
        action, _ = model.predict(observation, deterministic=True)
        action_id = int(action.item())
        observation, reward, terminated, truncated, info = env.step(action_id)
        contact_tracker.observe()
        total_reward += float(reward)
        engine_usage_cost += info.get(
            "fuel_consumed",
            ENGINE_COST_BY_ACTION[action_id],
        )
        steps += 1

    physical_env = env.unwrapped
    pad_center = (physical_env.helipad_x1 + physical_env.helipad_x2) / 2.0
    final_horizontal_error = abs(float(physical_env.lander.position.x) - pad_center)
    contact_motion = contact_tracker.pre_contact_motion

    return EpisodeEvaluation(
        seed=seed,
        steps=steps,
        total_reward=total_reward,
        success=is_successful_landing(
            env,
            terminated=terminated,
            truncated=truncated,
        ),
        terminated=terminated,
        truncated=truncated,
        final_horizontal_error=final_horizontal_error,
        engine_usage_cost=engine_usage_cost,
        pre_contact_speed=(
            contact_motion.speed if contact_motion is not None else None
        ),
        pre_contact_abs_angle=(
            contact_motion.abs_angle if contact_motion is not None else None
        ),
        pre_contact_angular_speed=(
            contact_motion.angular_speed if contact_motion is not None else None
        ),
    )


def evaluate_policy(
    model: PPO,
    scenario: ScenarioConfig,
    *,
    seeds: Sequence[int],
) -> list[EpisodeEvaluation]:
    if not seeds:
        raise ValueError("La evaluación necesita al menos una semilla.")

    env = create_scenario_env(scenario)

    try:
        return [evaluate_episode(model, env, seed=seed) for seed in seeds]
    finally:
        env.close()
