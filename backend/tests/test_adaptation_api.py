from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rl.adaptation_config import AdaptationConfig
from app.storage import database
from app.storage.job_queue import create_adaptation_experiment


TEST_OPERATOR_TOKEN = "operator-test-token-" * 3


@pytest.fixture
def api_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "api.sqlite3",
    )

    with TestClient(app) as client:
        yield client

@pytest.mark.parametrize("operation", ["create", "cancel"])
@pytest.mark.parametrize(
    ("configured_token", "provided_token", "expected_http_status"),
    [
        (None, None, 503),
        (TEST_OPERATOR_TOKEN, None, 401),
        (TEST_OPERATOR_TOKEN, "incorrect-token", 401),
        (TEST_OPERATOR_TOKEN, TEST_OPERATOR_TOKEN, 202),
    ],
    ids=["unconfigured", "missing", "wrong", "valid"],
)
def test_mutations_require_operator_credentials(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    configured_token: str | None,
    provided_token: str | None,
    expected_http_status: int,
) -> None:
    if configured_token is None:
        monkeypatch.delenv("ROCKET_OPERATOR_TOKEN", raising=False)
    else:
        monkeypatch.setenv("ROCKET_OPERATOR_TOKEN", configured_token)

    headers = (
        {}
        if provided_token is None
        else {"Authorization": f"Bearer {provided_token}"}
    )

    if operation == "cancel":
        experiment_id = create_adaptation_experiment(
            AdaptationConfig(
                max_additional_timesteps=0,
                block_timesteps=2048,
            )
        )
        path = f"/api/adaptation/experiments/{experiment_id.hex}/cancel"
        payload = None
    else:
        path = "/api/adaptation/experiments"
        payload = {
            "max_additional_timesteps": 0,
            "block_timesteps": 2048,
        }

    response = api_client.post(path, headers=headers, json=payload)

    assert response.status_code == expected_http_status

    with database.database_connection() as connection:
        statuses = [
            row["status"]
            for row in connection.execute(
                "SELECT status FROM adaptation_jobs ORDER BY position"
            ).fetchall()
        ]

    if operation == "cancel":
        expected_state = (
            "cancelled" if expected_http_status == 202 else "queued"
        )
        expected_statuses = [expected_state] * 5
    elif expected_http_status == 202:
        expected_statuses = ["queued"] * 5
    else:
        expected_statuses = []

    assert statuses == expected_statuses