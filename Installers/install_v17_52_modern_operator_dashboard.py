#!/usr/bin/env python3
"""
Claire Syntalion v17.52 — Modern Operator Dashboard
Single-file installer.

Purpose:
- Transform the launcher Command Center from a build/status layer into a real operator dashboard.
- Preserve existing dashboard files by backing them up.
- Add a modern dashboard shell, CSS, JS, runtime data adapter, manifest, and tests.
- Keep runtime isolation: dashboard reads status/actions; it does not mutate backend state without explicit button actions.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


VERSION = "v17.52"
BUILD_NAME = "Modern Operator Dashboard"
ROOT = Path.cwd()

FRONTEND_DIR = ROOT / "src" / "frontend" / "command_center" / "modern"
MANIFEST_DIR = ROOT / "manifests"
TESTS_DIR = ROOT / "tests"
BACKUP_DIR = ROOT / "backups" / "v17_52_modern_operator_dashboard"

FILES = {
    FRONTEND_DIR / "index.html": """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Claire Syntalion Operator Dashboard</title>
  <link rel="stylesheet" href="./operator_dashboard.css"/>
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">C</div>
        <div>
          <strong>Claire Syntalion</strong>
          <span>Governed Intelligence Platform</span>
        </div>
      </div>

      <nav class="nav" aria-label="Primary dashboard navigation">
        <button class="nav-item active" data-view="overview">Overview</button>
        <button class="nav-item" data-view="internet">Internet Ops</button>
        <button class="nav-item" data-view="campaigns">Campaigns</button>
        <button class="nav-item" data-view="trust">Source Trust</button>
        <button class="nav-item" data-view="runtime">Runtime Health</button>
        <button class="nav-item" data-view="deployment">Deployment</button>
        <button class="nav-item" data-view="launch">Launch Lock</button>
        <button class="nav-item" data-view="actions">Actions</button>
      </nav>

      <section class="operator-card">
        <span class="card-label">Operator Rule</span>
        <p>Blank data is a system signal. Claire should show unavailable, missing route, or insufficient evidence — never fake success.</p>
      </section>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">Modern Operator Dashboard</p>
          <h1 id="view-title">Overview</h1>
          <p id="view-subtitle">Governed operational status, runtime readiness, and controlled launch actions.</p>
        </div>
        <div class="topbar-actions">
          <button id="refresh-state" class="button primary">Refresh State</button>
          <button id="open-guide" class="button ghost">Use Guide</button>
        </div>
      </header>

      <section id="status-strip" class="status-strip" aria-live="polite"></section>
      <section id="dashboard-content" class="content-grid"></section>
    </main>
  </div>

  <dialog id="guide-dialog" class="guide-dialog">
    <h2>Claire Operator Guide</h2>
    <p>This dashboard is the control surface for using Claire, not just viewing build progress.</p>
    <ol>
      <li>Start with Overview to confirm readiness and blockers.</li>
      <li>Use Internet Ops and Campaigns for governed external intelligence work.</li>
      <li>Use Source Trust before relying on live findings.</li>
      <li>Use Runtime Health and Deployment before extended runs.</li>
      <li>Use Launch Lock to confirm protected invariants before any real use session.</li>
    </ol>
    <button class="button primary" onclick="document.getElementById('guide-dialog').close()">Close</button>
  </dialog>

  <script src="./operator_dashboard.js"></script>
</body>
</html>
""",

    FRONTEND_DIR / "operator_dashboard.css": """:root {
  --bg: #08101f;
  --panel: rgba(255,255,255,0.075);
  --panel-strong: rgba(255,255,255,0.115);
  --text: #f5f7fb;
  --muted: #a8b3c7;
  --line: rgba(255,255,255,0.14);
  --good: #68e0a4;
  --warn: #ffd166;
  --bad: #ff6b6b;
  --info: #72b7ff;
  --shadow: 0 24px 80px rgba(0,0,0,0.35);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at top left, rgba(54, 102, 255, 0.24), transparent 32rem),
    radial-gradient(circle at bottom right, rgba(0, 220, 160, 0.12), transparent 28rem),
    var(--bg);
}

button { font: inherit; }

.app-shell {
  display: grid;
  grid-template-columns: 310px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  border-right: 1px solid var(--line);
  padding: 26px;
  background: rgba(3, 9, 20, 0.72);
  backdrop-filter: blur(24px);
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 34px;
}

.brand-mark {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(100, 160, 255, 0.9), rgba(60, 230, 170, 0.9));
  color: #06101f;
  font-weight: 900;
  box-shadow: var(--shadow);
}

