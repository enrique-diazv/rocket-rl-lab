from dataclasses import dataclass
from statistics import mean
from typing import Literal
from app.rl.evaluation_metrics import EpisodeEvaluation

AdaptationStatus = Literal[
    "already_adapted",
    "adapted",
    "budget_reached",
]

AdaptationPhase = Literal["evaluating", "training"] | AdaptationStatus


@dataclass(frozen=True)
class AdaptationEvaluation:
    extra_training_timesteps: int
    training_episodes: int
    elapsed_wall_seconds: float
    episodes: tuple[EpisodeEvaluation, ...]

    def __post_init__(self) -> None:
        if not self.episodes:
            raise ValueError("El registro debe contener episodios de evaluación.")

    @property
    def success_rate(self) -> float:
        return sum(episode.success for episode in self.episodes) / len(self.episodes)

    @property
    def mean_original_reward(self) -> float:
        return mean(episode.total_reward for episode in self.episodes)


@dataclass(frozen=True)
class AdaptationResult:
    agent: str
    status: AdaptationStatus
    evaluations: tuple[AdaptationEvaluation, ...]
    time_to_threshold_steps: int | None


@dataclass(frozen=True)
class AdaptationProgress:
    agent: str
    phase: AdaptationPhase
    extra_training_timesteps: int
    training_episodes: int
    elapsed_wall_seconds: float
    evaluation_count: int
    evaluation: AdaptationEvaluation | None = None
