/* Claire v17.50 Dashboard Action Buttons
   Governed frontend action layer. It injects a small panel only once and calls
   declared backend routes with fetch. No shell execution, no eval, no dynamic code. */
(function () {
  "use strict";

  const PANEL_ID = "claire-v17-50-dashboard-actions";
  const OUTPUT_ID = "claire-v17-50-dashboard-output";
  const BUTTON_ENDPOINT = "/dashboard/alignment/buttons";

  const fallbackButtons = [
    { id: "health_check", label: "Check Runtime Health", method: "GET", route: "/health", category: "Runtime" },
    { id: "dashboard_alignment", label: "Verify Dashboard Alignment", method: "GET", route: "/dashboard/alignment/status", category: "Dashboard" },
    { id: "dashboard_capabilities", label: "Load Capability Manifest", method: "GET", route: "/dashboard/alignment/capabilities", category: "Dashboard" }
  ];

  function safeText(value) {
    if (typeof value === "string") return value;
    return JSON.stringify(value, null, 2);
  }

  function writeOutput(value) {
    const output = document.getElementById(OUTPUT_ID);
    if (!output) return;
    output.textContent = safeText(value);
  }

  async function callRoute(button) {
    writeOutput("Calling " + button.method + " " + button.route + " ...");
    try {
      const response = await fetch(button.route, { method: button.method || "GET", headers: { "Accept": "application/json" } });
      const contentType = response.headers.get("content-type") || "";
      const body = contentType.includes("application/json") ? await response.json() : await response.text();
      writeOutput({ button: button.id, route: button.route, ok: response.ok, status: response.status, body: body });
    } catch (error) {
      writeOutput({ button: button.id, route: button.route, ok: false, error: String(error) });
    }
  }

  function makeButton(button) {
    const el = document.createElement("button");
    el.type = "button";
    el.textContent = button.label;
    el.setAttribute("data-claire-action", button.id);
    el.style.margin = "4px";
    el.style.padding = "7px 10px";
    el.style.borderRadius = "8px";
    el.style.border = "1px solid rgba(255,255,255,0.25)";
    el.style.cursor = "pointer";
    el.addEventListener("click", function () { callRoute(button); });
    return el;
  }

  function renderPanel(buttons) {
    if (document.getElementById(PANEL_ID)) return;
    const panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.style.position = "fixed";
    panel.style.right = "16px";
    panel.style.bottom = "16px";
    panel.style.zIndex = "99999";
    panel.style.maxWidth = "420px";
    panel.style.maxHeight = "70vh";
    panel.style.overflow = "auto";
    panel.style.padding = "14px";
    panel.style.borderRadius = "14px";
    panel.style.background = "rgba(20, 24, 34, 0.94)";
    panel.style.color = "white";
    panel.style.boxShadow = "0 8px 32px rgba(0,0,0,0.35)";
    panel.style.fontFamily = "system-ui, -apple-system, Segoe UI, sans-serif";

    const title = document.createElement("h3");
    title.textContent = "Claire Runtime Actions v17.50";
    title.style.margin = "0 0 8px 0";
    title.style.fontSize = "15px";
    panel.appendChild(title);

    const help = document.createElement("p");
    help.textContent = "Use these buttons to verify dashboard/backend alignment and installed runtime capabilities.";
    help.style.fontSize = "12px";
    help.style.opacity = "0.85";
    help.style.margin = "0 0 8px 0";
    panel.appendChild(help);

    const buttonBox = document.createElement("div");
    buttons.forEach(function (button) { buttonBox.appendChild(makeButton(button)); });
    panel.appendChild(buttonBox);

    const output = document.createElement("pre");
    output.id = OUTPUT_ID;
    output.textContent = "Ready.";
    output.style.marginTop = "10px";
    output.style.padding = "10px";
    output.style.borderRadius = "10px";
    output.style.background = "rgba(0,0,0,0.35)";
    output.style.fontSize = "11px";
    output.style.whiteSpace = "pre-wrap";
    output.style.maxHeight = "240px";
    output.style.overflow = "auto";
    panel.appendChild(output);

    document.body.appendChild(panel);
  }

  async function loadButtons() {
    try {
      const response = await fetch(BUTTON_ENDPOINT, { headers: { "Accept": "application/json" } });
      if (!response.ok) return fallbackButtons;
      const payload = await response.json();
      return Array.isArray(payload.buttons) ? payload.buttons : fallbackButtons;
    } catch (error) {
      return fallbackButtons;
    }
  }

  function boot() {
    loadButtons().then(renderPanel);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
}());
