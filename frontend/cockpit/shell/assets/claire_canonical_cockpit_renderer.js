(function () {
  "use strict";

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value === undefined || value === null || value === "" ? "unavailable" : String(value);
  }

  function renderList(id, items, emptyText) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!items || items.length === 0) {
      el.className = "claire-list-empty";
      el.textContent = emptyText;
      return;
    }
    el.className = "claire-list";
    el.innerHTML = items.slice(0, 10).map((item) => {
      const title = item.title || item.name || item.headline || item.id || "Backend item";
      const route = item.route || item.type || item.category || item.status || "pending_review";
      return `<article class="claire-list-item"><strong>${escapeHtml(title)}</strong><span>${escapeHtml(route)}</span></article>`;
    }).join("");
  }

  async function refreshCanonicalCockpit() {
    if (!window.ClaireCanonicalPayloadAdapter) return;
    const result = await window.ClaireCanonicalPayloadAdapter.load();
    const payload = result.payload || {};
    const lifecycle = payload.lifecycle || {};
    const latest = payload.latest_run || {};
    const continuous = payload.continuous_runtime || {};
    const queue = payload.review_queue || [];
    const counts = payload.candidate_counts || {};
    const universes = payload.source_universes || [];

    setText("claire-status-payload", result.status === "available" ? "available" : "unavailable");
    setText("system-payload-state", result.status === "available" ? "available" : "unavailable");
    setText("claire-status-backend", continuous.status || result.status || "unavailable");
    setText("claire-status-run", latest.run_id || latest.id ? "active" : "none");
    setText("claire-active-run", latest.run_id || latest.id || "no active run");
    setText("claire-route-state", payload.selected_route || payload.terminal_state || "pending evidence");
    setText("claire-lifecycle-state", lifecycle.active_stage || lifecycle.current_stage || "30-stage runtime");
    setText("claire-continuous-state", continuous.status || continuous.runtime_state || "unavailable");
    setText("claire-continuous-badge", continuous.runtime_state || continuous.status || "unavailable");
    setText("system-runtime-state", continuous.runtime_state || continuous.status || "unavailable");
    setText("claire-continuous-json", JSON.stringify(continuous, null, 2));
    setText("claire-system-json", JSON.stringify({ adapter: result.adapter_build, source: result.payload_source, payload, route_truth: result.route_truth }, null, 2));

    setText("claire-review-count", queue.length);
    setText("review-workspace-count", queue.length);
    setText("claire-candidate-counts", `${counts.discovery || 0} D · ${counts.breakthrough || 0} B · ${counts.portfolio || 0} P · ${counts.design || 0} DS · ${counts.package || 0} PKG`);
    setText("intel-discovery-count", counts.discovery || 0);
    setText("intel-gap-count", counts.discovery || 0);
    setText("portfolio-count", counts.portfolio || 0);
    setText("breakthrough-count", counts.breakthrough || 0);
    setText("design-count", counts.design || 0);
    setText("source-universe-count", universes.length);

    renderList("claire-review-list", queue, "No review items exposed yet.");
    renderList("claire-discovery-list", queue.filter((item) => JSON.stringify(item).toLowerCase().includes("discovery")), "No backend discovery candidates exposed yet.");
    renderList("claire-source-list", universes, "No source universes loaded yet.");

    document.body.dataset.claireCanonicalPayloadStatus = result.status;
    document.body.dataset.claireCanonicalPayloadSource = result.payload_source || "none";
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  window.ClaireCanonicalCockpitRenderer = {
    version: "v19.83.3",
    refresh: refreshCanonicalCockpit
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", refreshCanonicalCockpit);
  } else {
    refreshCanonicalCockpit();
  }
})();
