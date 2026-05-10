# hyuabot-subway-timetable-updater

A one-time data loader that fetches full subway timetable data and populates the HYUabot database. Runs once at initial deployment.

## Overview

The job fetches complete timetable data for the two subway lines serving Hanyang University ERICA:

- **Line 4** (route ID: 1004) — Hanyang University station
- **Suin-Bundang Line** (route ID: 1071) — Sangnoksu station

Data is inserted into the `subway_timetable` table. Supports master-DB failover.

## Architecture

```
src/
├── main.py              # Entry point; fetches timetables for both lines
├── models.py            # SQLAlchemy ORM models (SubwayTimetable)
└── utils/
    └── database.py      # PostgreSQL engine factory with master failover
```

## Requirements

- Python ≥ 3.12
- PostgreSQL

## Environment Variables

| Variable            | Description              |
|---------------------|--------------------------|
| `POSTGRES_ID`       | PostgreSQL username      |
| `POSTGRES_PASSWORD` | PostgreSQL password      |
| `POSTGRES_HOST`     | PostgreSQL host          |
| `POSTGRES_PORT`     | PostgreSQL port          |
| `POSTGRES_DB`       | PostgreSQL database name |

## Running Locally

```bash
pip install -e .

export POSTGRES_ID=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=hyuabot

cd src && python main.py
```

## Docker

The container exits after a single run — trigger it as a Kubernetes Job or one-off container.

```bash
docker build -t hyuabot-subway-timetable-updater .

docker run --rm \
  -e POSTGRES_ID=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=hyuabot \
  hyuabot-subway-timetable-updater
```

## Development

```bash
pip install -e .[lint]       # flake8
pip install -e .[typecheck]  # mypy
pip install -e .[test]       # pytest
```

```bash
python -m flake8 src/ tests/
python -m mypy src/ tests/
python -m pytest -v
```

Tests run against a PostgreSQL instance at `localhost:25432`.

## CI/CD

| Workflow | Trigger | Jobs |
|---|---|---|
| `code-check.yml` | Push to any branch except `main` | lint, typecheck, test |
| `deploy.yml` | PR merged to `main` (or manual dispatch) | Docker build → push to `localhost:5000` |

CI runners: self-hosted X64 Linux (code checks) · ARM64 Linux (Docker build).

## License

GPLv3
