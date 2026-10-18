from dataclasses import dataclass


@dataclass(frozen=True)
class EpisodeEvaluation:
    seed: int
    steps: int
    total_reward: float
    success: bool
    terminated: bool
    truncated: bool