from __future__ import annotations

"""
Claire Command Classification and Response Cards — S457-S463

Full replacement repair for S457-S463.

Fix:
- Commands that ask Claire to analyze/evaluate/research a domain topic and merely include
  the word "suggest" should remain Ask Claire answer cards.
- "suggest_next_step" is reserved for operator workflow commands such as
  "move forward", "what now", "next", "continue", or "what should we do".

This module remains read-only and governed:
- no runtime mutation
- no runtime truth writes
- no automatic updates
- no autonomous execution
- no live web execution
- no browser execution
- no response-body reads
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S457-S463"
PHASE = "S457-S463"
JS_ASSET = "frontend/cockpit/shell/assets/claire_command_response_cards.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_command_response_cards.css"


BLOCKED_AUTHORITY: Dict[str, bool] = {
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_allowed": False,
    "runtime_truth_write_allowed": False,
    "automatic_updates_enabled": False,
    "autonomous_crawling_enabled": False,
    "autonomous_execution_enabled": False,
    "autonomous_agent_execution_enabled": False,
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
}


COMMAND_TYPES: Dict[str, Dict[str, Any]] = {
    "ask_claire": {
        "label": "Ask Claire",
        "description": "A normal governed intelligence question.",
        "allowed": True,
        "read_only": True,
        "card_type": "answer",
    },
    "explain_system_state": {
        "label": "Explain System State",
        "description": "Explain known runtime, lifecycle, payload, or governance state.",
        "allowed": True,
        "read_only": True,
        "card_type": "status",
    },
    "explain_route": {
        "label": "Explain Route",
        "description": "Explain lifecycle route, route hints, or why a path is selected.",
        "allowed": True,
        "read_only": True,
        "card_type": "route",
    },
    "explain_evidence": {
        "label": "Explain Evidence",
        "description": "Explain evidence requirement, source quality, confidence, or verification needs.",
        "allowed": True,
        "read_only": True,
        "card_type": "evidence",
    },
    "suggest_next_step": {
        "label": "Suggest Next Step",
        "description": "Suggest a safe next operator action without executing it.",
        "allowed": True,
        "read_only": True,
        "card_type": "next_step",
    },
    "help": {
        "label": "Help",
        "description": "Show available safe command categories.",
        "allowed": True,
        "read_only": True,
        "card_type": "help",
    },
    "prohibited_authority": {
        "label": "Prohibited Authority Command",
        "description": "Requests mutation, autonomous action, automatic update, or uncontrolled live web behavior.",
        "allowed": False,
        "read_only": True,
        "card_type": "blocked",
    },
    "unsupported": {
        "label": "Unsupported Command",
        "description": "Unrecognized command. Falls back to governed Q&A.",
        "allowed": True,
        "read_only": True,
        "card_type": "answer",
    },
}


PROHIBITED_TERMS = [
    "mutate runtime",
    "modify runtime",
    "rewrite active",
    "overwrite active",
    "change active code",
    "autonomous execute",
    "execute autonomously",
    "auto update",
    "automatic update",
    "uncontrolled crawl",
    "crawl the web automatically",
    "live crawl",
    "bypass governance",
    "skip approval",
    "ignore safety",
    "disable governance",
    "turn off safety",
    "write runtime truth",
]


COMMAND_KEYWORDS: Dict[str, List[str]] = {
    "explain_system_state": [
        "status",
        "system state",
        "ready",
        "readiness",
        "health",
        "payload",
        "dashboard",
        "governance state",
        "safety state",
    ],
    "explain_route": [
        "explain the route",
        "explain route",
        "selected path",
        "terminal state",
        "why did claire",
        "where are we",
    ],
    "explain_evidence": [
        "explain evidence",
        "evidence requirement",
        "source quality",
        "citation",
        "confidence",
        "verify",
        "proof",
        "supporting",
        "documented",
    ],
    "suggest_next_step": [
        "next",
        "move forward",
        "what now",
        "what should we do",
        "continue",
        "recommend next",
        "suggest next",
        "safe next step",
    ],
    "help": [
        "help",
        "commands",
        "what can claire do",
        "options",
    ],
}


ASK_CLAIRE_ANALYSIS_TERMS = [
    "can claire",
    "analyze",
    "analyse",
    "evaluate",
    "research",
    "assess",
    "compare",
    "identify",
    "review",
    "explain this",
    "question",
    "answer",
    "market",
    "engineering",
    "portfolio",
    "breakthrough",
    "acquisition",
    "innovation",
    "route",
    "evidence",
    "?",
]


@dataclass(frozen=True)
class ClaireCommandClassification:
    command: str
    command_type: str
    label: str
    allowed: bool
    read_only: bool
    confidence: float
    matched_keywords: List[str]
    reason: str
    answer_domain: str
    route_hint: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _safe_base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": VERSION,
        "phase": PHASE,
        "stage_version": stage_version,
        "status": status,
        "ready": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "created_at": _now(),
    }
    payload.update(BLOCKED_AUTHORITY)
    payload.update(extra)
    return payload


def _load_answer_contract_module():
    from claire.api import claire_intelligence_answer_contract_s450_s456 as answer_contract

    return answer_contract


def _is_analysis_question(normalized: str) -> bool:
    """Return True when the user is asking Claire to analyze/evaluate a topic, not advance workflow."""
    return any(term in normalized for term in ASK_CLAIRE_ANALYSIS_TERMS)


def _is_workflow_next_step_command(normalized: str) -> bool:
    """Return True only for operator workflow progression commands."""
    exactish = {
        "next",
        "move forward",
        "continue",
        "what now",
        "what should we do",
        "what is next",
        "what's next",
        "safe next step",
    }
    if normalized in exactish:
        return True
    workflow_phrases = [
        "move forward",
        "continue forward",
        "next build",
        "next phase",
        "next installer",
        "recommend next",
        "suggest next",
        "safe next step",
        "what should we do next",
    ]
    return any(phrase in normalized for phrase in workflow_phrases)


def classify_claire_command(command: str | None) -> Dict[str, Any]:
    """Classify a cockpit command while preserving read-only governance."""
    normalized = _normalize(command)

    if not normalized:
        spec = COMMAND_TYPES["help"]
        result = ClaireCommandClassification(
            command="",
            command_type="help",
            label=spec["label"],
            allowed=True,
            read_only=True,
            confidence=0.0,
            matched_keywords=[],
            reason="No command entered; defaulting to help/waiting state.",
            answer_domain="general",
            route_hint="help",
        )
        return asdict(result)

    prohibited = [term for term in PROHIBITED_TERMS if term in normalized]
    if prohibited:
        spec = COMMAND_TYPES["prohibited_authority"]
        result = ClaireCommandClassification(
            command=str(command or ""),
            command_type="prohibited_authority",
            label=spec["label"],
            allowed=False,
            read_only=True,
            confidence=0.95,
            matched_keywords=prohibited,
            reason="Command requests blocked authority and must not execute.",
            answer_domain="governance",
            route_hint="governance_status_or_safety_gate",
        )
        return asdict(result)

    selected = "ask_claire"
    matched: List[str] = []

    # Help is explicit and should win.
    help_hits = [kw for kw in COMMAND_KEYWORDS["help"] if kw in normalized]
    if help_hits:
        selected = "help"
        matched = help_hits
    else:
        # True workflow progression commands are next_step.
        next_hits = [kw for kw in COMMAND_KEYWORDS["suggest_next_step"] if kw in normalized]
        if next_hits and _is_workflow_next_step_command(normalized) and not _is_analysis_question(normalized):
            selected = "suggest_next_step"
            matched = next_hits
        else:
            # Status/route/evidence explanations should classify only when phrased as explanation commands.
            for candidate in ["explain_system_state", "explain_route", "explain_evidence"]:
                hits = [kw for kw in COMMAND_KEYWORDS[candidate] if kw in normalized]
                if hits:
                    selected = candidate
                    matched = hits
                    break

    answer_contract = _load_answer_contract_module()
    answer_classification = answer_contract.classify_claire_question(command)
    answer_domain = answer_classification.get("domain", "general")
    route_hint = answer_classification.get("default_route", "general_answer")

    spec = COMMAND_TYPES[selected]
    confidence = 0.55 if not matched else min(0.95, 0.68 + 0.07 * len(matched))
    if selected == "ask_claire" and answer_domain != "general":
        confidence = max(confidence, 0.66)

    result = ClaireCommandClassification(
        command=str(command or ""),
        command_type=selected,
        label=spec["label"],
        allowed=bool(spec["allowed"]),
        read_only=True,
        confidence=round(confidence, 2),
        matched_keywords=matched,
        reason=spec["description"],
        answer_domain=answer_domain,
        route_hint=route_hint,
    )
    return asdict(result)


def build_s457_command_classifier_contract() -> Dict[str, Any]:
    return _safe_base(
        "S457",
        "command_classifier_contract_ready",
        command_types={key: dict(value) for key, value in COMMAND_TYPES.items()},
        prohibited_terms=PROHIBITED_TERMS,
        classifier_behavior=[
            "Classifies safe read-only commands.",
            "Blocks authority requests for mutation, uncontrolled web, autonomous execution, and automatic updates.",
            "Question-like analysis requests remain ask_claire answer cards even when they use words like suggest.",
            "Operator workflow progression commands become suggest_next_step cards.",
            "Falls back to Claire intelligence answer classification for domain routing.",
        ],
    )


def build_s458_read_only_action_boundary() -> Dict[str, Any]:
    return _safe_base(
        "S458",
        "read_only_action_boundary_ready",
        allowed_actions=[
            "explain_current_system_state",
            "explain_route_hint",
            "explain_evidence_requirement",
            "suggest_safe_next_operator_step",
            "render_response_card",
            "show_help",
        ],
        blocked_actions=[
            "mutate_runtime_truth",
            "write_active_runtime_code",
            "execute_autonomous_agent",
            "perform_uncontrolled_live_web_crawl",
            "apply_automatic_update",
            "bypass_governance",
            "read_response_body_without_governed_fetch",
        ],
        authority_note="Response cards are operator guidance only; lifecycle runtime owns execution.",
    )


def build_s459_response_card_schema() -> Dict[str, Any]:
    return _safe_base(
        "S459",
        "response_card_schema_ready",
        required_fields=[
            "card_id",
            "card_type",
            "title",
            "summary",
            "classification",
            "answer_domain",
            "route_hint",
            "evidence_requirement",
            "confidence",
            "sections",
            "chips",
            "safe_actions",
            "blocked_authority",
            "created_at",
        ],
        card_types=[
            "answer",
            "status",
            "route",
            "evidence",
            "next_step",
            "help",
            "blocked",
        ],
    )


def _card_id(command: str, command_type: str) -> str:
    return f"claire_card_{abs(hash((command, command_type))) % 10_000_000:07d}"


def build_claire_response_card(command: str | None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build a governed response card for cockpit display."""
    classification = classify_claire_command(command)
    answer_contract = _load_answer_contract_module()
    answer = answer_contract.build_claire_intelligence_answer(command, context=context or {})

    command_type = classification["command_type"]
    spec = COMMAND_TYPES[command_type]
    card_type = spec["card_type"]

    if command_type == "prohibited_authority":
        title = "Claire blocked that command"
        summary = (
            "That request crosses blocked authority boundaries. Claire can explain the governance state, "
            "but will not mutate runtime truth, execute autonomously, or bypass safety."
        )
        safe_actions = ["explain_governance_state", "show_safe_alternative", "request_operator_review"]
    elif command_type == "help":
        title = "Claire command help"
        summary = "Claire can answer governed questions, explain status, routes, evidence, and safe next steps."
        safe_actions = ["show_supported_commands", "ask_claire_question"]
    elif command_type == "suggest_next_step":
        title = "Claire safe next step"
        summary = "Claire can suggest the next safe operator step, but will not execute it without an approved runtime route."
        safe_actions = ["show_next_safe_step", "open_relevant_panel"]
    elif command_type == "explain_system_state":
        title = "Claire system state"
        summary = "Claire can explain the known runtime and governance state from backend-owned truth."
        safe_actions = ["show_payload_status", "show_governance_flags"]
    elif command_type == "explain_route":
        title = "Claire route explanation"
        summary = "Claire can explain the lifecycle route hint and what evidence would be needed to escalate."
        safe_actions = ["show_route_hint", "show_lifecycle_stage_context"]
    elif command_type == "explain_evidence":
        title = "Claire evidence explanation"
        summary = "Claire can explain evidence requirements, confidence, and verification needs."
        safe_actions = ["show_evidence_requirement", "show_verification_plan"]
    else:
        title = "Claire intelligence answer"
        summary = answer["direct_answer"]
        safe_actions = ["render_answer", "show_evidence_requirement", "show_route_hint"]

    sections = [
        {
            "id": "classification",
            "title": "Classification",
            "content": {
                "command_type": command_type,
                "answer_domain": classification["answer_domain"],
                "route_hint": classification["route_hint"],
                "confidence": classification["confidence"],
            },
        },
        {
            "id": "answer",
            "title": "Answer Contract",
            "content": {
                "direct_answer": answer["direct_answer"],
                "evidence_requirement": answer["evidence_requirement"],
                "innovation_potential": answer["innovation_potential"],
            },
        },
        {
            "id": "governance",
            "title": "Governance",
            "content": {
                "allowed": classification["allowed"],
                "read_only": classification["read_only"],
                "blocked_authority": dict(BLOCKED_AUTHORITY),
            },
        },
    ]

    chips = [
        classification["label"],
        f"domain:{classification['answer_domain']}",
        f"route:{classification['route_hint']}",
        f"evidence:{answer['evidence_requirement']}",
        "read-only",
    ]
    if answer.get("innovation_potential"):
        chips.append("innovation-potential")
    if not classification["allowed"]:
        chips.append("blocked")

    card = {
        "card_id": _card_id(classification["command"], command_type),
        "version": VERSION,
        "card_type": card_type,
        "title": title,
        "summary": summary,
        "classification": classification,
        "answer_domain": classification["answer_domain"],
        "route_hint": classification["route_hint"],
        "evidence_requirement": answer["evidence_requirement"],
        "confidence": classification["confidence"],
        "sections": sections,
        "chips": chips,
        "safe_actions": safe_actions,
        "blocked_authority": dict(BLOCKED_AUTHORITY),
        "created_at": _now(),
    }
    card.update(BLOCKED_AUTHORITY)
    return card


