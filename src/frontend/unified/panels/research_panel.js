/**
 * Research Panel — Evidence & Source Intelligence Surface
 * ========================================================
 * ACS2-Claire / Syntalion — v10.3.2
 */

class ResearchPanel {
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
        const list = this.container.querySelector(".evidence-list");
        if (list) list.innerHTML = this._renderEvidence(data.evidence || []);
    }

    _render() {
        return `
            <div class="claire-panel">
                <div class="claire-panel-header">
                    <div>
                        <h1 class="claire-panel-title">Research</h1>
                        <p class="claire-panel-subtitle">Source evidence, credibility assessment, and provenance tracking</p>
                    </div>
                </div>
                <div class="claire-card">
                    <div class="claire-card-header"><span class="claire-card-title">Evidence Items</span></div>
                    <div class="evidence-list">
                        <p style="color:var(--claire-text-muted)">Run an evaluation to populate evidence.</p>
                    </div>
                </div>
            </div>`;
    }

    _renderEvidence(evidence) {
        if (!evidence.length) return "<p style=\"color:var(--claire-text-muted)\">No evidence collected.</p>";
        return evidence.map((e, i) => `
            <div class="claire-card" style="margin-bottom:8px;padding:12px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-weight:600;font-size:13px">${e.source || "Source " + (i+1)}</span>
                    <span class="claire-badge claire-badge-blue">${(e.relevance || 0).toFixed(0)}%</span>
                </div>
                <p style="font-size:13px;color:var(--claire-text-secondary);margin-top:6px">${(e.content || "").substring(0, 200)}</p>
            </div>
        `).join("");
    }

    async _loadData() {
        const last = this.state.getState("lastRun");
        if (last) this.refresh(last);
    }
}
