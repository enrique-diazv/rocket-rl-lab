from dataclasses import dataclass


@dataclass(frozen=True)
class EpisodeEvaluation:
    seed: int
    steps: int
    total_reward: float
    success: bool
    terminated: bool
    truncated: bool
    final_horizontal_error: float | None = None
    engine_usage_cost: float | None = None
    pre_contact_speed: float | None = None
    pre_contact_abs_angle: float | None = None
    pre_contact_angular_speed: float | None = None