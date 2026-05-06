/**
 * Lifecycle Panel — 30-Stage Lifecycle Viewer
 * =============================================
 * ACS2-Claire / Syntalion — v10.3.2
 *
 * Renders the complete 30-stage lifecycle with route-aware stage cards.
 * Shows stage status, skip reasons, evidence links, and progress.
 */

class LifecyclePanel {
    constructor(stateManager, apiClient, eventBus) {
        this.state = stateManager;
        this.api = apiClient;
        this.events = eventBus;
        this.container = null;
        this._unsubs = [];
    }

    mount(container) {
        this.container = container;
        this.container.innerHTML = this._render();
        this._loadData();
        this._unsubs.push(this.state.subscribe("lastRun", (d) => this.refresh(d)));
    }

    unmount() {
        this._unsubs.forEach((fn) => fn());
        this._unsubs = [];
        if (this.container) this.container.innerHTML = "";
    }

    refresh(data) {
        if (!this.container || !data) return;
        const grid = this.container.querySelector(".lifecycle-grid");
        if (grid) grid.innerHTML = this._renderStages(data);
        const pct = this.container.querySelector(".lifecycle-progress-value");
        if (pct && data.stages_completed) {
            const p = Math.round((data.stages_completed.length / 30) * 100);
            pct.textContent = p + "%";
        }
    }

    _render() {
        return `
            <div class="claire-panel">
                <div class="claire-panel-header">
                    <div>
                        <h1 class="claire-panel-title">Lifecycle</h1>
                        <p class="claire-panel-subtitle">30-stage evaluation lifecycle — route-aware execution</p>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:32px;font-weight:700" class="lifecycle-progress-value">0%</div>
                        <div style="color:var(--claire-text-secondary);font-size:12px">Complete</div>
                    </div>
                </div>
                <div class="lifecycle-grid claire-grid-3"></div>
            </div>`;
    }

    _renderStages(data) {
        const stageNames = [
            "Signal Ingestion","Source Classification","Credibility Weighting","Trend Detection",
            "Weak Signal Amplification","Discontinuity Detection","Opportunity Formation","Convergence Pattern ID",
            "Thesis Generation","Thesis Validation","Route Selection","Route Confidence Scoring",
            "Portfolio Analysis","Breakthrough Classification","Technology Assessment","Market Potential Scoring",
            "Competitive Landscape","Financial Modeling","Risk Assessment","Strategic Alignment",
            "Acquisition Target ID","Acquirer Matching","Deal Structure","Design Portal Routing",
            "Auto Design Generation","Package Construction","Evidence Compilation","Proof Binder Assembly",
            "Terminal State Resolution","Memory Commit"
        ];
        const completed = new Set(data.stages_completed || []);
        const skipped = new Set(data.stages_skipped || []);
        return stageNames.map((name, i) => {
            const num = i + 1;
            let status = "pending", badgeClass = "";
            if (completed.has(num)) { status = "completed"; badgeClass = "claire-badge-green"; }
            else if (skipped.has(num)) { status = "skipped"; badgeClass = "claire-badge-yellow"; }
            else if (num === (data.lifecycle_stage || 0)) { status = "active"; badgeClass = "claire-badge-blue"; }
            return `<div class="claire-card" style="padding:12px">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                    <span class="claire-badge ${badgeClass}" style="min-width:28px;justify-content:center">${num}</span>
                    <span style="font-size:13px;font-weight:600">${name}</span>
                </div>
                <div style="font-size:11px;color:var(--claire-text-muted);text-transform:uppercase">${status}</div>
            </div>`;
        }).join("");
    }

    async _loadData() {
        const last = this.state.getState("lastRun");
        if (last) this.refresh(last);
    }
}
