"""Legacy contract wrappers backed by the active ``claire.domain`` package."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from claire.domain.contract import ClaireIntent as ActiveClaireIntent
from claire.domain.contract import ClaireResult as ActiveClaireResult


class ClaireIntent(ActiveClaireIntent):
    def __init__(self, raw_input: str, intent_id: str | None = None, mode: str = "deterministic", request_type: str = "evaluate", **extra: Any):
        super().__init__(
            raw_input=raw_input,
            intent_id=intent_id or f"intent-{uuid.uuid4().hex[:8]}",
            mode=mode,
            request_type=request_type,
            **extra,
        )

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not self.raw_input:
            errors.append("raw_input is required")
        if self.mode not in {"deterministic", "connected", "hybrid"}:
            errors.append("mode must be deterministic, connected, or hybrid")
        return errors


class ClaireResult(ActiveClaireResult):
    def __init__(self, intent_id: str | None = None, **kwargs: Any):
        super().__init__(intent_id=intent_id, **kwargs)
        self.intent_id = intent_id or self.run_id

    def to_dict(self) -> Dict[str, Any]:
        payload = super().to_dict()
        payload["intent_id"] = self.intent_id
        return payload


class ContractValidator:
    def validate_input(self, intent: ClaireIntent) -> List[str]:
        return intent.validate()

    def validate_intent(self, payload: Dict[str, Any]) -> ClaireIntent:
        return ClaireIntent(
            intent_id=payload.get("intent_id") or payload.get("id"),
            raw_input=payload.get("raw_input") or payload.get("text") or payload.get("input") or "",
            mode=payload.get("mode", "deterministic"),
            request_type=payload.get("request_type", "evaluate"),
        )

    def validate(self, payload: Dict[str, Any]) -> ClaireIntent:
        return self.validate_intent(payload)
