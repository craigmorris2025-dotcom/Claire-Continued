from __future__ import annotations

from typing import Any

from claire.api.s51_route_specific_useful_outputs import build_all_route_output_previews
from claire.api.s52_useful_output_quality_gate import build_s52r1_r8_plateau_report


S53_VERSION = "v19.89.8-S53R1-R8"


def _base_authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "response_mode": "read_only_artifact",
    }


def build_cockpit_useful_output_browser() -> dict[str, Any]:
    s52 = build_s52r1_r8_plateau_report()
    previews = build_all_route_output_previews()["previews"]

    browser_cards = []
    for preview in previews:
        browser_cards.append({
            "card_id": f"s53-card-{preview['route_id']}",
            "route_id": preview["route_id"],
            "surface_id": preview["surface_id"],
            "title": preview["title"],
            "headline": preview["headline"],
            "summary": preview["summary"],
            "terminal_state": preview["terminal_state"],
            "section_count": preview["section_count"],
            "confidence": preview["confidence"],
            "evidence_state": preview["evidence_state"],
            "review_state": preview["review_state"],
            "display_mode": "useful_output_card",
            "visible_to_operator": True,
            "exportable": True,
            **_base_authority(),
        })

    return {
        "version": S53_VERSION,
        "phase": "S53R1-R4",
        "status": "cockpit_useful_output_browser_ready",
        "source_s52_status": s52["status"],
        "card_count": len(browser_cards),
        "cards": browser_cards,
        **_base_authority(),
        "next_phase": "S53R5-R8 output export registry and plateau",
    }


def build_output_export_registry() -> dict[str, Any]:
    browser = build_cockpit_useful_output_browser()
    export_items = []
    for card in browser["cards"]:
        export_items.append({
            "export_id": f"export-{card['route_id']}",
            "route_id": card["route_id"],
            "card_id": card["card_id"],
            "allowed_formats": ["json", "markdown"],
            "export_state": "available_for_operator_review",
            "requires_manual_review": True,
            "runtime_truth_write_allowed": False,
            "auto_export_enabled": False,
            "auto_promotion_enabled": False,
            **_base_authority(),
        })

    return {
        "version": S53_VERSION,
        "phase": "S53R5-R6",
        "status": "output_export_registry_ready",
        "export_count": len(export_items),
        "exports": export_items,
        **_base_authority(),
    }


def verify_cockpit_useful_output_browser() -> dict[str, Any]:
    browser = build_cockpit_useful_output_browser()
    registry = build_output_export_registry()
    failures: list[str] = []

    if browser["card_count"] != 7:
        failures.append("browser card count mismatch")
    if registry["export_count"] != 7:
        failures.append("export count mismatch")

    seen_cards: set[str] = set()
    for card in browser["cards"]:
        if card["card_id"] in seen_cards:
            failures.append(f"duplicate card {card['card_id']}")
        seen_cards.add(card["card_id"])
        if not card["visible_to_operator"]:
            failures.append(f"{card['card_id']} not visible")
        if card["runtime_truth_mutation_allowed"]:
            failures.append(f"{card['card_id']} runtime truth mutation allowed")
        if card["operator_mutation_enabled"]:
            failures.append(f"{card['card_id']} operator mutation enabled")
        if card["section_count"] <= 0:
            failures.append(f"{card['card_id']} missing sections")

    for export in registry["exports"]:
        if export["runtime_truth_write_allowed"]:
            failures.append(f"{export['export_id']} runtime truth write allowed")
        if export["auto_export_enabled"]:
            failures.append(f"{export['export_id']} auto export enabled")
        if export["auto_promotion_enabled"]:
            failures.append(f"{export['export_id']} auto promotion enabled")
        if "json" not in export["allowed_formats"]:
            failures.append(f"{export['export_id']} missing json export")

    return {
        "version": S53_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "card_count": browser["card_count"],
        "export_count": registry["export_count"],
        **_base_authority(),
    }


def build_s53r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_cockpit_useful_output_browser()
    return {
        "version": S53_VERSION,
        "phase": "S53R7-R8",
        "status": "s53r1_r8_ready" if verification["verification_ok"] else "s53r1_r8_blocked",
        "ready": verification["verification_ok"],
        "browser": build_cockpit_useful_output_browser(),
        "export_registry": build_output_export_registry(),
        "verification": verification,
        **_base_authority(),
        "next_phase": "S54 useful output persistence and run history integration",
    }