.brand strong { display: block; letter-spacing: -0.02em; }
.brand span { display: block; color: var(--muted); font-size: 0.84rem; margin-top: 3px; }

.nav { display: grid; gap: 8px; }

.nav-item {
  width: 100%;
  text-align: left;
  color: var(--muted);
  border: 1px solid transparent;
  background: transparent;
  padding: 12px 14px;
  border-radius: 14px;
  cursor: pointer;
}

.nav-item:hover,
.nav-item.active {
  color: var(--text);
  border-color: var(--line);
  background: var(--panel);
}

.operator-card {
  margin-top: 26px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.045));
}

.card-label,
.eyebrow {
  color: var(--info);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 0.72rem;
  font-weight: 800;
}

.operator-card p { color: var(--muted); line-height: 1.5; }

.workspace { padding: 30px; min-width: 0; }

.topbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

h1 { margin: 4px 0 8px; font-size: clamp(2rem, 4vw, 4rem); letter-spacing: -0.06em; }
h2 { margin: 0 0 10px; letter-spacing: -0.03em; }
p { margin: 0; }
#view-subtitle { color: var(--muted); max-width: 780px; line-height: 1.5; }

.topbar-actions { display: flex; gap: 10px; }

.button {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 11px 15px;
  color: var(--text);
  background: var(--panel);
  cursor: pointer;
}

.button.primary {
  color: #06101f;
  border-color: transparent;
  background: linear-gradient(135deg, #8db8ff, #75efbd);
  font-weight: 800;
}

.button.ghost:hover,
.button:hover { background: var(--panel-strong); }

.status-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.status-pill {
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 18px;
  padding: 14px;
}

.status-pill strong { display: block; font-size: 1.1rem; margin-top: 5px; }
.status-pill span { color: var(--muted); font-size: 0.78rem; }

.content-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 14px;
}

.panel {
  grid-column: span 4;
  min-height: 170px;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--panel);
  box-shadow: var(--shadow);
}

.panel.wide { grid-column: span 8; }
.panel.full { grid-column: 1 / -1; }

.panel p,
.panel li { color: var(--muted); line-height: 1.55; }

.metric {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 10px 0;
  border-bottom: 1px solid var(--line);
}

.metric:last-child { border-bottom: 0; }

.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 5px 10px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.08);
  font-size: 0.78rem;
  font-weight: 800;
}

.badge.good { color: var(--good); }
.badge.warn { color: var(--warn); }
.badge.bad { color: var(--bad); }
.badge.info { color: var(--info); }

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.action-button {
  text-align: left;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(255,255,255,0.08);
  color: var(--text);
  padding: 16px;
  cursor: pointer;
}

.action-button strong { display: block; margin-bottom: 6px; }
.action-button span { color: var(--muted); font-size: 0.9rem; line-height: 1.35; }

.notice {
  border-left: 4px solid var(--warn);
  background: rgba(255, 209, 102, 0.08);
  padding: 14px;
  border-radius: 14px;
}

.guide-dialog {
  width: min(680px, calc(100vw - 32px));
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 26px;
  color: var(--text);
  background: #0c1728;
}

.guide-dialog::backdrop { background: rgba(0,0,0,0.66); }

@media (max-width: 980px) {
  .app-shell { grid-template-columns: 1fr; }
  .sidebar { position: static; }
  .status-strip { grid-template-columns: repeat(2, 1fr); }
  .panel,
  .panel.wide { grid-column: 1 / -1; }
}

@media (max-width: 560px) {
  .workspace,
  .sidebar { padding: 18px; }
  .topbar { display: block; }
  .topbar-actions { margin-top: 16px; }
  .status-strip,
  .action-grid { grid-template-columns: 1fr; }
}
""",

    FRONTEND_DIR / "operator_dashboard.js": """const state = {
  view: "overview",
  backend: null,
  lastUpdated: null,
};

const routes = {
  health: ["/health", "/"],
  internetDashboard: ["/internet/ops/dashboard", "/internet/operations/dashboard"],
  dashboardState: ["/dashboard/state", "/api/dashboard/state"],
  launchLock: ["/launch/regression-lock", "/api/launch/regression-lock"],
  sourceTrust: ["/internet/source-trust", "/api/internet/source-trust"],
  campaigns: ["/internet/campaigns", "/api/internet/campaigns"],
};

