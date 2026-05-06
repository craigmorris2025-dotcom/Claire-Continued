/**
 * Trend Panel — Trend / Thesis Display
 * ======================================
 * ACS2-Claire / Syntalion — v10.3.2
 */

class TrendPanel {
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
                        <h1 class="claire-panel-title">Trends</h1>
                        <p class="claire-panel-subtitle">Trend detection, thesis generation, and convergence mapping</p>
                    </div>
                </div>
                <div class="claire-grid-2">
                    <div class="claire-card">
                        <div class="claire-card-header"><span class="claire-card-title">Active Trends</span></div>
                        <div class="trend-list"><p style="color:var(--claire-text-muted)">No trends detected yet.</p></div>
                    </div>
                    <div class="claire-card">
                        <div class="claire-card-header"><span class="claire-card-title">Thesis Timeline</span></div>
                        <div class="thesis-timeline"><p style="color:var(--claire-text-muted)">Run evaluations to build thesis history.</p></div>
                    </div>
                </div>
            </div>`;
        this._unsubs.push(this.state.subscribe("lastRun", (d) => this.refresh(d)));
    }

    unmount() { this._unsubs.forEach((fn) => fn()); this._unsubs = []; if (this.container) this.container.innerHTML = ""; }
    refresh(data) {
        if (!this.container || !data) return;
        const tl = this.container.querySelector(".trend-list");
        const meta = data.metadata || {};
        if (tl && meta.trends) {
            tl.innerHTML = (meta.trends || []).map((t) => `
                <div class="claire-card" style="margin-bottom:8px;padding:10px">
                    <div style="font-weight:600;font-size:13px">${t.name || t}</div>
                    <div style="font-size:12px;color:var(--claire-text-muted)">${t.strength || ""}</div>
                </div>
            `).join("") || "<p style=\"color:var(--claire-text-muted)\">No trends detected.</p>";
        }
    }
}
