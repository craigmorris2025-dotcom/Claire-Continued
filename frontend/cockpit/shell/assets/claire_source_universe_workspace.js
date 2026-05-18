/*
Claire Syntalion v19.82B.10
Source Universe Cockpit Workspace

Presentation-only cockpit layer.
No frontend-owned runtime truth.
No fake source results.
No fake discoveries.
No route scoring.
No lifecycle fabrication.

This workspace reads backend truth from:
- GET /universes
- GET /universes/{universe_id}
- POST /universes/{universe_id}/probe

If backend routes are unavailable, the cockpit displays unavailable/blocked states.
*/

(function () {
  "use strict";

  const CLAIRE_SOURCE_UNIVERSE_BUILD = "v19.82B.10";

  const STATE = {
    universes: [],
    selectedUniverseId: null,
    selectedUniverse: null,
    lastProbe: null,
    lastError: null,
    loading: false,
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function safeText(value, fallback) {
    if (value === null || value === undefined || value === "") {
      return fallback || "Unavailable";
    }
    return String(value);
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function nowIso() {
    return new Date().toISOString();
  }

  async function requestJson(url, options) {
    const response = await fetch(url, Object.assign({
      headers: { "Content-Type": "application/json" },
      cache: "no-store"
    }, options || {}));

    let payload = null;
    try {
      payload = await response.json();
    } catch (err) {
      payload = { error: "non_json_response", detail: String(err) };
    }

    if (!response.ok) {
      const message = payload && (payload.detail || payload.error || payload.message);
      throw new Error(message || ("HTTP " + response.status));
    }

    return payload;
  }

  function normalizeUniverses(payload) {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.universes)) return payload.universes;
    if (payload && Array.isArray(payload.source_universes)) return payload.source_universes;
    if (payload && payload.data && Array.isArray(payload.data.universes)) return payload.data.universes;
    return [];
  }

  function universeId(universe) {
    return universe.universe_id || universe.id || universe.key || universe.name || "unknown";
  }

  function universeName(universe) {
    return universe.display_name || universe.title || universe.name || universeId(universe);
  }

  function universePurpose(universe) {
    return universe.purpose || universe.description || universe.summary || "Backend-owned source universe. Awaiting richer runtime metadata.";
  }

  function universeStatus(universe) {
    return universe.status || universe.state || universe.availability || "registered";
  }

  function universeGovernance(universe) {
    return universe.governance_state || universe.governance || universe.policy_state || "governed";
  }

  function ensureWorkspace() {
    if (!document.body) return null;

    let existing = byId("claire-source-universe-workspace");
    if (existing) return existing;

    const section = document.createElement("section");
    section.id = "claire-source-universe-workspace";
    section.className = "claire-source-universe-workspace";
    section.setAttribute("data-build", CLAIRE_SOURCE_UNIVERSE_BUILD);
    section.innerHTML = `
      <div class="claire-su-header">
        <div>
          <p class="claire-su-kicker">Source Universe Workspace</p>
          <h2>Governed source universe control</h2>
          <p class="claire-su-subtitle">
            Select source universes, inspect backend-owned source scope, and launch governed probes without creating frontend truth.
          </p>
        </div>
        <div class="claire-su-actions">
          <button type="button" id="claire-su-refresh" class="claire-su-button">Refresh Universes</button>
          <button type="button" id="claire-su-probe" class="claire-su-button claire-su-button-primary" disabled>Governed Probe</button>
        </div>
      </div>

      <div class="claire-su-grid">
        <aside class="claire-su-card claire-su-list-card">
          <div class="claire-su-card-title">Registered Universes</div>
          <div id="claire-su-list" class="claire-su-list">
            <div class="claire-su-empty">Loading source universes from backend truth...</div>
          </div>
        </aside>

        <article class="claire-su-card claire-su-detail-card">
          <div class="claire-su-card-title">Universe Detail</div>
          <div id="claire-su-detail" class="claire-su-detail">
            <div class="claire-su-empty">Select a source universe to inspect scope, governance, and probe readiness.</div>
          </div>
        </article>

        <article class="claire-su-card claire-su-probe-card">
          <div class="claire-su-card-title">Governed Probe Result</div>
          <div id="claire-su-probe-result" class="claire-su-probe-result">
            <div class="claire-su-empty">No probe has been executed from this cockpit session.</div>
          </div>
        </article>
      </div>

      <div class="claire-su-lockline">
        Backend owns source truth. Cockpit displays only. Operator review remains required before promotion.
      </div>
    `;

    const anchor =
      byId("claire-enterprise-runtime-grid") ||
      byId("claire-cockpit-main") ||
      document.querySelector("main") ||
      document.body;

    anchor.appendChild(section);

    byId("claire-su-refresh").addEventListener("click", loadUniverses);
    byId("claire-su-probe").addEventListener("click", probeSelectedUniverse);

    return section;
  }

  function renderList() {
    const list = byId("claire-su-list");
    if (!list) return;

    const universes = asArray(STATE.universes);

    if (STATE.loading) {
      list.innerHTML = `<div class="claire-su-empty">Loading source universes from backend truth...</div>`;
      return;
    }

    if (STATE.lastError && universes.length === 0) {
      list.innerHTML = `
        <div class="claire-su-warning">
          Source universe backend unavailable.
          <span>${safeText(STATE.lastError)}</span>
        </div>
      `;
      return;
    }

    if (universes.length === 0) {
      list.innerHTML = `<div class="claire-su-empty">No backend source universes returned.</div>`;
      return;
    }

    list.innerHTML = universes.map((universe) => {
      const id = universeId(universe);
      const active = id === STATE.selectedUniverseId ? " active" : "";
      return `
        <button type="button" class="claire-su-list-item${active}" data-universe-id="${escapeHtml(id)}">
          <span class="claire-su-list-name">${escapeHtml(universeName(universe))}</span>
          <span class="claire-su-list-meta">${escapeHtml(universeStatus(universe))} · ${escapeHtml(universeGovernance(universe))}</span>
        </button>
      `;
    }).join("");

    list.querySelectorAll("[data-universe-id]").forEach((button) => {
      button.addEventListener("click", () => selectUniverse(button.getAttribute("data-universe-id")));
    });
  }

  function renderDetail() {
    const detail = byId("claire-su-detail");
    const probeButton = byId("claire-su-probe");
    if (!detail) return;

    const universe = STATE.selectedUniverse;
    if (!universe) {
      detail.innerHTML = `<div class="claire-su-empty">Select a source universe to inspect scope, governance, and probe readiness.</div>`;
      if (probeButton) probeButton.disabled = true;
      return;
    }

    if (probeButton) probeButton.disabled = false;

    const id = universeId(universe);
    const sourceTypes = asArray(universe.source_types || universe.sources || universe.provider_types);
    const allowedActions = asArray(universe.allowed_actions || universe.actions || universe.capabilities);
    const blockedActions = asArray(universe.blocked_actions || universe.disallowed_actions || universe.restrictions);
    const evidencePolicy = universe.evidence_policy || universe.policy || {};

    detail.innerHTML = `
      <div class="claire-su-detail-heading">
        <h3>${escapeHtml(universeName(universe))}</h3>
        <span>${escapeHtml(id)}</span>
      </div>
      <p class="claire-su-purpose">${escapeHtml(universePurpose(universe))}</p>

      <div class="claire-su-metrics">
        <div><span>Status</span><strong>${escapeHtml(universeStatus(universe))}</strong></div>
        <div><span>Governance</span><strong>${escapeHtml(universeGovernance(universe))}</strong></div>
        <div><span>Source Types</span><strong>${sourceTypes.length}</strong></div>
        <div><span>Allowed Actions</span><strong>${allowedActions.length}</strong></div>
      </div>

      <div class="claire-su-section">
        <h4>Source Types</h4>
        ${renderPills(sourceTypes, "Backend has not exposed source type detail yet.")}
      </div>

      <div class="claire-su-section">
        <h4>Allowed Operator Actions</h4>
        ${renderPills(allowedActions, "No allowed actions exposed by backend.")}
      </div>

      <div class="claire-su-section">
        <h4>Blocked / Governed Actions</h4>
        ${renderPills(blockedActions, "No blocked action list exposed by backend.")}
      </div>

      <div class="claire-su-section">
        <h4>Evidence Policy</h4>
        <pre>${escapeHtml(JSON.stringify(evidencePolicy, null, 2))}</pre>
      </div>
    `;
  }

  function renderProbe() {
    const container = byId("claire-su-probe-result");
    if (!container) return;

    const probe = STATE.lastProbe;

    if (!probe) {
      container.innerHTML = `<div class="claire-su-empty">No probe has been executed from this cockpit session.</div>`;
      return;
    }

    const universe = safeText(probe.universe_id || probe.id || STATE.selectedUniverseId, "Unknown universe");
    const status = safeText(probe.status || probe.state || probe.result_state, "returned");
    const candidates = asArray(probe.candidates || probe.results || probe.items);
    const blocked = probe.blocked === true || status.toLowerCase().includes("blocked");

    container.innerHTML = `
      <div class="${blocked ? "claire-su-warning" : "claire-su-success"}">
        Probe ${escapeHtml(status)} for ${escapeHtml(universe)}
        <span>${escapeHtml(probe.timestamp || probe.created_at || nowIso())}</span>
      </div>

      <div class="claire-su-section">
        <h4>Returned Candidate Count</h4>
        <div class="claire-su-large-number">${candidates.length}</div>
      </div>

      <div class="claire-su-section">
        <h4>Backend Probe Payload</h4>
        <pre>${escapeHtml(JSON.stringify(probe, null, 2))}</pre>
      </div>
    `;
  }

  function renderPills(items, emptyText) {
    const arr = asArray(items);
    if (arr.length === 0) {
      return `<div class="claire-su-muted">${escapeHtml(emptyText)}</div>`;
    }
    return `<div class="claire-su-pills">${arr.map((item) => `<span>${escapeHtml(String(item))}</span>`).join("")}</div>`;
  }

  function renderAll() {
    ensureWorkspace();
    renderList();
    renderDetail();
    renderProbe();
  }

  async function loadUniverses() {
    ensureWorkspace();
    STATE.loading = true;
    STATE.lastError = null;
    renderAll();

    try {
      const payload = await requestJson("/universes");
      STATE.universes = normalizeUniverses(payload);

      if (!STATE.selectedUniverseId && STATE.universes.length > 0) {
        STATE.selectedUniverseId = universeId(STATE.universes[0]);
      }

      const selected = STATE.universes.find((u) => universeId(u) === STATE.selectedUniverseId);
      STATE.selectedUniverse = selected || null;

      if (STATE.selectedUniverseId) {
        await loadUniverseDetail(STATE.selectedUniverseId, false);
      }
    } catch (err) {
      STATE.lastError = String(err && err.message ? err.message : err);
      STATE.universes = [];
      STATE.selectedUniverse = null;
    } finally {
      STATE.loading = false;
      renderAll();
    }
  }

  async function loadUniverseDetail(universeIdValue, rerender) {
    if (!universeIdValue) return;
    try {
      const payload = await requestJson("/universes/" + encodeURIComponent(universeIdValue));
      STATE.selectedUniverse = payload && (payload.universe || payload.source_universe || payload);
      STATE.lastError = null;
    } catch (err) {
      const fallback = STATE.universes.find((u) => universeId(u) === universeIdValue);
      STATE.selectedUniverse = fallback || null;
      STATE.lastError = String(err && err.message ? err.message : err);
    }
    if (rerender !== false) renderAll();
  }

  async function selectUniverse(universeIdValue) {
    STATE.selectedUniverseId = universeIdValue;
    STATE.lastProbe = null;
    await loadUniverseDetail(universeIdValue, true);
  }

  async function probeSelectedUniverse() {
    const id = STATE.selectedUniverseId;
    if (!id) return;

    const button = byId("claire-su-probe");
    if (button) {
      button.disabled = true;
      button.textContent = "Probing...";
    }

    try {
      const payload = await requestJson("/universes/" + encodeURIComponent(id) + "/probe", {
        method: "POST",
        body: JSON.stringify({
          requested_by: "operator_cockpit",
          build: CLAIRE_SOURCE_UNIVERSE_BUILD,
          mode: "governed_probe",
          frontend_truth_mutation: false,
          requested_at: nowIso()
        })
      });
      STATE.lastProbe = payload;
      STATE.lastError = null;
    } catch (err) {
      STATE.lastProbe = {
        universe_id: id,
        status: "blocked_or_unavailable",
        blocked: true,
        error: String(err && err.message ? err.message : err),
        timestamp: nowIso()
      };
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = "Governed Probe";
      }
      renderAll();
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  window.ClaireSourceUniverseWorkspace = {
    version: CLAIRE_SOURCE_UNIVERSE_BUILD,
    loadUniverses,
    selectUniverse,
    probeSelectedUniverse,
    state: STATE
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadUniverses);
  } else {
    loadUniverses();
  }
})();