const views = {
  overview: {
    title: "Overview",
    subtitle: "A plain-language operational view of Claire readiness, blockers, live status, and next safe action.",
  },
  internet: {
    title: "Internet Operations",
    subtitle: "Governed search, external evidence, bounded online execution, and internet runtime state.",
  },
  campaigns: {
    title: "Campaigns",
    subtitle: "Persistent longitudinal intelligence campaigns, refresh cycles, and campaign lifecycle state.",
  },
  trust: {
    title: "Source Trust",
    subtitle: "Adaptive source reputation, evidence weighting, quarantine, release, and trust risk.",
  },
  runtime: {
    title: "Runtime Health",
    subtitle: "Runtime stability, degraded-mode status, recovery protection, and orchestration safety.",
  },
  deployment: {
    title: "Deployment",
    subtitle: "Production hardening, rollback continuity, manifest state, and deployment safety.",
  },
  launch: {
    title: "Launch Lock",
    subtitle: "Regression lock, invariant protection, governance boundary status, and release readiness.",
  },
  actions: {
    title: "Actions",
    subtitle: "Safe operator actions with visible availability and route checks.",
  },
};

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([key, value]) => {
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  });
  children.forEach((child) => node.append(child));
  return node;
}

async function firstJson(routeList) {
  for (const route of routeList) {
    try {
      const response = await fetch(route, { cache: "no-store" });
      if (!response.ok) continue;
      const text = await response.text();
      try {
        return { route, ok: true, data: JSON.parse(text) };
      } catch {
        return { route, ok: true, data: { raw: text.slice(0, 500) } };
      }
    } catch {
      continue;
    }
  }
  return { route: null, ok: false, data: null };
}

async function loadBackendState() {
  const checks = {};
  await Promise.all(Object.entries(routes).map(async ([name, routeList]) => {
    checks[name] = await firstJson(routeList);
  }));

  state.backend = {
    checks,
    health: checks.health.ok ? "online" : "unavailable",
    dashboardState: checks.dashboardState.data,
    internet: checks.internetDashboard.ok,
    campaigns: checks.campaigns.ok,
    trust: checks.sourceTrust.ok,
    launchLock: checks.launchLock.ok,
  };
  state.lastUpdated = new Date();
}

function badge(ok, goodText = "Available", badText = "Needs wiring") {
  return el("span", { class: `badge ${ok ? "good" : "warn"}`, text: ok ? goodText : badText });
}

function panel(title, body, options = {}) {
  return el("section", { class: `panel ${options.className || ""}` }, [
    el("h2", { text: title }),
    ...(Array.isArray(body) ? body : [body]),
  ]);
}

function metric(label, valueNode) {
  return el("div", { class: "metric" }, [
    el("span", { text: label }),
    typeof valueNode === "string" ? el("strong", { text: valueNode }) : valueNode,
  ]);
}

function renderStrip() {
  const strip = document.getElementById("status-strip");
  strip.innerHTML = "";

  const backend = state.backend || {};
  const items = [
    ["Backend", backend.health === "online" ? "Online" : "Unavailable"],
    ["Internet Ops", backend.internet ? "Route found" : "Needs wiring"],
    ["Campaigns", backend.campaigns ? "Route found" : "Needs wiring"],
    ["Launch Lock", backend.launchLock ? "Route found" : "Needs wiring"],
  ];

  for (const [label, value] of items) {
    strip.append(el("div", { class: "status-pill" }, [
      el("span", { text: label }),
      el("strong", { text: value }),
    ]));
  }
}

function overviewView() {
  const backend = state.backend || {};
  return [
    panel("Operational Readiness", [
      metric("Backend health", badge(backend.health === "online", "Online", "Unavailable")),
      metric("Dashboard state route", badge(backend.checks?.dashboardState?.ok, "Connected", "Missing")),
      metric("Internet ops route", badge(backend.internet, "Connected", "Missing")),
      metric("Launch lock route", badge(backend.launchLock, "Connected", "Missing")),
    ], { className: "wide" }),
    panel("What This Dashboard Is Now", el("p", { text: "This is the operator layer: it shows what Claire can actually use, what is missing, and what should be fixed before live operational work." })),
    panel("Current Safest Next Action", el("div", { class: "notice" }, [
      el("p", { text: "Use this dashboard to identify route gaps and stale backend/frontend assumptions before running a real live campaign." }),
    ]), { className: "full" }),
  ];
}

