from collections.abc import Callable, Sequence
from time import perf_counter
from uuid import UUID

from stable_baselines3 import PPO

from app.rl.adaptation_callbacks import TrainingEpisodeCounter
from app.rl.adaptation_config import AdaptationConfig
from app.rl.adaptation_metrics import (
    AdaptationEvaluation,
    AdaptationPhase,
    AdaptationProgress,
    AdaptationResult,
    AdaptationStatus,
)
from app.rl.policy_evaluation import evaluate_policy
from app.storage.adaptations import (
    create_adaptation_run,
    save_adaptation_checkpoint,
    save_adaptation_evaluation,
    save_adaptation_result,
)
from app.rl.adaptation_protocol import (
    ADAPTATION_EVALUATION_SEEDS,
    INITIAL_CONFIRMATION_SEEDS,
    REQUIRED_CONSECUTIVE_EVALUATIONS,
    SUCCESS_RATE_THRESHOLD,
)
from app.rl.adaptation_training import (
    adaptation_model,
    train_adaptation_block,
)

class AdaptationSession:
    _model: PPO
    _initial_timesteps: int
    _started_at: float

    def __init__(
        self,
        agent: str,
        config: AdaptationConfig,
        experiment_id: UUID,
        *,
        on_progress: Callable[[AdaptationProgress], None],
    ) -> None:
        self._agent = agent
        self._config = config
        self._experiment_id = experiment_id
        self._on_progress = on_progress
        self._counter = TrainingEpisodeCounter()
        self._evaluations: list[AdaptationEvaluation] = []

    def _extra_steps(self) -> int:
        return int(self._model.num_timesteps) - self._initial_timesteps

    def _emit(
        self,
        phase: AdaptationPhase,
        *,
        evaluation: AdaptationEvaluation | None = None,
    ) -> None:
        self._on_progress(
            AdaptationProgress(
                agent=self._agent,
                phase=phase,
                extra_training_timesteps=self._extra_steps(),
                training_episodes=self._counter.completed_episodes,
                elapsed_wall_seconds=perf_counter() - self._started_at,
                evaluation_count=len(self._evaluations),
                evaluation=evaluation,
            )
        )

    def _save_checkpoint(self) -> None:
        save_adaptation_checkpoint(
            self._model,
            experiment_id=self._experiment_id,
            agent=self._agent,
            extra_training_timesteps=self._extra_steps(),
        )

    def _evaluate(self, seeds: Sequence[int]) -> AdaptationEvaluation:
        self._emit("evaluating")
        episodes = evaluate_policy(
            self._model,
            self._config.scenario,
            seeds=seeds,
        )
        evaluation = AdaptationEvaluation(
            extra_training_timesteps=self._extra_steps(),
            training_episodes=self._counter.completed_episodes,
            elapsed_wall_seconds=perf_counter() - self._started_at,
            episodes=tuple(episodes),
        )
        save_adaptation_evaluation(
            evaluation,
            experiment_id=self._experiment_id,
            agent=self._agent,
            evaluation_index=len(self._evaluations) + 1,
        )
        self._evaluations.append(evaluation)
        self._emit("evaluating", evaluation=evaluation)
        return evaluation

    def run(self) -> AdaptationResult:
        self._started_at = perf_counter()

        with adaptation_model(self._agent, self._config) as model:
            self._model = model
            self._initial_timesteps = int(model.num_timesteps)
            create_adaptation_run(
                model,
                experiment_id=self._experiment_id,
                agent=self._agent,
                config=self._config,
            )
            self._save_checkpoint()
            return self._run_cycle()

    def _advance_block(self) -> AdaptationEvaluation:
        self._emit("training")
        train_adaptation_block(
            self._model,
            self._config,
            self._counter,
            initial_timesteps=self._initial_timesteps,
        )
        self._save_checkpoint()
        return self._evaluate(ADAPTATION_EVALUATION_SEEDS)

    def _finish(self, status: AdaptationStatus) -> AdaptationResult:
        result = AdaptationResult(
            agent=self._agent,
            status=status,
            evaluations=tuple(self._evaluations),
            time_to_threshold_steps=(
                None
                if status == "budget_reached"
                else self._extra_steps()
            ),
        )
        save_adaptation_result(
            result,
            experiment_id=self._experiment_id,
        )
        self._emit(status)
        return result

    def _run_cycle(self) -> AdaptationResult:
        initial = self._evaluate(ADAPTATION_EVALUATION_SEEDS)

        if initial.success_rate >= SUCCESS_RATE_THRESHOLD:
            confirmation = self._evaluate(INITIAL_CONFIRMATION_SEEDS)
            if confirmation.success_rate >= SUCCESS_RATE_THRESHOLD:
                return self._finish("already_adapted")

        consecutive_passes = 0

        while self._extra_steps() < self._config.max_additional_timesteps:
            evaluation = self._advance_block()
            consecutive_passes = (
                consecutive_passes + 1
                if evaluation.success_rate >= SUCCESS_RATE_THRESHOLD
                else 0
            )

            if consecutive_passes >= REQUIRED_CONSECUTIVE_EVALUATIONS:
                return self._finish("adapted")

        return self._finish("budget_reached")