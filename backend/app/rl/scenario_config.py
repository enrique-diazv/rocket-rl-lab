from pydantic import BaseModel, ConfigDict, Field


class ScenarioConfig(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    gravity: float = Field(
        default=-10.0,
        gt=-12.0,
        lt=0.0,
        allow_inf_nan=False,
    )

    max_episode_steps: int = Field(
        default=1000,
        gt=0,
        strict=True,
    )