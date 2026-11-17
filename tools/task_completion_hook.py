"""Post-task loop hook for the CC-01 repository.

This is intentionally a small template. Call it after each completed task so
the workflow has one stable extension point for future automation.

Example:
    python tools/task_completion_hook.py --task RF-A3 --status complete \
        --note "Datum table updated and Blender validation passed"
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "outputs" / "validation" / "task_completion_hook.jsonl"


def post_task_hook(task: str, status: str, note: str = "") -> dict[str, str]:
    """Run the empty post-task extension point and record its invocation.

    Keep future task-loop behavior in this function. The current hook only
    records a structured completion event and deliberately performs no model
    edits, rebuilds, commits, or external actions.
    """
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "status": status,
        "note": note,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def main() -> None:
    parser = argparse.ArgumentParser(description="Invoke the CC-01 post-task loop hook.")
    parser.add_argument("--task", required=True, help="Task or checklist ID just completed.")
    parser.add_argument("--status", default="complete", choices=("complete", "partial", "blocked"))
    parser.add_argument("--note", default="", help="Short verification or handoff note.")
    args = parser.parse_args()
    event = post_task_hook(args.task, args.status, args.note)
    print("CC-01 task completion hook called:", json.dumps(event, ensure_ascii=False))


if __name__ == "__main__":
    main()
