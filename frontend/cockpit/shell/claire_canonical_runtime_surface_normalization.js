
// Claire Syntalion v19.89.8-S8
// Canonical Runtime Surface Normalization
// Backend owns truth. Cockpit presentation only.

(function () {
  "use strict";

  const VERSION = "v19.89.8-S8";

  const CANONICAL = {
    LIVE: "live",
    DEGRADED: "degraded",
    UNAVAILABLE: "unavailable",
    BLOCKED: "blocked"
  };

  const NORMALIZATION_MAP = {
    "connected": CANONICAL.LIVE,
    "available": CANONICAL.LIVE,
    "complete": CANONICAL.LIVE,
    "active": CANONICAL.LIVE,
    "healthy": CANONICAL.LIVE,
    "ok": CANONICAL.LIVE,

    "partial": CANONICAL.DEGRADED,
    "degraded": CANONICAL.DEGRADED,
    "limited": CANONICAL.DEGRADED,
    "fallback": CANONICAL.DEGRADED,

    "offline": CANONICAL.UNAVAILABLE,
    "unavailable": CANONICAL.UNAVAILABLE,
    "failed": CANONICAL.UNAVAILABLE,
    "failed to fetch": CANONICAL.UNAVAILABLE,

    "blocked": CANONICAL.BLOCKED,
    "disabled": CANONICAL.BLOCKED,
    "runtime authority blocked": CANONICAL.BLOCKED
  };

  const state = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    normalized: [],
    counts: {
      live: 0,
      degraded: 0,
      unavailable: 0,
      blocked: 0
    }
  };

  function normalize(text) {
    if (!text) return null;
    const lowered = String(text).trim().toLowerCase();

    for (const [key, value] of Object.entries(NORMALIZATION_MAP)) {
      if (lowered.includes(key)) return value;
    }

    return null;
  }

  function allNodes() {
    return Array.from(document.querySelectorAll("div, section, article, span, p, h1, h2, h3, h4"));
  }

  function badgeFor(node) {
    if (!node) return null;

    const text = (node.innerText || "").trim();
    const normalized = normalize(text);

    if (!normalized) return null;

    return {
      node,
      original: text,
      normalized
    };
  }

  function applyCanonical(node, normalized) {
    if (!node || !normalized) return;

    node.setAttribute("data-claire-s8-normalized", normalized);

    const canonicalText =
      normalized === CANONICAL.LIVE ? "Live" :
      normalized === CANONICAL.DEGRADED ? "Degraded" :
      normalized === CANONICAL.UNAVAILABLE ? "Unavailable" :
      normalized === CANONICAL.BLOCKED ? "Blocked" :
      normalized;

    // Avoid rewriting large content blocks.
    const current = (node.innerText || "").trim();

    if (
      current.length < 40 &&
      (
        current.toLowerCase().includes("connected") ||
        current.toLowerCase().includes("available") ||
        current.toLowerCase().includes("complete") ||
        current.toLowerCase().includes("active") ||
        current.toLowerCase().includes("healthy") ||
        current.toLowerCase().includes("ok") ||
        current.toLowerCase().includes("offline") ||
        current.toLowerCase().includes("failed") ||
        current.toLowerCase().includes("blocked")
      )
    ) {
      node.textContent = canonicalText;
    }

    if (normalized === CANONICAL.LIVE) {
      node.setAttribute("data-claire-runtime-surface-live", "true");
    }
  }

  function runNormalization() {
    state.normalized = [];
    state.counts = {
      live: 0,
      degraded: 0,
      unavailable: 0,
      blocked: 0
    };

    const seen = new WeakSet();

    for (const node of allNodes()) {
      if (seen.has(node)) continue;

      const result = badgeFor(node);

      if (!result) continue;

      applyCanonical(result.node, result.normalized);

      state.normalized.push({
        original: result.original,
        normalized: result.normalized
      });

      if (state.counts[result.normalized] !== undefined) {
        state.counts[result.normalized] += 1;
      }

      seen.add(node);
    }

    document.documentElement.setAttribute(
      "data-claire-runtime-surface-normalized",
      VERSION
    );

    window.ClaireCanonicalRuntimeSurfaceNormalization = state;

    return state;
  }

  window.ClaireCanonicalRuntimeSurfaceNormalizationTools = {
    version: VERSION,
    run: runNormalization,
    state
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runNormalization);
  } else {
    runNormalization();
  }

  setInterval(runNormalization, 30000);
})();
