/*
Claire Syntalion v19.77
Cockpit UX Diagnostics

Browser-side diagnostics only. This does not create runtime truth.
*/

export function collectCockpitUxDiagnostics() {
  const runtimeGate = document.getElementById("claire-runtime-payload-gate-mount");
  const migrationStrip = document.getElementById("claire-cockpit-migration-status-strip");

  return {
    version: "v19.77",
    checked_at: new Date().toISOString(),
    cockpit_shell_loaded: true,
    runtime_gate_mount_present: Boolean(runtimeGate),
    migration_status_strip_present: Boolean(migrationStrip),
    runtime_gate_state: runtimeGate ? runtimeGate.getAttribute("data-bridge-state") || "present" : "missing",
    search_surface_policy: "backend_truth_owned_no_fake_results",
    launcher_target: "frontend/cockpit/shell/cockpit_shell.html",
    legacy_dashboard_state: "preserved_fallback",
  };
}

export function renderCockpitUxDiagnostics(target) {
  if (!target) return;
  const diagnostics = collectCockpitUxDiagnostics();
  target.innerHTML = `
    <section class="cockpit-ux-diagnostics">
      <h3>Cockpit UX Diagnostics</h3>
      <pre>${JSON.stringify(diagnostics, null, 2)}</pre>
    </section>
  `;
}
