from app.rl.adaptation_metrics import AdaptationResult
from app.storage import adaptations
from app.storage.job_queue import (
    ClaimedAdaptationJob,
    get_active_adaptation_job,
)
from app.workers.recovery import recover_interrupted_job
from pathlib import Path

import pytest

import json

from app.rl.adaptation_metrics import AdaptationEvaluation, AdaptationProgress
from app.rl.evaluation_metrics import EpisodeEvaluation
from app.storage.job_queue import record_adaptation_progress

from app.rl.adaptation_config import AdaptationConfig
from app.storage import database
from app.storage.job_queue import (
    ActiveExperimentError,
    claim_next_adaptation_job,
    create_adaptation_experiment,
    is_adaptation_cancel_requested,
    request_adaptation_cancel,
    stop_adaptation_job,
)
from app.storage.schema import initialize_database


@pytest.fixture
def queue_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "queue.sqlite3",
    )
    initialize_database()


@pytest.mark.usefixtures("queue_database")
def test_queue_limits_experiments_and_active_jobs() -> None:
    config = AdaptationConfig(max_additional_timesteps=0)

    experiment_id = create_adaptation_experiment(config)

    with pytest.raises(ActiveExperimentError):
        create_adaptation_experiment(config)

    with database.database_connection() as connection:
        jobs = connection.execute(
            """
            SELECT agent, status
            FROM adaptation_jobs
            WHERE experiment_id = ?
            """,
            (experiment_id.hex,),
        ).fetchall()
        counts = connection.execute("""
            SELECT
                (SELECT COUNT(*) FROM adaptation_experiments),
                (SELECT COUNT(*) FROM adaptation_jobs),
                (SELECT COUNT(*) FROM adaptation_events)
            """).fetchone()

    assert {job["agent"] for job in jobs} == {
        "precision",
        "speed",
        "efficiency",
        "stability",
        "balanced",
    }
    assert all(job["status"] == "queued" for job in jobs)
    assert tuple(counts) == (1, 5, 1)

    claimed = claim_next_adaptation_job()
    assert claimed is not None
    assert claimed.experiment_id == experiment_id
    assert claim_next_adaptation_job() is None

    with database.database_connection() as connection:
        statuses = connection.execute("""
            SELECT status, COUNT(*) AS job_count
            FROM adaptation_jobs
            GROUP BY status
            """).fetchall()
        event_count = connection.execute(
            "SELECT COUNT(*) FROM adaptation_events"
        ).fetchone()[0]

    assert {row["status"]: row["job_count"] for row in statuses} == {
        "queued": 4,
        "running": 1,
    }
    assert event_count == 2


@pytest.mark.usefixtures("queue_database")
def test_pending_evaluation_preserves_previous_metrics() -> None:
    create_adaptation_experiment(
        AdaptationConfig(
            max_additional_timesteps=2048,
            block_timesteps=2048,
        )
    )
    claimed = claim_next_adaptation_job()
    assert claimed is not None

    episode = EpisodeEvaluation(
        seed=2000,
        steps=1000,
        total_reward=5.0,
        success=False,
        terminated=False,
        truncated=True,
    )
    evaluation = AdaptationEvaluation(
        extra_training_timesteps=0,
        training_episodes=0,
        elapsed_wall_seconds=1.0,
        episodes=(episode,),
    )

    record_adaptation_progress(
        claimed.job_id,
        AdaptationProgress(
            agent=claimed.agent,
            phase="evaluating",
            extra_training_timesteps=0,
            training_episodes=0,
            elapsed_wall_seconds=1.0,
            evaluation_count=1,
            evaluation=evaluation,
        ),
    )
    record_adaptation_progress(
        claimed.job_id,
        AdaptationProgress(
            agent=claimed.agent,
            phase="evaluating",
            extra_training_timesteps=2048,
            training_episodes=2,
            elapsed_wall_seconds=4.0,
            evaluation_count=1,
        ),
    )

    with database.database_connection() as connection:
        row = connection.execute(
            "SELECT progress_json FROM adaptation_jobs WHERE id = ?",
            (claimed.job_id.hex,),
        ).fetchone()

    snapshot = json.loads(row["progress_json"])
    assert snapshot["extra_training_timesteps"] == 2048
    assert snapshot["last_evaluation"]["extra_training_timesteps"] == 0
    assert snapshot["last_evaluation"]["mean_original_reward"] == 5.0


