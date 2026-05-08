(function () {
  "use strict";

  const MEMORY_PATHS = [
    "verified_memory_status.json",
    "./verified_memory_status.json",
    "/src/frontend/command_center/modern/verified_memory_status.json",
    "/exports/latest/verified_memory_gate_report.json",
    "../../../exports/latest/verified_memory_gate_report.json",
    "exports/latest/verified_memory_gate_report.json"
  ];

  const FEEDBACK_PATHS = [
    "recursive_feedback_status.json",
    "./recursive_feedback_status.json",
    "/src/frontend/command_center/modern/recursive_feedback_status.json",
    "/exports/latest/recursive_feedback_gate_report.json",
    "../../../exports/latest/recursive_feedback_gate_report.json",
    "exports/latest/recursive_feedback_gate_report.json"
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
        if (response.ok) return await response.json();
      } catch (_) {}
    }
    return null;
  }

  function ensureStyles() {
    if (document.getElementById("claire-verified-memory-style")) return;
    const style = document.createElement("style");
    style.id = "claire-verified-memory-style";
    style.textContent = `
      .claire-memory-panel {
        margin: 18px 0;
        padding: 18px;
        border: 1px solid rgba(168, 85, 247, 0.28);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(10, 8, 24, 0.96), rgba(19, 15, 36, 0.94));
        color: #e2e8f0;
        box-shadow: 0 0 28px rgba(168, 85, 247, 0.08);
      }
      .claire-memory-panel * { box-sizing: border-box; white-space: normal; overflow-wrap: anywhere; }
      .claire-memory-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; margin-bottom: 14px; }
      .claire-memory-title {
        font-family: Orbitron, Inter, system-ui, sans-serif;
        color: #c084fc;
        font-size: 13px;
        letter-spacing: .16em;
        text-transform: uppercase;
        font-weight: 800;
      }
      .claire-memory-subtitle { color: #94a3b8; font-size: 12px; line-height: 1.5; margin-top: 4px; }
      .claire-memory-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 92px;
        padding: 7px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .claire-memory-eligible, .claire-memory-allowed { color: #22c55e; border: 1px solid rgba(34,197,94,.45); background: rgba(34,197,94,.08); }
      .claire-memory-blocked, .claire-memory-not_generated { color: #f59e0b; border: 1px solid rgba(245,158,11,.45); background: rgba(245,158,11,.08); }
      .claire-memory-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 10px; margin: 14px 0; }
      .claire-memory-metric { border: 1px solid rgba(148, 163, 184, .16); border-radius: 14px; padding: 12px; background: rgba(15, 23, 42, .48); }
      .claire-memory-label { color: #94a3b8; font-size: 10px; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 5px; }
      .claire-memory-value { color: #f8fafc; font-weight: 800; font-size: 14px; line-height: 1.35; }
      .claire-memory-reasons { display: grid; gap: 8px; margin-top: 12px; }
      .claire-memory-reason { border: 1px solid rgba(148, 163, 184, .14); border-radius: 12px; padding: 10px; background: rgba(2, 6, 23, .32); color: #cbd5e1; font-size: 12px; line-height: 1.5; }
    `;
    document.head.appendChild(style);
  }

  function findMount() {
    const ids = [
      "memory",
      "memory-surface",
      "surface-memory",
      "claire-memory-surface",
      "main-workspace",
      "workspace",
      "app"
    ];
    for (const id of ids) {
      const node = document.getElementById(id);
      if (node) return node;
    }
    return document.querySelector("main") || document.body;
  }

  function classFor(status) {
    const normalized = String(status || "not_generated").toLowerCase().replace(/\s+/g, "_");
    return `claire-memory-${normalized}`;
  }

  function metric(label, value) {
    return `
      <div class="claire-memory-metric">
        <div class="claire-memory-label">${escapeHtml(label)}</div>
        <div class="claire-memory-value">${escapeHtml(value)}</div>
      </div>
    `;
  }

  function render(memory, feedback) {
    ensureStyles();

    let panel = document.getElementById("claire-verified-memory-panel");
    if (!panel) {
      panel = document.createElement("section");
      panel.id = "claire-verified-memory-panel";
      panel.className = "claire-memory-panel";
      findMount().appendChild(panel);
    }

    const memoryStatus = memory?.memory_status || "not_generated";
    const feedbackStatus = feedback?.feedback_status || "not_generated";
    const reasons = [
      ...(Array.isArray(memory?.memory_reasons) ? memory.memory_reasons : []),
      ...(Array.isArray(feedback?.feedback_reasons) ? feedback.feedback_reasons : [])
    ];
    const reasonHtml = reasons.length
      ? reasons.slice(0, 8).map((reason) => `<div class="claire-memory-reason">${escapeHtml(reason)}</div>`).join("")
      : `<div class="claire-memory-reason">No verified memory report has been generated yet. Run python tools/claire_build_verified_memory.py after validation.</div>`;

    panel.innerHTML = `
      <div class="claire-memory-header">
        <div>
          <div class="claire-memory-title">Verified Memory + Recursive Feedback Gate</div>
          <div class="claire-memory-subtitle">
            Shows whether a validated Claire output may enter verified memory and whether recursive feedback is allowed.
          </div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
          <span class="claire-memory-pill ${classFor(memoryStatus)}">${escapeHtml(memoryStatus)}</span>
          <span class="claire-memory-pill ${classFor(feedbackStatus)}">${escapeHtml(feedbackStatus)}</span>
        </div>
      </div>

      <div class="claire-memory-grid">
        ${metric("Run", memory?.run_id || feedback?.run_id || "unknown")}
        ${metric("Route", memory?.route_selected || feedback?.route_selected || "unknown")}
        ${metric("Terminal", memory?.terminal_state || feedback?.terminal_state || "missing")}
        ${metric("Validation", memory?.validation_passed ? "passed" : "not passed")}
        ${metric("Evidence", memory?.evidence_count ?? 0)}
        ${metric("Memory", memory?.memory_eligible ? "eligible" : "blocked")}
        ${metric("Recursion", feedback?.recursive_feedback_allowed ? "allowed" : "blocked")}
        ${metric("Storage", memory?.storage_mode || "gated report only")}
      </div>

      <div class="claire-memory-reasons">
        ${reasonHtml}
      </div>
    `;
  }

  async function boot() {
    const [memory, feedback] = await Promise.all([
      fetchFirstJson(MEMORY_PATHS),
      fetchFirstJson(FEEDBACK_PATHS)
    ]);

    render(memory || {
      memory_status: "not_generated",
      memory_eligible: false,
      memory_reasons: ["Run tools/claire_build_verified_memory.py after runtime truth and validation authority reports exist."]
    }, feedback || {
      feedback_status: "not_generated",
      recursive_feedback_allowed: false,
      feedback_reasons: ["Recursive feedback is blocked until verified memory eligibility passes."]
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
