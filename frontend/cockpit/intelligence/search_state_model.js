
/* Claire Syntalion v19.69 Search State Model */
window.ClaireSearchStateModel = (() => {
  const modes = [
    { id: "normal_web_search", label: "Web", enabled: false, unavailableReason: "Live web execution is not wired in this cockpit step." },
    { id: "governed_research", label: "Research", enabled: false, unavailableReason: "Governed research route wiring is pending." },
    { id: "runtime_project_search", label: "Runtime", enabled: true, unavailableReason: null },
    { id: "command_recognition", label: "Command", enabled: true, unavailableReason: null },
    { id: "future_ai_agent_entry", label: "Agent", enabled: false, unavailableReason: "Future AI-agent execution is reserved but not enabled." }
  ];

  const state = { activeMode: "runtime_project_search", query: "", results: [], lastError: null };

  function getModes() { return JSON.parse(JSON.stringify(modes)); }
  function getMode(id) { return modes.find((mode) => mode.id === id) || modes[0]; }
  function getState() { return JSON.parse(JSON.stringify(state)); }
  function setActiveMode(modeId) { state.activeMode = getMode(modeId).id; notify(); }
  function setQuery(query) { state.query = query || ""; notify(); }
  function setResults(results) { state.results = Array.isArray(results) ? results : []; state.lastError = null; notify(); }
  function setError(error) { state.lastError = error || "unknown_error"; notify(); }

  function notify() {
    window.dispatchEvent(new CustomEvent("claire:search-state", { detail: getState() }));
  }

  return { getModes, getMode, getState, setActiveMode, setQuery, setResults, setError };
})();
