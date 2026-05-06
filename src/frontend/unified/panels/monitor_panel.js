/**
 * Monitor Panel — Live Intelligence Monitor
 * ============================================
 * ACS2-Claire / Syntalion — v10.3.2
 */

class MonitorPanel {
    constructor(stateManager, apiClient, eventBus) {
        this.state = stateManager;
        this.api = apiClient;
        this.events = eventBus;
        this.container = null;
        this._unsubs = [];
        this._refreshInterval = null;
    }

    mount(container) {
        this.container = container;
        this.container.innerHTML = `
            <div class="claire-panel">
                <div class="claire-panel-header">
                    <div>
                        <h1 class="claire-panel-title">Monitor</h1>
                        <p class="claire-panel-subtitle">Live intelligence feeds, source health, and signal monitoring</p>
                    </div>
                    <div style="display:flex;gap:8px">
                        <button class="claire-btn" data-action="refresh-monitor">Refresh</button>
                        <button class="claire-btn claire-btn-primary" data-action="toggle-live">Go Live</button>
                    </div>
                </div>
                <div class="claire-grid-2">
                    <div class="claire-card">
                        <div class="claire-card-header"><span class="claire-card-title">Monitor Timeline</span></div>
                        <div class="monitor-timeline" style="max-height:400px;overflow-y:auto">
                            <p style="color:var(--claire-text-muted)">No monitor events yet.</p>
                        </div>
                    </div>
                    <div class="claire-card">
                        <div class="claire-card-header"><span class="claire-card-title">Source Health</span></div>
                        <div class="monitor-sources">
                            <p style="color:var(--claire-text-muted)">Loading source status...</p>
                        </div>
                    </div>
                </div>
                <div class="claire-card" style="margin-top:16px">
                    <div class="claire-card-header"><span class="claire-card-title">Active Signals</span></div>
                    <div class="monitor-signals"><p style="color:var(--claire-text-muted)">No active signals.</p></div>
                </div>
            </div>`;
        this.container.querySelector("[data-action=\"refresh-monitor\"]")?.addEventListener("click", () => this._loadMonitorData());
        this.container.querySelector("[data-action=\"toggle-live\"]")?.addEventListener("click", (e) => this._toggleLive(e.target));
        this._loadMonitorData();
        this._unsubs.push(this.state.subscribe("lastRun", () => this._loadMonitorData()));
    }

    unmount() {
        this._unsubs.forEach((fn) => fn()); this._unsubs = [];
        if (this._refreshInterval) { clearInterval(this._refreshInterval); this._refreshInterval = null; }
        if (this.container) this.container.innerHTML = "";
    }

    refresh(data) { this._loadMonitorData(); }

    _toggleLive(btn) {
        if (this._refreshInterval) {
            clearInterval(this._refreshInterval);
            this._refreshInterval = null;
            btn.textContent = "Go Live";
            btn.classList.remove("claire-btn-primary");
        } else {
            this._refreshInterval = setInterval(() => this._loadMonitorData(), 15000);
            btn.textContent = "Stop Live";
            btn.classList.add("claire-btn-primary");
        }
    }

    async _loadMonitorData() {
        try {
            const data = await this.api.get("/monitor/status");
            const tl = this.container?.querySelector(".monitor-timeline");
            if (tl && data.events) {
                tl.innerHTML = data.events.map((e) => `
                    <div style="padding:8px 0;border-bottom:1px solid var(--claire-border)">
                        <div style="display:flex;justify-content:space-between">
                            <span style="font-weight:600;font-size:13px">${e.type || ""}</span>
                            <span style="font-size:11px;color:var(--claire-text-muted)">${e.timestamp || ""}</span>
                        </div>
                        <div style="font-size:13px;color:var(--claire-text-secondary);margin-top:2px">${e.detail || ""}</div>
                    </div>
                `).join("");
            }
        } catch (err) {
            console.warn("[MonitorPanel]", err.message);
        }
    }
}
