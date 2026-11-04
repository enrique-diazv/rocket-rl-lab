from pydantic import BaseModel, Field

from app.rl.adaptation_metrics import AdaptationPhase

from datetime import datetime
from typing import Literal
from uuid import UUID

from app.rl.adaptation_config import AdaptationConfig
from app.rl.scenario_config import ScenarioConfig


class AdaptationEvaluationSummary(BaseModel):
    evaluation_index: int = Field(ge=1)
    extra_training_timesteps: int = Field(ge=0)
    training_episodes: int = Field(ge=0)
    elapsed_wall_seconds: float = Field(ge=0, allow_inf_nan=False)
    episode_count: int = Field(ge=1)
    success_rate: float = Field(
        ge=0,
        le=1,
        allow_inf_nan=False,
    )
    mean_original_reward: float = Field(allow_inf_nan=False)


class AdaptationProgressSnapshot(BaseModel):
    agent: str
    phase: AdaptationPhase
    extra_training_timesteps: int = Field(ge=0)
    training_episodes: int = Field(ge=0)
    elapsed_wall_seconds: float = Field(ge=0, allow_inf_nan=False)
    evaluation_count: int = Field(ge=0)
    last_evaluation: AdaptationEvaluationSummary | None


AdaptationJobStatus = (
    Literal["queued", "running", "failed", "cancelled"] | AdaptationPhase
)


class AdaptationJobSnapshot(BaseModel):
    id: UUID
    agent: str
    status: AdaptationJobStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    progress: AdaptationProgressSnapshot | None
    error: str | None


class AdaptationExperimentSnapshot(BaseModel):
    id: UUID
    created_at: datetime
    config: AdaptationConfig
    cancel_requested: bool
    jobs: list[AdaptationJobSnapshot] = Field(
        min_length=5,
        max_length=5,
    )
    last_event_id: int = Field(ge=0)


class AdaptationScenarioRequest(ScenarioConfig):
    max_episode_steps: int = Field(
        default=1000,
        gt=0,
        le=2000,
        strict=True,
    )


class AdaptationExperimentRequest(AdaptationConfig):
    scenario: AdaptationScenarioRequest = Field(
        default_factory=AdaptationScenarioRequest,
    )
    max_additional_timesteps: int = Field(
        default=102_400,
        ge=0,
        le=102_400,
        multiple_of=2048,
        strict=True,
    )
    block_timesteps: int = Field(
        default=10_240,
        gt=0,
        le=10_240,
        multiple_of=2048,
        strict=True,
    )


AdaptationEventType = Literal[
    "experiment_created",
    "job_started",
    "job_progress",
    "evaluation_completed",
    "job_stopped",
    "cancel_requested",
]


class AdaptationEventSnapshot(BaseModel):
    id: int = Field(gt=0)
    experiment_id: UUID
    job_id: UUID | None
    event_type: AdaptationEventType
    created_at: datetime
    agent: str | None
    status: AdaptationJobStatus | None
    finished_at: datetime | None
    progress: AdaptationProgressSnapshot | None
    cancel_requested: bool | None
    error: str | None


class AdaptationAgentSummary(BaseModel):
    id: str
    name: str
    checkpoint_available: bool
