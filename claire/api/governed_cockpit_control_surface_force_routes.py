from __future__ import annotations

from fastapi import APIRouter, Response

from claire.governance.governed_cockpit_control_surface_force_mount import (
    get_cockpit_control_surface_buttons,
    get_cockpit_control_surface_payload,
    preview_operation,
)

router = APIRouter(tags=["cockpit-control-surface"])

_CONTROL_SURFACE_JS = '(function () {\n  const VERSION = "S985-S1012";\n  const PAYLOAD_URL = "/api/cockpit/control-surface/payload";\n  const FALLBACK = {\n    stage: "S985-S1012",\n    status: "fallback_control_surface_ready",\n    action_count: 16,\n    operator_message: "Visible cockpit controls are mounted from fallback payload. Execution remains blocked.",\n    buttons: [],\n    control_surface: {\n      buttons: [\n        ["run_readiness_audit", "Run readiness audit"],\n        ["inspect_providers", "Inspect providers"],\n        ["open_source_policy", "Open source policy"],\n        ["compile_search_plan", "Compile search plan"],\n        ["preview_metadata_search", "Preview metadata search"],\n        ["view_metadata_contract", "View metadata contract"],\n        ["open_quarantine_review", "Open quarantine review"],\n        ["build_evidence_cards", "Build evidence cards"],\n        ["score_source_confidence", "Score source confidence"],\n        ["show_review_actions", "Show review actions"],\n        ["build_body_read_request", "Build body-read request"],\n        ["run_body_read_preflight", "Run body-read preflight"],\n        ["draft_source_ingestion", "Draft source ingestion"],\n        ["preview_truth_promotion", "Preview truth promotion"],\n        ["verify_s900_gate", "Verify S900 gate"],\n        ["verify_button_mount", "Verify button mount"]\n      ].map(([key, label]) => ({ key, label, operation_mode: "preview_only", execution_enabled: false }))\n    },\n    blocked_flags: {\n      live_web_execution_enabled: false,\n      search_provider_execution_enabled: false,\n      browser_execution_enabled: false,\n      network_request_performed: false,\n      body_read_allowed: false,\n      autonomous_crawling_enabled: false,\n      automatic_updates_enabled: false,\n      runtime_mutation_enabled: false,\n      runtime_truth_mutation_enabled: false,\n      package_download_performed: false,\n      package_install_performed: false,\n      command_execution_enabled: false\n    }\n  };\n\n  function normalizePayload(payload) {\n    const buttons = (payload && payload.control_surface && payload.control_surface.buttons) || payload.buttons || FALLBACK.control_surface.buttons;\n    return Object.assign({}, FALLBACK, payload || {}, {\n      control_surface: Object.assign({}, FALLBACK.control_surface, (payload && payload.control_surface) || {}, { buttons })\n    });\n  }\n\n  function findCommandSurface() {\n    const input = Array.from(document.querySelectorAll(\'input, textarea\')).find((el) => {\n      const placeholder = (el.getAttribute(\'placeholder\') || \'\').toLowerCase();\n      return placeholder.includes(\'ask claire\') || placeholder.includes(\'governed web\') || placeholder.includes(\'command\');\n    });\n    if (input) {\n      return input.closest(\'section, div, main, article\') || input.parentElement;\n    }\n    const headings = Array.from(document.querySelectorAll(\'h1, h2, h3, .title\')).filter((el) => /claire operator cockpit|governed web|evidence|actions|overview/i.test(el.textContent || \'\'));\n    if (headings.length) return headings[0].parentElement || document.body;\n    return document.querySelector(\'main\') || document.body;\n  }\n\n  function updateActionsChip(count) {\n    const all = Array.from(document.querySelectorAll(\'body *\')).filter((el) => el.children.length === 0 && /^\\s*Actions\\s*:\\s*\\d+\\s*$/i.test(el.textContent || \'\'));\n    all.forEach((el) => { el.textContent = \'Actions: \' + count; el.setAttribute(\'data-claire-actions-count-forced\', String(count)); });\n  }\n\n  function replaceEmptyActionsText(count) {\n    const nodes = [];\n    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);\n    while (walker.nextNode()) nodes.push(walker.currentNode);\n    nodes.forEach((node) => {\n      if ((node.nodeValue || \'\').includes(\'No governed actions registered\')) {\n        node.nodeValue = \'Governed operation controls registered: \' + count + \'. Buttons are visible and preview-only; execution remains blocked.\';\n      }\n    });\n  }\n\n  function showPreview(key, label) {\n    const output = document.getElementById(\'claire-s985-s1012-operation-output\');\n    if (!output) return;\n    output.textContent = \'Loading preview for \' + label + \'...\';\n    fetch(\'/api/cockpit/control-surface/preview/\' + encodeURIComponent(key), { cache: \'no-store\' })\n      .then((res) => res.ok ? res.json() : Promise.reject(new Error(\'preview endpoint unavailable\')))\n      .then((payload) => {\n        output.textContent = JSON.stringify(payload, null, 2);\n      })\n      .catch(() => {\n        output.textContent = JSON.stringify({\n          operation_key: key,\n          label: label,\n          status: \'local_preview_only\',\n          execution_enabled: false,\n          network_request_performed: false,\n          body_read_performed: false,\n          runtime_mutation_performed: false,\n          command_execution_performed: false,\n          message: \'Local preview only. Execution remains blocked.\'\n        }, null, 2);\n      });\n  }\n\n  function render(payload) {\n    payload = normalizePayload(payload);\n    const buttons = payload.control_surface.buttons || [];\n    const count = payload.action_count || buttons.length || 0;\n    let root = document.getElementById(\'claire-s985-s1012-control-surface\');\n    if (!root) {\n      root = document.createElement(\'section\');\n      root.id = \'claire-s985-s1012-control-surface\';\n      root.className = \'claire-s985-s1012-control-surface\';\n      const anchor = findCommandSurface();\n      if (anchor && anchor.parentElement) {\n        anchor.insertAdjacentElement(\'afterend\', root);\n      } else {\n        document.body.insertBefore(root, document.body.firstChild);\n      }\n    }\n    root.innerHTML = \'\';\n\n    const header = document.createElement(\'div\');\n    header.className = \'claire-s985-s1012-control-header\';\n    header.innerHTML = \'<div><div class="claire-s985-s1012-eyebrow">OPERATOR CONTROL SURFACE</div><h2>Governed Operation Buttons</h2><p>Buttons are mounted for cockpit operation. All execution, body-read, runtime mutation, package install, and command authority remain blocked.</p></div><span class="claire-s985-s1012-badge">\' + count + \' preview actions</span>\';\n    root.appendChild(header);\n\n    const grid = document.createElement(\'div\');\n    grid.className = \'claire-s985-s1012-button-grid\';\n    buttons.forEach((button) => {\n      const btn = document.createElement(\'button\');\n      btn.type = \'button\';\n      btn.className = \'claire-s985-s1012-op-button\';\n      btn.setAttribute(\'data-operation-key\', button.key);\n      btn.innerHTML = \'<strong>\' + (button.label || button.key) + \'</strong><span>\' + (button.operation_mode || \'preview_only\') + \'</span>\';\n      btn.addEventListener(\'click\', () => showPreview(button.key, button.label || button.key));\n      grid.appendChild(btn);\n    });\n    root.appendChild(grid);\n\n    const out = document.createElement(\'pre\');\n    out.id = \'claire-s985-s1012-operation-output\';\n    out.className = \'claire-s985-s1012-output\';\n    out.textContent = JSON.stringify({ stage: payload.stage, status: payload.status, action_count: count, blocked_flags: payload.blocked_flags }, null, 2);\n    root.appendChild(out);\n\n    updateActionsChip(count);\n    replaceEmptyActionsText(count);\n    document.body.setAttribute(\'data-claire-s985-s1012-control-surface-mounted\', \'true\');\n  }\n\n  function mount() {\n    fetch(PAYLOAD_URL, { cache: \'no-store\' })\n      .then((res) => res.ok ? res.json() : FALLBACK)\n      .then(render)\n      .catch(() => render(FALLBACK));\n  }\n\n  if (document.readyState === \'loading\') {\n    document.addEventListener(\'DOMContentLoaded\', mount);\n  } else {\n    mount();\n  }\n  setTimeout(mount, 500);\n  setTimeout(mount, 1500);\n  setTimeout(mount, 3500);\n  try {\n    const observer = new MutationObserver(() => {\n      if (!document.getElementById(\'claire-s985-s1012-control-surface\')) mount();\n      const current = document.body.getAttribute(\'data-claire-s985-s1012-control-surface-mounted\');\n      if (current !== \'true\') mount();\n    });\n    observer.observe(document.body, { childList: true, subtree: true });\n  } catch (err) {}\n})();\n'
_CONTROL_SURFACE_CSS = '.claire-s985-s1012-control-surface {\n  margin: 24px 0;\n  padding: 22px;\n  border: 1px solid rgba(79, 183, 255, 0.35);\n  border-radius: 22px;\n  background: rgba(10, 20, 38, 0.94);\n  box-shadow: 0 0 0 1px rgba(79, 183, 255, 0.10), 0 18px 60px rgba(0, 0, 0, 0.28);\n}\n.claire-s985-s1012-control-header {\n  display: flex;\n  align-items: flex-start;\n  justify-content: space-between;\n  gap: 18px;\n  margin-bottom: 18px;\n}\n.claire-s985-s1012-eyebrow {\n  color: #66f6ff;\n  font-size: 12px;\n  letter-spacing: 0.28em;\n  margin-bottom: 8px;\n}\n.claire-s985-s1012-control-header h2 {\n  margin: 0 0 8px 0;\n  font-size: 28px;\n  color: #ffffff;\n}\n.claire-s985-s1012-control-header p {\n  margin: 0;\n  color: rgba(226, 238, 255, 0.82);\n  line-height: 1.45;\n}\n.claire-s985-s1012-badge {\n  white-space: nowrap;\n  border: 1px solid rgba(86, 255, 148, 0.45);\n  color: #56ff94;\n  border-radius: 999px;\n  padding: 9px 14px;\n  font-size: 14px;\n  background: rgba(86, 255, 148, 0.08);\n}\n.claire-s985-s1012-button-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));\n  gap: 12px;\n}\n.claire-s985-s1012-op-button {\n  text-align: left;\n  border: 1px solid rgba(79, 183, 255, 0.38);\n  border-radius: 16px;\n  background: rgba(18, 42, 68, 0.72);\n  color: #f3f8ff;\n  padding: 14px 16px;\n  cursor: pointer;\n  min-height: 78px;\n}\n.claire-s985-s1012-op-button:hover {\n  border-color: rgba(102, 246, 255, 0.76);\n  background: rgba(27, 58, 92, 0.88);\n}\n.claire-s985-s1012-op-button strong {\n  display: block;\n  font-size: 15px;\n  margin-bottom: 8px;\n}\n.claire-s985-s1012-op-button span {\n  display: inline-block;\n  font-size: 11px;\n  text-transform: uppercase;\n  letter-spacing: 0.12em;\n  color: #ffc247;\n}\n.claire-s985-s1012-output {\n  margin: 18px 0 0 0;\n  padding: 16px;\n  max-height: 240px;\n  overflow: auto;\n  border-radius: 14px;\n  border: 1px solid rgba(255, 255, 255, 0.10);\n  background: rgba(2, 8, 18, 0.68);\n  color: rgba(238, 246, 255, 0.92);\n  font-size: 12px;\n}\n@media (max-width: 900px) {\n  .claire-s985-s1012-control-header { flex-direction: column; }\n  .claire-s985-s1012-badge { white-space: normal; }\n}\n'


