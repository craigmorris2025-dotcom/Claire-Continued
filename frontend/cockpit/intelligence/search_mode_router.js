
/* Claire Syntalion v19.69 Search Mode Router */
/* No fake web results. Disabled modes return truthful blocked states. */
window.ClaireSearchModeRouter = (() => {
  function classifyCommand(query) {
    const q = String(query || "").trim().toLowerCase();
    if (!q) return { type: "empty", title: "No command entered", detail: "Enter a search or command.", allowed: false };
    if (q.includes("runtime") || q.includes("lifecycle") || q.includes("payload")) {
      return { type: "navigate_runtime", title: "Runtime navigation preview", detail: "This can route to runtime/lifecycle panels after command execution wiring.", allowed: true };
    }
    if (q.includes("search") || q.includes("web") || q.includes("research")) {
      return { type: "search_request", title: "Search/research intent detected", detail: "This will route into governed search once live provider wiring is enabled.", allowed: true };
    }
    return { type: "unknown_preview", title: "Command preview", detail: "No executable command is enabled for this text yet.", allowed: false };
  }

  async function run(modeId, query) {
    const mode = window.ClaireSearchStateModel.getMode(modeId);
    const trimmed = String(query || "").trim();

    if (!mode.enabled) {
      return { ok: false, mode: mode.id, blocked: true, title: mode.label + " unavailable", message: mode.unavailableReason, results: [] };
    }
    if (!trimmed) {
      return { ok: false, mode: mode.id, blocked: true, title: "Empty query", message: "Enter a query before running search.", results: [] };
    }
    if (mode.id === "command_recognition") {
      const preview = classifyCommand(trimmed);
      return { ok: true, mode: mode.id, blocked: false, title: preview.title, message: preview.detail, results: [preview] };
    }
    if (mode.id === "runtime_project_search") {
      return runRuntimeProjectSearch(trimmed);
    }
    return { ok: false, mode: mode.id, blocked: true, title: "Mode not implemented", message: "This mode is registered but not wired yet.", results: [] };
  }

  async function runRuntimeProjectSearch(query) {
    if (!window.ClaireCockpitPayloadAdapter) {
      return { ok: false, mode: "runtime_project_search", blocked: true, title: "Payload adapter unavailable", message: "Shared payload adapter is required.", results: [] };
    }

    let payload = window.ClaireCockpitPayloadAdapter.getState().payload;
    if (!payload.loaded || !payload.ok) {
      await window.ClaireCockpitPayloadAdapter.refreshAll();
      payload = window.ClaireCockpitPayloadAdapter.getState().payload;
    }
    if (!payload.ok) {
      return { ok: false, mode: "runtime_project_search", blocked: true, title: "Runtime payload unavailable", message: payload.error || "Could not load /dashboard/payload.", results: [] };
    }

    const results = searchObject(payload.data, query).slice(0, 25);
    return { ok: true, mode: "runtime_project_search", blocked: false, title: "Runtime/project search complete", message: results.length + " payload matches found.", results };
  }

  function searchObject(value, query) {
    const q = String(query || "").toLowerCase();
    const results = [];

    function visit(node, path) {
      if (results.length >= 100 || node === null || typeof node === "undefined") return;
      if (typeof node === "string" || typeof node === "number" || typeof node === "boolean") {
        const text = String(node);
        if (text.toLowerCase().includes(q)) {
          results.push({ type: "payload_match", title: path || "payload", detail: text.length > 220 ? text.slice(0, 220) + "…" : text, allowed: true });
        }
        return;
      }
      if (Array.isArray(node)) {
        node.forEach((item, index) => visit(item, path + "[" + index + "]"));
        return;
      }
      if (typeof node === "object") {
        Object.keys(node).forEach((key) => {
          if (key.toLowerCase().includes(q)) {
            results.push({ type: "payload_key_match", title: path ? path + "." + key : key, detail: "Matched payload key.", allowed: true });
          }
          visit(node[key], path ? path + "." + key : key);
        });
      }
    }

    visit(value, "payload");
    return results;
  }

  return { run, classifyCommand };
})();
