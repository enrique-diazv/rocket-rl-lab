CREATE TABLE adaptation_experiments (
    id TEXT PRIMARY KEY NOT NULL,
    created_at TEXT NOT NULL,
    config_json TEXT NOT NULL,
    cancel_requested INTEGER NOT NULL DEFAULT 0
        CHECK (cancel_requested IN (0, 1))
);

CREATE TABLE adaptation_jobs (
    id TEXT PRIMARY KEY NOT NULL,
    experiment_id TEXT NOT NULL
        REFERENCES adaptation_experiments(id),
    agent TEXT NOT NULL CHECK (
        agent IN ('precision', 'speed', 'efficiency', 'stability', 'balanced')
    ),
    status TEXT NOT NULL CHECK (
        status IN (
            'queued', 'running', 'evaluating', 'training',
            'already_adapted', 'adapted', 'budget_reached',
            'failed', 'cancelled'
        )
    ),
    position INTEGER NOT NULL CHECK (position >= 0),
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    progress_json TEXT,
    error TEXT,
    UNIQUE (experiment_id, agent),
    UNIQUE (experiment_id, position)
);

CREATE TABLE adaptation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT NOT NULL
        REFERENCES adaptation_experiments(id),
    job_id TEXT REFERENCES adaptation_jobs(id),
    event_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX adaptation_jobs_queue_idx
    ON adaptation_jobs(status, created_at, position);

CREATE UNIQUE INDEX adaptation_single_active_job_idx
    ON adaptation_jobs((1))
    WHERE status IN ('running', 'evaluating', 'training');

CREATE INDEX adaptation_events_experiment_idx
    ON adaptation_events(experiment_id, id);