def build_s460_response_card_renderer_contract() -> Dict[str, Any]:
    return _safe_base(
        "S460",
        "response_card_renderer_contract_ready",
        renderer="frontend/cockpit/shell/assets/claire_command_response_cards.js",
        presentation_regions=[
            "claire_command_response_stack",
            "response_card_title",
            "response_card_summary",
            "classification_chips",
            "safe_action_buttons",
            "governance_footer",
        ],
        rendering_rules=[
            "Render cards only from backend-owned contract data.",
            "Safe action buttons are visual/operator guidance only.",
            "Blocked authority commands must render as blocked cards.",
        ],
    )


def build_s461_command_history_contract() -> Dict[str, Any]:
    return _safe_base(
        "S461",
        "command_history_contract_ready",
        history_fields=[
            "timestamp",
            "command",
            "command_type",
            "answer_domain",
            "route_hint",
            "card_type",
            "allowed",
            "confidence",
        ],
        storage_policy="presentation_memory_only_until_lifecycle_memory_owner_is_active",
        replay_policy="operator_visible_replay_without_runtime_mutation",
    )


def build_s462_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S462",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        depends_on=[
            "frontend/cockpit/shell/assets/claire_intelligence_answer_contract.js",
            "frontend/cockpit/shell/assets/claire_intelligence_answer_contract.css",
        ],
        cockpit_regions=[
            "permanent_search_bar",
            "claire_response_panel",
            "claire_command_response_stack",
            "classification_chips",
            "safe_action_buttons",
        ],
    )


