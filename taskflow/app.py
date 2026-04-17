from flask import Flask, jsonify, request
from taskflow.store import TaskStore

app = Flask(__name__)
store = TaskStore()


@app.route("/tasks", methods=["GET"])
def list_tasks():
    status = request.args.get("status")
    priority = request.args.get("priority")
    tasks = store.all()

    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]

    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    task = store.create(
        title=data["title"],
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
    )
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = store.get(task_id)
    if task is None:
        return jsonify({"error": "task not found"}), 404
    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = store.get(task_id)
    if task is None:
        return jsonify({"error": "task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400

    updated = store.update(task_id, data)
    return jsonify(updated)


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    task = store.get(task_id)
    if task is None:
        return jsonify({"error": "task not found"}), 404

    # BUG: this marks the task complete but does NOT persist updated_at timestamp
    # Also, it overwrites the entire task dict instead of merging, so description
    # and priority fields silently vanish from the response after completion.
    completed = {
        "id": task["id"],
        "title": task["title"],
        "status": "completed",
    }
    store._tasks[task_id] = completed
    return jsonify(completed)


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = store.get(task_id)
    if task is None:
        return jsonify({"error": "task not found"}), 404
    store.delete(task_id)
    return "", 204


@app.route("/tasks/stats", methods=["GET"])
def stats():
    tasks = store.all()
    counts = {"pending": 0, "in_progress": 0, "completed": 0}
    for t in tasks:
        s = t.get("status")
        if s in counts:
            counts[s] += 1
    return jsonify({"total": len(tasks), "by_status": counts})