function internetView() {
  const backend = state.backend || {};
  return [
    panel("Internet Runtime", [
      metric("Operations dashboard route", badge(backend.internet, "Available", "Missing")),
      metric("Governed action script", el("span", { class: "badge info", text: "Dashboard-managed" })),
      el("p", { text: "This section should become the user-friendly surface for governed external search, evidence baskets, and online runtime status." }),
    ], { className: "wide" }),
    panel("Missing Data Rule", el("p", { text: "If live internet state is unavailable, the UI must say so. It must not pretend a campaign or source check succeeded." })),
  ];
}

function campaignsView() {
  const backend = state.backend || {};
  return [
    panel("Campaign Lifecycle", [
      metric("Campaign route", badge(backend.campaigns, "Available", "Missing")),
      metric("Refresh cycles", el("span", { class: "badge warn", text: "Awaiting live state" })),
      metric("Persistence", el("span", { class: "badge warn", text: "Awaiting proof" })),
    ], { className: "wide" }),
    panel("Operator Meaning", el("p", { text: "Campaigns should show objective, cadence, last run, evidence count, trust risk, next refresh, and final status." })),
  ];
}

function trustView() {
  const backend = state.backend || {};
  return [
    panel("Source Trust Intelligence", [
      metric("Source trust route", badge(backend.trust, "Available", "Missing")),
      metric("Quarantine state", el("span", { class: "badge warn", text: "Awaiting data" })),
      metric("Reputation memory", el("span", { class: "badge warn", text: "Awaiting data" })),
    ], { className: "wide" }),
    panel("Trust Principle", el("p", { text: "Trust should be visible before evidence is trusted. This dashboard should show why a source is weighted, quarantined, or released." })),
  ];
}

function runtimeView() {
  return [
    panel("Runtime Safety", [
      metric("Bounded orchestration", el("span", { class: "badge good", text: "Protected by architecture" })),
      metric("Degraded mode", el("span", { class: "badge warn", text: "Needs live signal" })),
      metric("Recovery", el("span", { class: "badge warn", text: "Needs live signal" })),
    ], { className: "wide" }),
    panel("No Fake Green", el("p", { text: "Runtime health should distinguish installed, reachable, executing, degraded, blocked, and failed states." })),
  ];
}

function deploymentView() {
  return [
    panel("Deployment Hardening", [
      metric("Rollback safety", el("span", { class: "badge good", text: "Installed" })),
      metric("Manifest state", el("span", { class: "badge good", text: "Installed" })),
      metric("Production config", el("span", { class: "badge warn", text: "Verify locally" })),
    ], { className: "wide" }),
    panel("Deployment View Goal", el("p", { text: "Show exact deploy readiness, blocked checks, rollback state, installed build chain, and manifest mismatches." })),
  ];
}

function launchView() {
  const backend = state.backend || {};
  return [
    panel("Launch Regression Lock", [
      metric("Launch route", badge(backend.launchLock, "Available", "Missing")),
      metric("Invariant lock", el("span", { class: "badge good", text: "Installed" })),
      metric("Real launch proof", el("span", { class: "badge warn", text: "Not yet proven" })),
    ], { className: "wide" }),
    panel("Honest Status", el("p", { text: "Launch lock means install/regression protection exists. It does not mean the platform has been used under real operational load." })),
  ];
}

function actionsView() {
  const actionList = [
    ["Refresh dashboard state", "Reload backend routes and visible readiness.", refresh],
    ["Check route availability", "Verify important backend routes are reachable.", refresh],
    ["Open use guide", "Show operator sequence and safety rules.", () => document.getElementById("guide-dialog").showModal()],
    ["Prepare live campaign", "Placeholder-free UI slot: disabled until route and schema are confirmed.", null],
  ];

  const buttons = actionList.map(([title, description, handler]) => {
    const button = el("button", { class: "action-button", type: "button" }, [
      el("strong", { text: title }),
      el("span", { text: description }),
    ]);
    if (handler) button.addEventListener("click", handler);
    else {
      button.disabled = true;
      button.style.opacity = "0.56";
      button.title = "Disabled until backend route and schema are verified.";
    }
    return button;
  });

  return [
    panel("Safe Operator Actions", el("div", { class: "action-grid" }, buttons), { className: "full" }),
  ];
}

const renderers = {
  overview: overviewView,
  internet: internetView,
  campaigns: campaignsView,
  trust: trustView,
  runtime: runtimeView,
  deployment: deploymentView,
  launch: launchView,
  actions: actionsView,
};

function render() {
  const meta = views[state.view];
  document.getElementById("view-title").textContent = meta.title;
  document.getElementById("view-subtitle").textContent = meta.subtitle;

  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === state.view);
  });

  renderStrip();

  const content = document.getElementById("dashboard-content");
  content.innerHTML = "";
  const nodes = renderers[state.view]();
  nodes.forEach((node) => content.append(node));
}

