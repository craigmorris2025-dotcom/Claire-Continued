/**
 * Packages Panel — Export / Package Browser
 * ============================================
 * ACS2-Claire / Syntalion — v10.3.2
 */

class PackagesPanel {
    constructor(stateManager, apiClient, eventBus) {
        this.state = stateManager;
        this.api = apiClient;
        this.events = eventBus;
        this.container = null;
        this._unsubs = [];
    }

    mount(container) {
        this.container = container;
        this.container.innerHTML = `
            <div class="claire-panel">
                <div class="claire-panel-header">
                    <div>
                        <h1 class="claire-panel-title">Packages</h1>
                        <p class="claire-panel-subtitle">Export packages, binders, and deliverable browser</p>
                    </div>
                    <button class="claire-btn claire-btn-primary" data-action="refresh-packages">Refresh</button>
                </div>
                <div class="claire-card">
                    <div class="claire-card-header"><span class="claire-card-title">Available Packages</span></div>
                    <table class="claire-table">
                        <thead><tr>
                            <th>Package</th><th>Type</th><th>Route</th><th>Created</th><th>Status</th>
                        </tr></thead>
                        <tbody class="packages-list"></tbody>
                    </table>
                </div>
                <div class="claire-grid-3" style="margin-top:16px">
                    <div class="claire-card" style="text-align:center">
                        <div style="font-size:32px;font-weight:700" class="pkg-total">0</div>
                        <div style="color:var(--claire-text-secondary);font-size:12px">Total Packages</div>
                    </div>
                    <div class="claire-card" style="text-align:center">
                        <div style="font-size:32px;font-weight:700" class="pkg-portfolio">0</div>
                        <div style="color:var(--claire-text-secondary);font-size:12px">Portfolio Binders</div>
                    </div>
                    <div class="claire-card" style="text-align:center">
                        <div style="font-size:32px;font-weight:700" class="pkg-acquisition">0</div>
                        <div style="color:var(--claire-text-secondary);font-size:12px">Acquisition Packages</div>
                    </div>
                </div>
            </div>`;
        this.container.querySelector("[data-action=\"refresh-packages\"]")?.addEventListener("click", () => this._loadPackages());
        this._loadPackages();
        this._unsubs.push(this.state.subscribe("lastRun", () => this._loadPackages()));
    }

    unmount() { this._unsubs.forEach((fn) => fn()); this._unsubs = []; if (this.container) this.container.innerHTML = ""; }

    refresh(data) { this._loadPackages(); }

    async _loadPackages() {
        try {
            const packages = await this.api.get("/packages");
            if (!Array.isArray(packages)) return;
            const tbody = this.container?.querySelector(".packages-list");
            if (tbody) {
                tbody.innerHTML = packages.map((p) => `
                    <tr>
                        <td>${p.name || p.id || ""}</td>
                        <td><span class="claire-badge claire-badge-blue">${p.type || ""}</span></td>
                        <td>${p.route || ""}</td>
                        <td>${p.created || ""}</td>
                        <td><span class="claire-badge claire-badge-green">${p.status || "ready"}</span></td>
                    </tr>
                `).join("");
            }
            const total = this.container?.querySelector(".pkg-total");
            if (total) total.textContent = packages.length;
            const portfolio = this.container?.querySelector(".pkg-portfolio");
            if (portfolio) portfolio.textContent = packages.filter((p) => p.type === "portfolio").length;
            const acq = this.container?.querySelector(".pkg-acquisition");
            if (acq) acq.textContent = packages.filter((p) => p.type === "acquisition").length;
        } catch (err) {
            console.warn("[PackagesPanel]", err.message);
        }
    }
}
