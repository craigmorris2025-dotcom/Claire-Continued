/*
Claire Command Response Cards — S457-S463
Presentation-only cockpit renderer. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireCommandResponseCardsVersion = "v19.89.8-S457-S463";

  const ClaireCommandResponseAuthority = Object.freeze({
    backendOwnsTruth: true,
    cockpitPresentationOnly: true,
    runtimeTruthMutationAllowed: false,
    runtimeTruthWriteAllowed: false,
    runtimeMutationEnabled: false,
    automaticUpdatesEnabled: false,
    autonomousCrawlingEnabled: false,
    autonomousExecutionEnabled: false,
    autonomousAgentExecutionEnabled: false,
    liveWebExecutionEnabled: false,
    browserExecutionEnabled: false,
    networkRequestPerformed: false,
    bodyReadAllowed: false
  });

  function ensureStack() {
    let stack = document.getElementById("claire-command-response-stack");
    if (stack) return stack;

    stack = document.createElement("section");
    stack.id = "claire-command-response-stack";
    stack.className = "claire-command-response-stack";
    stack.setAttribute("data-version", ClaireCommandResponseCardsVersion);
    stack.innerHTML = [
      "<div class='claire-command-stack-header'>",
      "<span>Claire Command Response Cards</span>",
      "<small>Read-only • Governed • Backend truth</small>",
      "</div>",
      "<div id='claire-command-card-list' class='claire-command-card-list'>",
      "<div class='claire-command-card claire-command-card-empty'>",
      "<strong>Ready for governed Claire command responses.</strong>",
      "<p>Ask Claire a question, request route context, evidence requirements, or safe next steps.</p>",
      "</div>",
      "</div>"
    ].join("");

    const target =
      document.getElementById("claire-intelligence-answer-panel") ||
      document.querySelector("[data-claire-command-surface]") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(stack);
    return stack;
  }

  function renderClaireCommandResponseCard(card) {
    const stack = ensureStack();
    const list = stack.querySelector("#claire-command-card-list");
    const el = document.createElement("article");
    const blocked = card && card.card_type === "blocked";
    el.className = "claire-command-card" + (blocked ? " claire-command-card-blocked" : "");
    el.setAttribute("data-card-type", (card && card.card_type) || "answer");

    const chips = ((card && card.chips) || []).map(function (chip) {
      return "<span class='claire-command-chip'>" + escapeHtml(chip) + "</span>";
    }).join("");

    const safeActions = ((card && card.safe_actions) || []).map(function (action) {
      return "<button type='button' class='claire-safe-action-button' data-action='" + escapeHtml(action) + "'>" +
        escapeHtml(action.replaceAll("_", " ")) +
        "</button>";
    }).join("");

    el.innerHTML = [
      "<div class='claire-command-card-topline'>",
      "<strong>" + escapeHtml((card && card.title) || "Claire response") + "</strong>",
      "<small>" + escapeHtml((card && card.card_type) || "answer") + "</small>",
      "</div>",
      "<p>" + escapeHtml((card && card.summary) || "No response summary available.") + "</p>",
      "<div class='claire-command-chip-row'>" + chips + "</div>",
      "<div class='claire-safe-action-row'>" + safeActions + "</div>",
      "<footer>Runtime mutation, autonomous execution, live web execution, and automatic updates remain blocked.</footer>"
    ].join("");

    list.prepend(el);
    return el;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.ClaireCommandResponseCards = Object.freeze({
    version: ClaireCommandResponseCardsVersion,
    authority: ClaireCommandResponseAuthority,
    ensureStack,
    renderClaireCommandResponseCard
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureStack);
  } else {
    ensureStack();
  }
})();