@pytest.mark.usefixtures("queue_database")
def test_cancel_request_waits_for_active_job_to_stop() -> None:
    experiment_id = create_adaptation_experiment(
        AdaptationConfig(max_additional_timesteps=0)
    )
    claimed = claim_next_adaptation_job()
    assert claimed is not None
    assert not is_adaptation_cancel_requested(experiment_id)

    request_adaptation_cancel(experiment_id)

    assert is_adaptation_cancel_requested(experiment_id)

    with database.database_connection() as connection:
        statuses = connection.execute("""
            SELECT status, COUNT(*) AS job_count
            FROM adaptation_jobs
            GROUP BY status
            """).fetchall()

    assert {row["status"]: row["job_count"] for row in statuses} == {
        "cancelled": 4,
        "running": 1,
    }

    stop_adaptation_job(claimed.job_id, status="cancelled")
    assert claim_next_adaptation_job() is None

    with database.database_connection() as connection:
        cancelled_count = connection.execute("""
            SELECT COUNT(*)
            FROM adaptation_jobs
            WHERE status = 'cancelled'
            """).fetchone()[0]
        events_before_repeat = connection.execute(
            "SELECT COUNT(*) FROM adaptation_events"
        ).fetchone()[0]

    assert cancelled_count == 5

    request_adaptation_cancel(experiment_id)
    stop_adaptation_job(claimed.job_id, status="cancelled")

    with database.database_connection() as connection:
        events_after_repeat = connection.execute(
            "SELECT COUNT(*) FROM adaptation_events"
        ).fetchone()[0]

    assert events_after_repeat == events_before_repeat

def _save_completed_adaptation(job: ClaimedAdaptationJob) -> Path:
    evaluation = AdaptationEvaluation(
        extra_training_timesteps=0,
        training_episodes=0,
        elapsed_wall_seconds=1.0,
        episodes=(
            EpisodeEvaluation(
                seed=2000,
                steps=1000,
                total_reward=5.0,
                success=False,
                terminated=False,
                truncated=True,
            ),
        ),
    )
    checkpoint = adaptations.adaptation_checkpoint_path(
        job.experiment_id, job.agent, 0
    )
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_bytes(b"checkpoint de prueba")

    adaptations.save_adaptation_evaluation(
        evaluation,
        experiment_id=job.experiment_id,
        agent=job.agent,
        evaluation_index=1,
    )
    adaptations.save_adaptation_result(
        AdaptationResult(
            agent=job.agent,
            status="budget_reached",
            evaluations=(evaluation,),
            time_to_threshold_steps=None,
        ),
        experiment_id=job.experiment_id,
    )
    record_adaptation_progress(
        job.job_id,
        AdaptationProgress(
            agent=job.agent,
            phase="evaluating",
            extra_training_timesteps=0,
            training_episodes=0,
            elapsed_wall_seconds=1.0,
            evaluation_count=1,
            evaluation=evaluation,
        ),
    )
    return checkpoint

@pytest.mark.usefixtures("queue_database")
@pytest.mark.parametrize(
    ("case", "expected_status"),
    [
        ("completed", "budget_reached"),
        ("interrupted", "failed"),
        ("cancel_requested", "cancelled"),
        ("changed_checkpoint", "failed"),
    ],
)
def test_worker_recovers_interrupted_job(
    case: str,
    expected_status: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        adaptations,
        "ADAPTATION_DIRECTORY",
        tmp_path / "adaptations",
    )
    create_adaptation_experiment(
        AdaptationConfig(max_additional_timesteps=0)
    )
    job = claim_next_adaptation_job()
    assert job is not None
    checkpoint = _save_completed_adaptation(job)

    if case in ("interrupted", "cancel_requested"):
        (checkpoint.parent / "result.json").unlink()

    if case == "cancel_requested":
        request_adaptation_cancel(job.experiment_id)
    elif case == "changed_checkpoint":
        checkpoint.write_bytes(b"checkpoint modificado")

    recover_interrupted_job()

    with database.database_connection() as connection:
        recovered = connection.execute(
            "SELECT status, error FROM adaptation_jobs WHERE id = ?",
            (job.job_id.hex,),
        ).fetchone()

    assert recovered["status"] == expected_status
    assert get_active_adaptation_job() is None
    assert checkpoint.is_file()
    assert (
        checkpoint.parent / "evaluations" / "evaluation_1.json"
    ).is_file()

    if case == "changed_checkpoint":
        assert "hash" in recovered["error"]