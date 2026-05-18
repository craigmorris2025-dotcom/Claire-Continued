/* Claire Syntalion v19.68 Status Model */

window.ClaireCockpitStatusModel = (() => {
  function labelFor(entry, label) {
    if (!entry || !entry.loaded) return `${label}: not loaded`;
    if (entry.ok) return `${label}: online`;
    if (entry.error === "request_timeout") return `${label}: timeout`;
    return `${label}: unavailable`;
  }

  function classFor(entry) {
    if (!entry || !entry.loaded) return "status-pill status-unwired";
    if (entry.ok) return "status-pill status-online";
    return "status-pill status-error";
  }

  function explain(entry) {
    if (!entry || !entry.loaded) return "Not loaded yet.";
    if (entry.ok) return "Loaded from backend canonical route.";
    return `Unavailable: ${entry.error || "unknown error"}`;
  }

  return { labelFor, classFor, explain };
})();
