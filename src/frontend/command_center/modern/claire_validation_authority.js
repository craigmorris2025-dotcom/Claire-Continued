(function () {
  "use strict";

  const REPORT_PATHS = [
    "validation_authority_status.json",
    "./validation_authority_status.json",
    "/src/frontend/command_center/modern/validation_authority_status.json",
    "/exports/latest/validation_authority_report.json",
    "../../../exports/latest/validation_authority_report.json",
    "exports/latest/validation_authority_report.json"
  ];

  const EVIDENCE_PATHS = [
    "evidence_traceability_status.json",
    "./evidence_traceability_status.json",
    "/src/frontend/command_center/modern/evidence_traceability_status.json",
    "/exports/latest/evidence_traceability_index.json",
    "../../../exports/latest/evidence_traceability_index.json",
    "exports/latest/evidence_traceability_index.json"
  ];

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function fetchFirstJson(paths) {
    for (const path of paths) {
      try {
        const response = await fetch(path, { cache: "no-store" });
        if (response.ok) {
          return await response.json();
        }
      } catch (_) {
        // Try next path. Local/static hosting differs by launch mode.
      }
    }
    return null;
  }

  function statusClass(status) {
    const normalized = String(status || "not_generated").toLowerCase();
    if (normalized === "pass") return "claire-validation-pass";
    if (normalized === "warning") return "claire-validation-warning";
    if (normalized === "blocked") return "claire-validation-blocked";
    if (normalized === "fail") return "claire-validation-fail";
    return "claire-validation-missing";
  }

  function ensureStyles() {
    if (document.getElementById("claire-validation-authority-style")) return;

    const style = document.createElement("style");
    style.id = "claire-validation-authority-style";
    style.textContent = `
      .claire-validation-authority-panel {
        margin: 18px 0;
        padding: 18px;
        border: 1px solid rgba(0, 212, 255, 0.24);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(7, 12, 23, 0.96), rgba(12, 20, 36, 0.94));
        color: #dce8f7;
        box-shadow: 0 0 28px rgba(0, 212, 255, 0.08);
      }
      .claire-validation-authority-panel * {
        box-sizing: border-box;
        overflow-wrap: anywhere;
        white-space: normal;
      }
      .claire-validation-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 14px;
        margin-bottom: 14px;
      }
      .claire-validation-title {
        font-family: Orbitron, Inter, system-ui, sans-serif;
        color: #00d4ff;
        font-size: 13px;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-weight: 800;
      }
      .claire-validation-subtitle {
        margin-top: 4px;
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.5;
      }
      .claire-validation-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 94px;
        padding: 7px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .claire-validation-pass { color: #22c55e; border: 1px solid rgba(34,197,94,.45); background: rgba(34,197,94,.08); }
      .claire-validation-warning { color: #fbbf24; border: 1px solid rgba(251,191,36,.45); background: rgba(251,191,36,.08); }
      .claire-validation-blocked { color: #fb923c; border: 1px solid rgba(251,146,60,.45); background: rgba(251,146,60,.08); }
      .claire-validation-fail { color: #f87171; border: 1px solid rgba(248,113,113,.45); background: rgba(248,113,113,.08); }
      .claire-validation-missing { color: #94a3b8; border: 1px solid rgba(148,163,184,.35); background: rgba(148,163,184,.06); }
      .claire-validation-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        margin: 14px 0;
      }
      .claire-validation-metric {
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 14px;
        padding: 12px;
        background: rgba(15, 23, 42, 0.5);
      }
      .claire-validation-label {
        color: #94a3b8;
        font-size: 10px;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: 5px;
      }
      .claire-validation-value {
        color: #e2e8f0;
        font-weight: 800;
        font-size: 15px;
        line-height: 1.35;
      }
      .claire-validation-checks {
        display: grid;
        gap: 8px;
        margin-top: 12px;
      }
      .claire-validation-check {
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 12px;
        padding: 10px;
        background: rgba(2, 6, 23, 0.34);
      }
      .claire-validation-check-name {
        color: #e2e8f0;
        font-weight: 700;
        font-size: 12px;
        line-height: 1.45;
      }
      .claire-validation-check-details {
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 3px;
      }
      .claire-validation-empty {
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.6;
        border: 1px dashed rgba(148, 163, 184, 0.24);
        border-radius: 12px;
        padding: 12px;
        background: rgba(148, 163, 184, 0.04);
      }
    `;
    document.head.appendChild(style);
  }

  function findMount() {
    const preferredIds = [
      "validation",
      "validation-surface",
      "surface-validation",
      "claire-validation-surface",
      "main-workspace",
      "workspace",
      "app"
    ];
    for (const id of preferredIds) {
      const node = document.getElementById(id);
      if (node) return node;
    }
    return document.querySelector("main") || document.body;
  }

  function metric(label, value) {
    return `
      <div class="claire-validation-metric">
        <div class="claire-validation-label">${escapeHtml(label)}</div>
        <div class="claire-validation-value">${escapeHtml(value)}</div>
      </div>
    `;
  }

  function render(report, evidence) {
    ensureStyles();

    let panel = document.getElementById("claire-validation-authority-panel");
    if (!panel) {
      panel = document.createElement("section");
      panel.id = "claire-validation-authority-panel";
      panel.className = "claire-validation-authority-panel";
      findMount().appendChild(panel);
    }

    const status = report?.validation_authority_status || "not_generated";
    const score = report?.validation_score ?? 0;
    const checks = Array.isArray(report?.checks) ? report.checks : [];
    const visibleChecks = checks.slice(0, 7);
    const evidenceCount = evidence?.evidence_count ?? report?.evidence_summary?.evidence_count ?? 0;
    const unsupportedCount = evidence?.unsupported_count ?? report?.evidence_summary?.unsupported_count ?? 0;

    const checksHtml = visibleChecks.length
      ? visibleChecks.map((check) => `
          <div class="claire-validation-check">
            <div class="claire-validation-pill ${statusClass(check.status)}" style="margin-bottom:7px;">${escapeHtml(check.status)}</div>
            <div class="claire-validation-check-name">${escapeHtml(check.name || check.check_id)}</div>
            <div class="claire-validation-check-details">${escapeHtml(check.details || "")}</div>
          </div>
        `).join("")
      : `<div class="claire-validation-empty">No validation checks have been generated yet. Run <strong>python tools/claire_validate_runtime_truth.py</strong> after a Claire run.</div>`;

    panel.innerHTML = `
      <div class="claire-validation-header">
        <div>
          <div class="claire-validation-title">Validation Authority + Evidence Traceability</div>
          <div class="claire-validation-subtitle">
            Governed pass/fail authority for runtime truth, route integrity, evidence support, terminal state, and memory eligibility.
          </div>
        </div>
        <div class="claire-validation-pill ${statusClass(status)}">${escapeHtml(status)}</div>
      </div>

      <div class="claire-validation-grid">
        ${metric("Run", report?.run_id || "unknown")}
        ${metric("Route", report?.route_selected || "unknown")}
        ${metric("Terminal", report?.terminal_state || "missing")}
        ${metric("Score", `${score}/100`)}
        ${metric("Checks", `${report?.checks_passed ?? 0} pass / ${report?.checks_warning ?? 0} warn / ${report?.checks_failed ?? 0} fail`)}
        ${metric("Evidence", `${evidenceCount} item(s)`)}
        ${metric("Unsupported", `${unsupportedCount}`)}
        ${metric("Memory", report?.memory_eligible ? "eligible" : "blocked")}
      </div>

      <div class="claire-validation-checks">
        ${checksHtml}
      </div>
    `;
  }

  async function boot() {
    const [report, evidence] = await Promise.all([
      fetchFirstJson(REPORT_PATHS),
      fetchFirstJson(EVIDENCE_PATHS)
    ]);

    if (!report && !evidence) {
      render({
        validation_authority_status: "not_generated",
        validation_score: 0,
        run_id: "unknown",
        route_selected: "unknown",
        terminal_state: "missing",
        checks: []
      }, {
        evidence_count: 0,
        unsupported_count: 0
      });
      return;
    }

    render(report || {}, evidence || {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
