/**
 * Technology Panel — Technology Intelligence UI
 * ================================================
 * ACS2-Claire / Syntalion — v10.3.2
 */

class TechnologyPanel {
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
                        <h1 class="claire-panel-title">Technology</h1>
                        <p class="claire-panel-subtitle">Technology stack assessment, compatibility analysis, deployment viability</p>
                    </div>
                </div>
                <div class="claire-grid-3">
                    <div class="claire-card">
                        <div class="claire-card-title">Stack Score</div>
                        <div class="tech-stack-score" style="font-size:36px;font-weight:700;margin-top:8px;color:var(--claire-text-muted)">—</div>
                    </div>
                    <div class="claire-card">
                        <div class="claire-card-title">Compatibility</div>
                        <div class="tech-compat-score" style="font-size:36px;font-weight:700;margin-top:8px;color:var(--claire-text-muted)">—</div>
                    </div>
                    <div class="claire-card">
                        <div class="claire-card-title">Deploy Viability</div>
                        <div class="tech-deploy-score" style="font-size:36px;font-weight:700;margin-top:8px;color:var(--claire-text-muted)">—</div>
                    </div>
                </div>
                <div class="claire-card" style="margin-top:16px">
                    <div class="claire-card-header"><span class="claire-card-title">Technology Assessment</span></div>
                    <div class="tech-assessment">
                        <p style="color:var(--claire-text-muted)">Run a technology-aware evaluation to populate assessment data.</p>
                    </div>
                </div>
            </div>`;
        this._unsubs.push(this.state.subscribe("lastRun", (d) => this.refresh(d)));
    }

    unmount() { this._unsubs.forEach((fn) => fn()); this._unsubs = []; if (this.container) this.container.innerHTML = ""; }
    refresh(data) {
        if (!this.container || !data) return;
        const scores = data.scores || {};
        const ts = this.container.querySelector(".tech-stack-score");
        if (ts && scores.technical_feasibility !== undefined) {
            ts.textContent = scores.technical_feasibility;
            ts.style.color = scores.technical_feasibility >= 60 ? "var(--claire-accent-green)" : "var(--claire-accent-yellow)";
        }
    }
}
