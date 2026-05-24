from __future__ import annotations

from typing import Dict, List


class RetryDeadLetterManager:
    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts
        self.attempts: Dict[str, int] = {}
        self.dead_letters: List[dict] = []

    def should_retry(self, request_id: str, status: str) -> bool:
        if status in {"success", "blocked", "review_required"}:
            return False
        current = self.attempts.get(request_id, 0)
        return current < self.max_attempts

    def record_failure(self, request_id: str, status: str, error: str | None = None) -> dict:
        self.attempts[request_id] = self.attempts.get(request_id, 0) + 1
        if self.attempts[request_id] >= self.max_attempts:
            item = {
                "request_id": request_id,
                "status": status,
                "error": error,
                "attempts": self.attempts[request_id],
            }
            self.dead_letters.append(item)
            return {"dead_lettered": True, "item": item}
        return {"dead_lettered": False, "attempts": self.attempts[request_id]}

    def snapshot(self) -> dict:
        return {"attempts": dict(self.attempts), "dead_letters": list(self.dead_letters)}