@router.get("/api/cockpit/control-surface/payload")
def cockpit_control_surface_payload():
    return get_cockpit_control_surface_payload()


@router.get("/api/cockpit/control-surface/buttons")
def cockpit_control_surface_buttons():
    return {"buttons": get_cockpit_control_surface_buttons(), "action_count": len(get_cockpit_control_surface_buttons())}


@router.get("/api/cockpit/control-surface/actions")
def cockpit_control_surface_actions():
    payload = get_cockpit_control_surface_payload()
    return {"actions": payload["actions"], "action_count": payload["action_count"], "execution_enabled": False}


@router.get("/api/cockpit/control-surface/status")
def cockpit_control_surface_status():
    payload = get_cockpit_control_surface_payload()
    return {
        "stage": payload["stage"],
        "status": payload["status"],
        "action_count": payload["action_count"],
        "dangerous_authority_preserved": payload["dangerous_authority_preserved"],
        "blocked_flags": payload["blocked_flags"],
    }


@router.get("/api/cockpit/control-surface/preview/{operation_key}")
def cockpit_control_surface_preview(operation_key: str):
    return preview_operation(operation_key)


@router.get("/api/cockpit/control-surface/assets/js")
def cockpit_control_surface_js_asset():
    return Response(_CONTROL_SURFACE_JS, media_type="application/javascript")


@router.get("/api/cockpit/control-surface/assets/css")
def cockpit_control_surface_css_asset():
    return Response(_CONTROL_SURFACE_CSS, media_type="text/css")


@router.get("/api/internet/control-surface/payload")
def internet_control_surface_payload():
    payload = get_cockpit_control_surface_payload()
    payload["internet_execution_enabled"] = False
    return payload


@router.get("/api/internet/s1012-stop-gate")
def internet_s1012_stop_gate():
    payload = get_cockpit_control_surface_payload()
    return {
        "stage": "S985-S1012",
        "status": "stop_gate_ready",
        "visible_controls_required": True,
        "action_count": payload["action_count"],
        "dangerous_authority_preserved": payload["dangerous_authority_preserved"],
        "blocked_flags": payload["blocked_flags"],
    }
