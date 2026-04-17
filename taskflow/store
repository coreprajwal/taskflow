from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


class TaskStore:
    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def all(self):
        return list(self._tasks.values())

    def get(self, task_id: int):
        return self._tasks.get(task_id)

    def create(self, title: str, description: str = "", priority: str = "medium"):
        task_id = self._next_id
        self._next_id += 1
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": _now(),
            "updated_at": _now(),
        }
        self._tasks[task_id] = task
        return task

    def update(self, task_id: int, data: dict):
        task = self._tasks[task_id]
        allowed = {"title", "description", "priority", "status"}
        for key, value in data.items():
            if key in allowed:
                task[key] = value
        task["updated_at"] = _now()
        return task

    def delete(self, task_id: int):
        del self._tasks[task_id]
