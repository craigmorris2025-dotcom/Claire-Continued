"use strict";
(function () {
  window.ClaireOperatorActionClickBridge = window.ClaireOperatorActionClickBridge || {
    build: "v19.89.8-s1626-s1650",
    status: "linked_to_dashboard_v3",
    click_count: 0,
    last_result: null
  };

  function actionKeyFrom(target) {
    const explicit = target.getAttribute("data-action-key")
      || target.getAttribute("data-operation-key")
      || target.getAttribute("data-operation-control");
    if (explicit) return explicit;

    const endpoint = target.getAttribute("data-endpoint-path")
      || target.getAttribute("data-endpoint")
      || "";
    if (!endpoint) return "inspect_endpoint";
    return endpoint
      .replace(/^\/+/, "")
      .replace(/[{}]/g, "")
      .replace(/[^A-Za-z0-9_/-]+/g, "-")
      .split("/")
      .filter(Boolean)
      .slice(-2)
      .join("_") || "inspect_endpoint";
  }

  function ensurePane() {
    let pane = document.querySelector(".claire-operator-action-result-pane");
    if (pane) return pane;

    pane = document.createElement("section");
    pane.className = "claire-operator-action-result-pane";
    pane.setAttribute("aria-live", "polite");
    pane.innerHTML = [
      "<div class=\"claire-result-pane-header\">",
      "<div><p class=\"claire-result-pane-kicker\">Operator action</p><h2>Review result</h2></div>",
      "<span class=\"claire-result-pane-lock\">Web execution blocked</span>",
      "</div>",
      "<div class=\"claire-action-result-loading\">Select an operator action to review its governed result.</div>"
    ].join("");

    const resultPane = document.getElementById("result-pane")
      || document.querySelector(".result-pane-wrap")
      || document.body;
    resultPane.appendChild(pane);
    return pane;
  }

  function renderResult(pane, payload) {
    window.ClaireOperatorActionClickBridge.last_result = payload;
    const blocked = payload.blocked_authority || {};
    pane.innerHTML = [
      "<div class=\"claire-result-pane-header\">",
      "<div><p class=\"claire-result-pane-kicker\">Operator action</p><h2></h2></div>",
      "<span class=\"claire-result-pane-lock\">Web execution blocked</span>",
      "</div>",
      "<article class=\"claire-action-result-card\">",
      "<div class=\"claire-result-status-row\"><span></span><span>Body reads blocked</span></div>",
      "<p class=\"claire-result-summary\"></p>",
      "<p class=\"claire-result-next-step\"></p>",
      "<div class=\"claire-result-lock-grid\"></div>",
      "</article>"
    ].join("");
    pane.querySelector("h2").textContent = payload.label || payload.action_key || "Review result";
    pane.querySelector(".claire-result-status-row span").textContent = payload.status || "review_preview_ready";
    pane.querySelector(".claire-result-summary").textContent = payload.summary || "Review-only preview is available. Execution remains blocked.";
    pane.querySelector(".claire-result-next-step").textContent = payload.next_step || "Continue through governed operator review before enabling any runtime action.";
    pane.querySelector(".claire-result-lock-grid").innerHTML = [
      "runtime mutation: " + (blocked.runtime_mutation || "blocked"),
      "network request: " + (payload.network_request_performed ? "performed" : "blocked"),
      "body reads: " + (payload.body_read_allowed ? "allowed" : "blocked"),
      "execution: " + (payload.execution_enabled ? "enabled" : "blocked")
    ].map(function (item) {
      const span = document.createElement("span");
      span.textContent = item;
      return span.outerHTML;
    }).join("");
  }

  function renderError(pane, error) {
    pane.innerHTML = [
      "<article class=\"claire-action-result-card claire-action-result-error\">",
      "<h3>Operator action review failed</h3>",
      "<p></p>",
      "<p>Web execution blocked. Body reads blocked.</p>",
      "</article>"
    ].join("");
    pane.querySelector("p").textContent = error && error.message ? error.message : String(error);
  }

  document.addEventListener("click", function (event) {
    const target = event.target && event.target.closest ? event.target.closest("[data-endpoint-path], [data-operation-control]") : null;
    if (!target) return;
    event.preventDefault();

    const actionKey = actionKeyFrom(target);
    const pane = ensurePane();
    window.ClaireOperatorActionClickBridge.click_count += 1;
    window.ClaireOperatorActionClickBridge.last_target = target.getAttribute("data-endpoint-path") || target.getAttribute("data-endpoint") || "";
    pane.innerHTML = "<div class=\"claire-action-result-loading\">Loading governed action preview. Web execution blocked. Body reads blocked.</div>";

    fetch("/dashboard/operator-action/result/" + encodeURIComponent(actionKey), { method: "GET" })
      .then(function (response) {
        if (!response.ok) throw new Error("GET action result failed: " + response.status);
        return response.json();
      })
      .then(function (payload) {
        renderResult(pane, payload);
      })
      .catch(function (error) {
        renderError(pane, error);
      });
  }, true);
})();
