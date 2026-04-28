import { sendCommand } from "./api.js";
import { UpdateUI } from "./update_ui.js";

// CLAIRE Search Handler -> backend /api/command
function handleSearchEvent(event) {
  if (event.key === "Enter") {
    const query = event.target.value.trim();
    if (!query) return;

    console.log("CLAIRE Query:", query);

    sendCommand(query)
      .then(result => {
        console.log("CLAIRE Result:", result);
      })
      .catch(err => {
        console.error("CLAIRE Error:", err);
      });
  }
}

// Launch Process functionality
function launchProcess() {
  console.log("Launching innovation discovery process...");
  // Integration point for process launch (e.g., POST /api/command with "launch process")

  const launchBtn = document.querySelector(".launch-process");
  if (launchBtn) {
    launchBtn.style.background = "linear-gradient(135deg, var(--success), var(--accent2))";
    launchBtn.innerHTML = "<span>⚡</span>Processing...";

    setTimeout(() => {
      launchBtn.style.background = "linear-gradient(135deg, var(--accent), var(--accent3))";
      launchBtn.innerHTML = "<span>🚀</span>Launch Process";
    }, 3000);
  }
}

// Real-time spectrum animation
function initSpectrum() {
  const canvas = document.getElementById("spectrumCanvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const width = (canvas.width = canvas.offsetWidth);
  const height = (canvas.height = 60);

  let time = 0;

  function drawSpectrum() {
    ctx.clearRect(0, 0, width, height);

    const gradient = ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, "rgba(108, 99, 255, 0.1)");
    gradient.addColorStop(0.25, "rgba(0, 212, 170, 0.2)");
    gradient.addColorStop(0.5, "rgba(255, 215, 0, 0.3)");
    gradient.addColorStop(0.75, "rgba(244, 114, 182, 0.2)");
    gradient.addColorStop(1, "rgba(108, 99, 255, 0.1)");

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Analysis wave (blue)
    ctx.strokeStyle = "#6c63ff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let x = 0; x < width; x += 2) {
      const y =
        height / 2 +
        Math.sin((x + time) * 0.02) * 8 +
        Math.sin((x + time) * 0.05) * 4;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Discovery wave (teal)
    ctx.strokeStyle = "#22d3a7";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let x = 0; x < width; x += 2) {
      const y = height / 2 + Math.sin((x + time + 100) * 0.03) * 6;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Breakthrough wave (gold)
    ctx.strokeStyle = "#ffd700";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    for (let x = 0; x < width; x += 3) {
      const y =
        height / 2 +
        Math.sin((x + time + 200) * 0.025) * 10 +
        Math.sin((x + time + 50) * 0.08) * 3;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Innovation wave (pink)
    ctx.strokeStyle = "#ff6b9d";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x < width; x += 2) {
      const y = height / 2 + Math.sin((x + time + 300) * 0.04) * 5;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    time += 2;
    requestAnimationFrame(drawSpectrum);
  }

  drawSpectrum();
}

// Mode Switching
function switchMode(mode) {
  document.querySelectorAll(".mode-badge").forEach(badge => {
    badge.classList.remove("active");
  });

  if (window.event && window.event.target) {
    window.event.target.classList.add("active");
  }

  const modeDisplay = document.querySelector(".mode-display");
  const modeNames = {
    deterministic: "Deterministic Mode • Rule-based Analysis • Full Audit Trail",
    connected: "Connected Intelligence • AI-Enhanced • Real-time Learning",
    hybrid: "Hybrid Mode • Best of Both • Adaptive Intelligence"
  };

  if (modeDisplay) {
    modeDisplay.innerHTML = `
      <span>🔒</span>
      <span>${modeNames[mode]}</span>
    `;
  }

  console.log(`Switched to ${mode} mode`);
}

// Navigation Functions
function openDiscovery() {
  console.log("Opening Live Discoveries...");
}

function openMarketAnalysis() {
  console.log("Opening Market Analysis...");
}

function openInnovationSearch() {
  console.log("Opening Innovation Search...");
}

function openFinancialMarkets() {
  console.log("Opening Financial Markets...");
}

function openNewsIntelligence() {
  console.log("Opening News Intelligence...");
}

function openPatentDatabase() {
  console.log("Opening Patent Database...");
}

function openCompanyIntel() {
  console.log("Opening Company Intelligence...");
}

function openActivePortfolios() {
  console.log("Opening Active Portfolios...");
}

function openBuyerMatching() {
  console.log("Opening Buyer Matching...");
}

function openDealPipeline() {
  console.log("Opening Deal Pipeline...");
}

function openCustomization(type) {
  console.log(`Opening ${type} customization...`);
}

function openSettings() {
  console.log("Opening System Settings...");
}

// Keyboard shortcut for CLAIRE search
function initSearchShortcut() {
  document.addEventListener("keydown", function (event) {
    if ((event.metaKey || event.ctrlKey) && event.key === "k") {
      event.preventDefault();
      const input = document.querySelector(".search-input");
      if (input) input.focus();
    }
  });
}

// Wire everything on DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
  console.log("Claire-Syntalion Dashboard Initialized");
  console.log("Ready for FastAPI backend integration");

  initSpectrum();
  initSearchShortcut();
  new UpdateUI();
});

// Expose functions for inline HTML handlers
window.handleSearch = handleSearchEvent;
window.launchProcess = launchProcess;
window.switchMode = switchMode;
window.openDiscovery = openDiscovery;
window.openMarketAnalysis = openMarketAnalysis;
window.openInnovationSearch = openInnovationSearch;
window.openFinancialMarkets = openFinancialMarkets;
window.openNewsIntelligence = openNewsIntelligence;
window.openPatentDatabase = openPatentDatabase;
window.openCompanyIntel = openCompanyIntel;
window.openActivePortfolios = openActivePortfolios;
window.openBuyerMatching = openBuyerMatching;
window.openDealPipeline = openDealPipeline;
window.openCustomization = openCustomization;
window.openSettings = openSettings;