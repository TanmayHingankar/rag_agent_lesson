import json
from pathlib import Path
from datetime import datetime, timezone

class MemoryStore:
    def __init__(self, path="data/memory.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"runs": [], "failure_patterns": {}})

    def _read(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"runs": [], "failure_patterns": {}}

    def _write(self, data):
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def context(self, limit=5):
        data = self._read()
        patterns = sorted(
            data["failure_patterns"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]
        return [
            {"failure": k, **v}
            for k, v in patterns
        ]

    def record(self, topic, evaluations):
        data = self._read()
        failures = []
        for ev in evaluations:
            for check in ev.failed_checks:
                failures.append(check)
                p = data["failure_patterns"].setdefault(
                    check, {"count": 0, "last_seen": None}
                )
                p["count"] += 1
                p["last_seen"] = datetime.now(timezone.utc).isoformat()

        data["runs"].append({
            "topic": topic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "failures": failures,
            "attempts": len(evaluations),
        })
        data["runs"] = data["runs"][-50:]
        self._write(data)
