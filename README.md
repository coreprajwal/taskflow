ok# TaskFlow

A lightweight REST API for managing tasks, built with Flask.

## Setup

```bash
pip install -r requirements.txt
```

## Run the server

```bash
flask --app taskflow.app run
```

## Run tests

```bash
pytest tests/ -v
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List all tasks (filter by `?status=` or `?priority=`) |
| POST | `/tasks` | Create a task |
| GET | `/tasks/<id>` | Get a task |
| PUT | `/tasks/<id>` | Update a task |
| DELETE | `/tasks/<id>` | Delete a task |
| POST | `/tasks/<id>/complete` | Mark a task as complete |
| GET | `/tasks/stats` | Get task counts by status |

### Create task body

```json
{
  "title": "Fix the bug",
  "description": "Optional longer description",
  "priority": "high"
}
```

Priorities: `low`, `medium`, `high`  
Statuses: `pending`, `in_progress`, `completed`


agentic project work
