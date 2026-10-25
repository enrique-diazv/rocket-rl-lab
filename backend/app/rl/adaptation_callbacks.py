from stable_baselines3.common.callbacks import BaseCallback


class TrainingEpisodeCounter(BaseCallback):
    def __init__(self) -> None:
        super().__init__()
        self.completed_episodes = 0

    def _on_step(self) -> bool:
        self.completed_episodes += int(self.locals["dones"].sum())
        return True