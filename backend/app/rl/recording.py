from stable_baselines3 import PPO

from app.rl.env_factory import create_lander_env
from app.rl.landing_metrics import is_successful_landing
from app.rl.trajectory import (
    EpisodeTrajectory,
    capture_frame,
    capture_scene,
)


def record_episode(model: PPO, *, seed: int) -> EpisodeTrajectory:
    env = create_lander_env()

    try:
        observation, _ = env.reset(seed=seed)
        scene = capture_scene(env)
        frames = [capture_frame(env)]
        total_reward = 0.0
        terminated = False
        truncated = False

        while not (terminated or truncated):
            action, _ = model.predict(
                observation,
                deterministic=True,
            )
            observation, reward, terminated, truncated, _ = (
                env.step(action.item())
            )
            total_reward += float(reward)
            frames.append(capture_frame(env))

        return EpisodeTrajectory(
            seed=seed,
            steps=len(frames) - 1,
            total_reward=total_reward,
            success=is_successful_landing(
                env,
                terminated=terminated,
                truncated=truncated,
            ),
            terminated=terminated,
            truncated=truncated,
            scene=scene,
            frames=frames,
        )
    finally:
        env.close()