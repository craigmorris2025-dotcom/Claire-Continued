(function () {
  "use strict";

  const BUILD = "v19.83.3";

  const ROUTES = {
    primaryPayload: "/dashboard/payload",
    fallbackPayload: "/api/dashboard/payload",
    payloadStatus: "/dashboard/payload/status",
    fallbackPayloadStatus: "/api/dashboard/payload/status",
    continuousStatus: "/runtime/continuous/status",
    reviewQueue: "/runtime/continuous/review-queue",
    universes: "/universes",
    routeTruth: "/system/cockpit-truth"
  };

  const EMPTY = {
    status: "unavailable",
    payload_status: "unavailable",
    truth_owner: "backend",
    selected_route: "pending_evidence",
    terminal_state: "payload_unavailable",
    latest_run: { status: "no_active_run", run_id: null },
    continuous_runtime: { status: "unavailable", runtime_state: "unavailable" },
    review_queue: [],
    candidate_counts: { discovery: 0, breakthrough: 0, portfolio: 0, design: 0, package: 0 },
    lifecycle: { stage_count: 30, active_stage: "unavailable", terminal_state: "payload_unavailable" },
    rules: { frontend_truth_mutation: false, candidate_generation: "not_fabricated", operator_review_required: true }
  };

  async function fetchJson(url) {
    const res = await fetch(url, { cache: "no-store" });
    const payload = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error("route_unavailable");
      err.url = url;
      err.status = res.status;
      err.payload = payload;
      throw err;
    }
    return payload;
  }

  async function firstAvailable(urls, fallback) {
    const attempts = [];
    for (const url of urls) {
      try {
        const payload = await fetchJson(url);
        return { payload, source: url, attempts, available: true };
      } catch (err) {
        attempts.push({ url, status: err.status || "error" });
      }
    }
    return { payload: fallback, source: null, attempts, available: false };
  }

  function normalizeQueue(payload) {
    if (!payload) return [];
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload.review_queue)) return payload.review_queue;
    if (Array.isArray(payload.items)) return payload.items;
    if (Array.isArray(payload.candidates)) return payload.candidates;
    if (payload.data && Array.isArray(payload.data.review_queue)) return payload.data.review_queue;
    return [];
  }

  function normalizeUniverses(payload) {
    if (!payload) return [];
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload.universes)) return payload.universes;
    if (Array.isArray(payload.source_universes)) return payload.source_universes;
    return [];
  }

  function candidateCounts(queue) {
    const out = { discovery: 0, breakthrough: 0, portfolio: 0, design: 0, package: 0 };
    (queue || []).forEach((item) => {
      const text = JSON.stringify(item).toLowerCase();
      if (text.includes("discovery") || text.includes("gap") || text.includes("trend") || text.includes("signal")) out.discovery += 1;
      if (text.includes("breakthrough")) out.breakthrough += 1;
      if (text.includes("portfolio")) out.portfolio += 1;
      if (text.includes("design") || text.includes("blueprint") || text.includes("autodesign")) out.design += 1;
      if (text.includes("package") || text.includes("acquisition")) out.package += 1;
    });
    return out;
  }

  async function load() {
    const payloadResult = await firstAvailable([ROUTES.primaryPayload, ROUTES.fallbackPayload], EMPTY);
    const statusResult = await firstAvailable([ROUTES.payloadStatus, ROUTES.fallbackPayloadStatus], { status: "unavailable", payload_status: "unavailable" });
    const continuousResult = await firstAvailable([ROUTES.continuousStatus], EMPTY.continuous_runtime);
    const queueResult = await firstAvailable([ROUTES.reviewQueue], { review_queue: [] });
    const universesResult = await firstAvailable([ROUTES.universes], { universes: [] });
    const truthResult = await firstAvailable([ROUTES.routeTruth], { status: "unavailable" });

    const queue = normalizeQueue(queueResult.payload);
    const counts = Object.assign({}, candidateCounts(queue), payloadResult.payload.candidate_counts || {});
    const universes = normalizeUniverses(universesResult.payload);

    return {
      adapter_build: BUILD,
      loaded_at: new Date().toISOString(),
      status: payloadResult.available ? "available" : "unavailable",
      payload_source: payloadResult.source,
      payload_attempts: payloadResult.attempts,
      payload_status: statusResult.payload,
      payload: Object.assign({}, EMPTY, payloadResult.payload, {
        continuous_runtime: Object.assign({}, EMPTY.continuous_runtime, payloadResult.payload.continuous_runtime || {}, continuousResult.payload || {}),
        review_queue: queue,
        candidate_counts: counts,
        source_universes: universes
      }),
      route_truth: truthResult.payload,
      rules: {
        backend_owns_truth: true,
        frontend_truth_mutation: false,
        candidate_generation: "not_fabricated",
        no_fake_output: true
      }
    };
  }

  window.ClaireCanonicalPayloadAdapter = {
    version: BUILD,
    routes: ROUTES,
    empty: EMPTY,
    load: load,
    normalizeQueue: normalizeQueue,
    normalizeUniverses: normalizeUniverses
  };
})();
