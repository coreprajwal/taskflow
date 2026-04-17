import pytest
from taskflow.app import app, store


@pytest.fixture(autouse=True)
def reset_store():
    """Reset the task store before each test."""
    store._tasks.clear()
    store._next_id = 1
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def create_task(client, title="Test task", description="A description", priority="high"):
    resp = client.post(
        "/tasks",
        json={"title": title, "description": description, "priority": priority},
    )
    assert resp.status_code == 201
    return resp.get_json()


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------

def test_create_task(client):
    task = create_task(client)
    assert task["title"] == "Test task"
    assert task["status"] == "pending"
    assert task["priority"] == "high"
    assert "created_at" in task
    assert "updated_at" in task


def test_get_task(client):
    created = create_task(client)
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == created["id"]


def test_get_missing_task(client):
    resp = client.get("/tasks/999")
    assert resp.status_code == 404


def test_list_tasks(client):
    create_task(client, title="Task A")
    create_task(client, title="Task B")
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_filter_by_status(client):
    create_task(client, title="Task A")
    t = create_task(client, title="Task B")
    client.put(f"/tasks/{t['id']}", json={"status": "in_progress"})
    resp = client.get("/tasks?status=in_progress")
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Task B"


def test_update_task(client):
    task = create_task(client)
    resp = client.put(f"/tasks/{task['id']}", json={"title": "Updated", "priority": "low"})
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated["title"] == "Updated"
    assert updated["priority"] == "low"
    assert updated["description"] == "A description"  # unchanged fields preserved


def test_delete_task(client):
    task = create_task(client)
    resp = client.delete(f"/tasks/{task['id']}")
    assert resp.status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_stats(client):
    create_task(client, title="A")
    t = create_task(client, title="B")
    client.post(f"/tasks/{t['id']}/complete")
    resp = client.get("/tasks/stats")
    data = resp.get_json()
    assert data["total"] == 2
    assert data["by_status"]["completed"] == 1
    assert data["by_status"]["pending"] == 1


# ---------------------------------------------------------------------------
# complete_task — this is where the bug surfaces
# ---------------------------------------------------------------------------

def test_complete_task_preserves_fields(client):
    """
    After marking a task complete, description and priority must still be
    present in the response (and in subsequent GET requests).
    """
    task = create_task(client, description="Important details", priority="high")
    task_id = task["id"]

    resp = client.post(f"/tasks/{task_id}/complete")
    assert resp.status_code == 200
    body = resp.get_json()

    # These fields must not disappear after completion
    assert "description" in body, "description missing from complete response"
    assert "priority" in body, "priority missing from complete response"
    assert body["status"] == "completed"

    # Verify persistence via GET
    fetched = client.get(f"/tasks/{task_id}").get_json()
    assert fetched["description"] == "Important details"
    assert fetched["priority"] == "high"


def test_complete_task_sets_updated_at(client):
    """
    Completing a task must update the updated_at timestamp.
    """
    task = create_task(client)
    original_updated_at = task["updated_at"]

    import time; time.sleep(0.05)  # ensure clock advances

    resp = client.post(f"/tasks/{task['id']}/complete")
    body = resp.get_json()

    assert "updated_at" in body, "updated_at missing from complete response"
    assert body["updated_at"] != original_updated_at, (
        "updated_at was not refreshed when task was completed"
    )


def test_complete_already_completed_task(client):
    """Completing a task twice should be idempotent."""
    task = create_task(client)
    client.post(f"/tasks/{task['id']}/complete")
    resp = client.post(f"/tasks/{task['id']}/complete")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "completed"
