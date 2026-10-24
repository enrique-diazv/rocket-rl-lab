from dataclasses import dataclass


@dataclass(frozen=True)
class RewardWeights:
    time_penalty: float = 0.0
    hover_bonus: float = 0.0
    progress_weight: float = 0.0
    horizontal_progress_weight: float = 0.0
    fuel_penalty: float = 0.0
    stability_penalty: float = 0.0


AGENT_PROFILES: dict[str, RewardWeights] = {
    "precision": RewardWeights(
        time_penalty=0.05,
        horizontal_progress_weight=10.0,
    ),
    "speed": RewardWeights(
        time_penalty=0.10,
    ),
    "efficiency": RewardWeights(
        time_penalty=0.05,
        fuel_penalty=1.0,
    ),
    "stability": RewardWeights(
        time_penalty=0.05,
        progress_weight=10.0,
        stability_penalty=0.10,
    ),
    "balanced": RewardWeights(
        time_penalty=0.05,
        progress_weight=5.0,
        horizontal_progress_weight=5.0,
        fuel_penalty=0.5,
        stability_penalty=0.05,
    ),
}