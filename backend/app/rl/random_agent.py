from app.rl.env_factory import create_lander_env


def main() -> None:
    env = create_lander_env(render_mode="human")

    try:
        env.action_space.seed(42)

        for episode_index in range(3):
            env.reset(seed=42 + episode_index)
            total_reward = 0.0
            terminated = False
            truncated = False

            while not (terminated or truncated):
                action = env.action_space.sample()
                _, reward, terminated, truncated, _ = env.step(action)
                total_reward += float(reward)

            print(
                f"Episodio {episode_index + 1}: "
                f"recompensa={total_reward:.2f}, "
                f"terminated={terminated}, truncated={truncated}"
            )
    finally:
        env.close()


if __name__ == "__main__":
    main()