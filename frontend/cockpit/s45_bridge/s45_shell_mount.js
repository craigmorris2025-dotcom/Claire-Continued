/*
 * Claire S45 shell mount.
 * Presentation-only panel data mounting over backend-owned read-only payloads.
 */

export const S45_SHELL_MOUNT_CONTRACT = Object.freeze({
  version: "v19.89.8-S45R9-R16",
  backendOwnsTruth: true,
  cockpitPresentationOnly: true,
  presentationOnly: true,
  runtimeTruthMutationAllowed: false,
  operatorMutationEnabled: false,
  autonomousExecutionEnabled: false,
  automaticUpdatesEnabled: false,
  responseMode: "read_only_artifact"
});

export function createPanelMount(panel) {
  return {
    mountId: panel.mount_id || panel.panel_id,
    surfaceId: panel.surface_id,
    fetchPath: panel.fetch_path,
    method: "GET",
    mounted: true,
    renderMode: "read_only_operator_card",
    responseMode: "read_only_artifact",
    presentationOnly: true,
    runtimeTruthMutationAllowed: false,
    operatorMutationEnabled: false
  };
}

export async function mountReadOnlyPanel(target, panel) {
  const mount = createPanelMount(panel);
  const response = await fetch(mount.fetchPath, {
    method: "GET",
    cache: "no-store",
    headers: { "Accept": "application/json" }
  });

  const payload = await response.json();
  const section = document.createElement("section");
  section.className = "s45-shell-mounted-panel";
  section.id = mount.mountId;
  section.dataset.responseMode = "read_only_artifact";
  section.dataset.runtimeTruthMutationAllowed = "false";
  section.dataset.operatorMutationEnabled = "false";

  const heading = document.createElement("h3");
  heading.textContent = panel.title || mount.surfaceId;

  const status = document.createElement("p");
  status.textContent = response.ok ? "Available" : "Unavailable";

  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(payload, null, 2);

  section.appendChild(heading);
  section.appendChild(status);
  section.appendChild(pre);
  target.appendChild(section);

  return {
    ...mount,
    status: response.status,
    available: response.ok,
    payload,
    rendered: true
  };
}