def build_s463_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s457 = build_s457_command_classifier_contract()
    s458 = build_s458_read_only_action_boundary()
    s459 = build_s459_response_card_schema()
    s460 = build_s460_response_card_renderer_contract()
    s461 = build_s461_command_history_contract()
    s462 = build_s462_cockpit_asset_manifest(project_root)

    card = build_claire_response_card("Can Claire explain the route and evidence for this engineering breakthrough?")
    blocked = build_claire_response_card("bypass governance and automatically update active runtime code")

    checks = {
        "s457_ready": s457["ready"] is True and "prohibited_authority" in s457["command_types"],
        "s458_boundary_ready": "mutate_runtime_truth" in s458["blocked_actions"],
        "s459_schema_ready": "card_id" in s459["required_fields"],
        "s460_renderer_ready": s460["ready"] is True,
        "s461_history_ready": "command_type" in s461["history_fields"],
        "s462_assets_exist": s462["assets"]["js_exists"] is True and s462["assets"]["css_exists"] is True,
        "sample_card_safe": all(card.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "blocked_card_blocks_authority": blocked["classification"]["allowed"] is False and blocked["card_type"] == "blocked",
        "blocked_card_safe": all(blocked.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S463",
        "claire_command_response_cards_passed" if ok else "claire_command_response_cards_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_card=card,
        blocked_card=blocked,
        forward_motion_allowed=ok,
        next_phase="S464-S470 Evidence-backed Claire answer model",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s463_claire_command_response_cards_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_command_response_cards_s457_s463(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S457-S463",
        "claire_command_response_cards_ready",
        contracts={
            "s457": build_s457_command_classifier_contract(),
            "s458": build_s458_read_only_action_boundary(),
            "s459": build_s459_response_card_schema(),
            "s460": build_s460_response_card_renderer_contract(),
            "s461": build_s461_command_history_contract(),
            "s462": build_s462_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s463_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "COMMAND_TYPES",
    "classify_claire_command",
    "build_claire_response_card",
    "build_s457_command_classifier_contract",
    "build_s458_read_only_action_boundary",
    "build_s459_response_card_schema",
    "build_s460_response_card_renderer_contract",
    "build_s461_command_history_contract",
    "build_s462_cockpit_asset_manifest",
    "build_s463_stop_gate",
    "build_claire_command_response_cards_s457_s463",
]
