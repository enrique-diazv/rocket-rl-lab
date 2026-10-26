from pathlib import Path
from uuid import UUID, uuid4

from stable_baselines3 import PPO

from app.rl.agent_profiles import AGENT_PROFILES

from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from platform import python_version
from typing import Any

from app.rl.adaptation_config import AdaptationConfig
from app.rl.adaptation_protocol import (
    ADAPTATION_EVALUATION_SEEDS,
    INITIAL_CONFIRMATION_SEEDS,
    REQUIRED_CONSECUTIVE_EVALUATIONS,
    SUCCESS_RATE_THRESHOLD,
)
from app.storage.checkpoints import CHECKPOINT_DIRECTORY

ADAPTATION_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "experiments" / "adaptations"
)
from app.rl.adaptation_metrics import AdaptationEvaluation, AdaptationResult

def adaptation_checkpoint_path(
    experiment_id: UUID,
    agent: str,
    extra_training_timesteps: int,
) -> Path:
    if agent not in AGENT_PROFILES:
        raise ValueError(f"Agente desconocido: {agent}")

    if extra_training_timesteps < 0:
        raise ValueError("Los pasos adicionales no pueden ser negativos.")

    path = (
        ADAPTATION_DIRECTORY
        / experiment_id.hex
        / agent
        / f"step_{extra_training_timesteps}.zip"
    ).resolve()

    if not path.is_relative_to(ADAPTATION_DIRECTORY.resolve()):
        raise ValueError("La ruta debe permanecer dentro de adaptaciones.")

    return path


def save_adaptation_checkpoint(
    model: PPO,
    *,
    experiment_id: UUID,
    agent: str,
    extra_training_timesteps: int,
) -> Path:
    destination = adaptation_checkpoint_path(
        experiment_id,
        agent,
        extra_training_timesteps,
    )

    if destination.exists():
        raise FileExistsError(f"El checkpoint ya existe: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        f"{destination.stem}.{uuid4().hex}.tmp.zip"
    )

    try:
        model.save(temporary)
        temporary.rename(destination)
    finally:
        temporary.unlink(missing_ok=True)

    return destination

def _write_json_record(
    destination: Path,
    payload: dict[str, Any],
) -> None:
    if destination.exists():
        raise FileExistsError(f"El registro ya existe: {destination}")

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        indent=2,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        f"{destination.name}.{uuid4().hex}.tmp"
    )

    try:
        temporary.write_text(serialized, encoding="utf-8")
        temporary.rename(destination)
    finally:
        temporary.unlink(missing_ok=True)


def create_adaptation_run(
    model: PPO,
    *,
    experiment_id: UUID,
    agent: str,
    config: AdaptationConfig,
) -> Path:
    directory = adaptation_checkpoint_path(
        experiment_id, agent, 0
    ).parent
    directory.mkdir(parents=True, exist_ok=False)
    source = CHECKPOINT_DIRECTORY / f"{agent}.zip"

    payload = {
        "schema_version": 1,
        "experiment_id": experiment_id.hex,
        "agent": agent,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "python_version": python_version(),
        "base_checkpoint_sha256": sha256(source.read_bytes()).hexdigest(),
        "base_training_timesteps": int(model.num_timesteps),
        "config": config.model_dump(),
        "reward_weights": asdict(AGENT_PROFILES[agent]),
        "protocol": {
            "evaluation_seeds": ADAPTATION_EVALUATION_SEEDS,
            "initial_confirmation_seeds": INITIAL_CONFIRMATION_SEEDS,
            "success_rate_threshold": SUCCESS_RATE_THRESHOLD,
            "required_consecutive_evaluations": REQUIRED_CONSECUTIVE_EVALUATIONS,
        },
        "ppo": {
            "policy_kwargs": model.policy_kwargs,
            "n_steps": model.n_steps,
            "n_envs": model.n_envs,
            "batch_size": model.batch_size,
            "n_epochs": model.n_epochs,
            "seed": model.seed,
            "device": str(model.device),
        },
        "versions": {
            name: version(name)
            for name in (
                "gymnasium",
                "Box2D",
                "numpy",
                "stable-baselines3",
                "torch",
            )
        },
    }

    _write_json_record(directory / "config.json", payload)
    return directory

def _evaluation_payload(
    evaluation: AdaptationEvaluation,
) -> dict[str, Any]:
    return {
        **asdict(evaluation),
        "success_rate": evaluation.success_rate,
        "mean_original_reward": evaluation.mean_original_reward,
    }


def save_adaptation_evaluation(
    evaluation: AdaptationEvaluation,
    *,
    experiment_id: UUID,
    agent: str,
    evaluation_index: int,
) -> Path:
    if evaluation_index < 1:
        raise ValueError("El índice de evaluación debe ser positivo.")

    checkpoint = adaptation_checkpoint_path(
        experiment_id,
        agent,
        evaluation.extra_training_timesteps,
    )
    destination = (
        checkpoint.parent
        / "evaluations"
        / f"evaluation_{evaluation_index}.json"
    )
    payload = {
        "schema_version": 1,
        "experiment_id": experiment_id.hex,
        "agent": agent,
        "evaluation_index": evaluation_index,
        "checkpoint_filename": checkpoint.name,
        "checkpoint_sha256": sha256(checkpoint.read_bytes()).hexdigest(),
        "evaluation": _evaluation_payload(evaluation),
    }

    _write_json_record(destination, payload)
    return destination


def save_adaptation_result(
    result: AdaptationResult,
    *,
    experiment_id: UUID,
) -> Path:
    directory = adaptation_checkpoint_path(
        experiment_id,
        result.agent,
        0,
    ).parent
    destination = directory / "result.json"
    payload = {
        "schema_version": 1,
        "experiment_id": experiment_id.hex,
        "agent": result.agent,
        "status": result.status,
        "time_to_threshold_steps": result.time_to_threshold_steps,
        "evaluations": [
            _evaluation_payload(evaluation)
            for evaluation in result.evaluations
        ],
    }

    _write_json_record(destination, payload)
    return destination