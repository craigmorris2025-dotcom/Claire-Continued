/* Claire Syntalion v19.67 Panel Registry */
/* Truth rule: this registry describes UI panels only. Backend remains source of truth. */

window.ClaireCockpitPanelRegistry = (() => {
  const panels = [
    {
      id: "runtime",
      title: "Runtime",
      module: "runtime",
      cards: [
        ["runtime-status", "Runtime Status", "Shows backend/runtime availability once shared adapters are wired."],
        ["active-lifecycle", "Active Lifecycle", "Reserved for the 30-stage lifecycle execution state."],
        ["run-history", "Run History", "Reserved for run history and terminal states."],
        ["runtime-truth", "Runtime Truth", "Reserved for evidence/runtime-truth surfaces."]
      ]
    },
    {
      id: "intelligence",
      title: "Intelligence",
      module: "intelligence",
      cards: [
        ["command-surface", "Claire Command Surface", "Permanent search/command/research surface. v19.69 panel active with truthful blocked states."],
        ["governed-web", "Governed Web", "Reserved for source trust, provider readiness, allowlist, rate, and review state."],
        ["discovery-trends", "Discovery / Trends", "Reserved for discovery, trend, signal, and thesis outputs."],
        ["portfolio", "Portfolio Intelligence", "Reserved for portfolio creation/optimization outputs."]
      ]
    },
    {
      id: "design",
      title: "Design",
      module: "design",
      cards: [
        ["breakthroughs", "Breakthroughs", "Reserved for breakthrough classification and escalation."],
        ["advancement-path", "Advancement Path", "Reserved for route-aware advancement selection."],
        ["autodesign", "AutoDesign", "Reserved for design/invention/system architecture outputs."],
        ["blueprint-viewer", "Blueprint Viewer", "Reserved for blueprint/spec/buildability outputs."]
      ]
    },
    {
      id: "package",
      title: "Package",
      module: "package",
      cards: [
        ["packages", "Packages", "Reserved for final package construction outputs."],
        ["acquisition-fit", "Acquisition Fit", "Reserved for acquirer rationale and fit analysis."],
        ["positioning", "Strategic Positioning", "Reserved for moat, differentiation, and value capture."],
        ["exports", "Exports", "Reserved for export/package links."]
      ]
    },
    {
      id: "system",
      title: "System",
      module: "system",
      cards: [
        ["system-health", "System Health", "Reserved for health, boot, and route proof."],
        ["route-proof", "Route Proof", "Reserved for backend route/payload ownership state."],
        ["provider-readiness", "Provider Readiness", "Reserved for search/provider/governed web readiness."],
        ["governance-proof", "Governance Proof", "Reserved for allowlist, trust, rate, and safety proof."]
      ]
    }
  ];

  function all() {
    return panels.slice();
  }

  function find(id) {
    return panels.find((panel) => panel.id === id) || panels[0];
  }

  return { all, find };
})();