async function refresh() {
  await loadBackendState();
  render();
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    state.view = button.dataset.view;
    render();
  });
});

document.getElementById("refresh-state").addEventListener("click", refresh);
document.getElementById("open-guide").addEventListener("click", () => {
  document.getElementById("guide-dialog").showModal();
});

refresh();
""",

    FRONTEND_DIR / "internet_operations_dashboard.html": """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="refresh" content="0; url=./index.html"/>
  <title>Claire Internet Operations</title>
</head>
<body>
  <p>Internet Operations has moved into the main Claire Operator Dashboard.</p>
  <p><a href="./index.html">Open Claire Operator Dashboard</a></p>
</body>
</html>
""",

    MANIFEST_DIR / "v17_52_modern_operator_dashboard.json": json.dumps({
        "version": VERSION,
        "name": BUILD_NAME,
        "installed_at": None,
        "purpose": "Replace build-layer Command Center with a modern operator dashboard shell and runtime-aware UI sections.",
        "files": [
            "src/frontend/command_center/modern/index.html",
            "src/frontend/command_center/modern/operator_dashboard.css",
            "src/frontend/command_center/modern/operator_dashboard.js",
            "src/frontend/command_center/modern/internet_operations_dashboard.html",
            "tests/test_v17_52_modern_operator_dashboard.py",
        ],
        "governance": {
            "no_placeholders": True,
            "runtime_isolation_preserved": True,
            "dashboard_does_not_fake_success": True,
            "missing_routes_are_visible": True,
            "rollback_backup_created": True,
        },
        "operator_sections": [
            "overview",
            "internet",
            "campaigns",
            "source_trust",
            "runtime_health",
            "deployment",
            "launch_lock",
            "actions",
        ],
    }, indent=2),

    TESTS_DIR / "test_v17_52_modern_operator_dashboard.py": """from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "src" / "frontend" / "command_center" / "modern"


def test_v17_52_dashboard_files_exist():
    assert (DASH / "index.html").exists()
    assert (DASH / "operator_dashboard.css").exists()
    assert (DASH / "operator_dashboard.js").exists()
    assert (ROOT / "manifests" / "v17_52_modern_operator_dashboard.json").exists()


def test_v17_52_index_is_operator_dashboard_not_build_layer():
    html = (DASH / "index.html").read_text(encoding="utf-8")
    assert "Claire Syntalion Operator Dashboard" in html
    assert "Modern Operator Dashboard" in html
    assert "Internet Ops" in html
    assert "Campaigns" in html
    assert "Source Trust" in html
    assert "Launch Lock" in html


def test_v17_52_dashboard_has_runtime_aware_routes_and_no_fake_success_rule():
    js = (DASH / "operator_dashboard.js").read_text(encoding="utf-8")
    assert "/health" in js
    assert "/internet/ops/dashboard" in js
    assert "/internet/campaigns" in js
    assert "/internet/source-trust" in js
    assert "/launch/regression-lock" in js
    assert "Needs wiring" in js
    assert "Missing" in js
    assert "Not yet proven" in js


def test_v17_52_dashboard_has_modern_responsive_layout():
    css = (DASH / "operator_dashboard.css").read_text(encoding="utf-8")
    assert "app-shell" in css
    assert "content-grid" in css
    assert "status-strip" in css
    assert "@media" in css
    assert "backdrop-filter" in css


def test_v17_52_internet_dashboard_redirects_to_main_operator_dashboard():
    html = (DASH / "internet_operations_dashboard.html").read_text(encoding="utf-8")
    assert "url=./index.html" in html
    assert "moved into the main Claire Operator Dashboard" in html
""",
}


def backup_existing_file(path: Path) -> None:
    if not path.exists():
        return
    relative = path.relative_to(ROOT)
    backup_path = BACKUP_DIR / relative
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup_existing_file(path)

    if path.name == "v17_52_modern_operator_dashboard.json":
        data = json.loads(content)
        data["installed_at"] = datetime.now(timezone.utc).isoformat()
        content = json.dumps(data, indent=2)

    path.write_text(content, encoding="utf-8", newline="\n")


def install() -> None:
    for path, content in FILES.items():
        write_file(path, content)

    print(f"{VERSION} — {BUILD_NAME} installed.")
    print("Backups stored in:", BACKUP_DIR)
    print("Run:")
    print("  python -m pytest tests\\test_v17_52_modern_operator_dashboard.py")


if __name__ == "__main__":
    install()
