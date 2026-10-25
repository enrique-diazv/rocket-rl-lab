from pydantic import BaseModel, ConfigDict, Field

from app.rl.scenario_config import ScenarioConfig


class AdaptationConfig(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    scenario: ScenarioConfig = Field(
        default_factory=ScenarioConfig,
    )

    max_additional_timesteps: int = Field(
        default=102_400,
        ge=0,
        le=1_024_000,
        strict=True,
    )

    block_timesteps: int = Field(
        default=10_240,
        gt=0,
        le=102_400,
        strict=True,
    )