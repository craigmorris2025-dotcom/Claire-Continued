/**
 * Discover Panel — Discovery Pipeline Surface
 * ==============================================
 * ACS2-Claire / Syntalion — v10.3.2
 */

class DiscoverPanel {
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
                        <h1 class="claire-panel-title">Discover</h1>
                        <p class="claire-panel-subtitle">Signal discovery pipeline — opportunity formation and convergence detection</p>
                    </div>
                    <button class="claire-btn claire-btn-primary" data-action="scan">Start Discovery Scan</button>
                </div>
                <div class="claire-grid-3">
                    <div class="claire-card"><div class="claire-card-title">Signals Detected</div><div class="discover-signals-count" style="font-size:36px;font-weight:700;margin-top:8px">0</div></div>
                    <div class="claire-card"><div class="claire-card-title">Opportunities Formed</div><div class="discover-opps-count" style="font-size:36px;font-weight:700;margin-top:8px">0</div></div>
                    <div class="claire-card"><div class="claire-card-title">Convergence Patterns</div><div class="discover-conv-count" style="font-size:36px;font-weight:700;margin-top:8px">0</div></div>
                </div>
                <div class="claire-card" style="margin-top:16px">
                    <div class="claire-card-header"><span class="claire-card-title">Discovery Feed</span></div>
                    <div class="discover-feed"><p style="color:var(--claire-text-muted)">No discoveries yet. Start a scan to begin.</p></div>
                </div>
            </div>`;
        this.container.querySelector("[data-action=\"scan\"]")?.addEventListener("click", () => this._startScan());
        this._unsubs.push(this.state.subscribe("lastRun", (d) => this.refresh(d)));
    }

    unmount() { this._unsubs.forEach((fn) => fn()); this._unsubs = []; if (this.container) this.container.innerHTML = ""; }
    refresh(data) { /* update counts from metadata */ }
    async _startScan() {
        try { const result = await this.api.post("/discover/scan"); this.events.emit("discover:scan-complete", result); } catch (err) { console.error("[DiscoverPanel]", err); }
    }
}
