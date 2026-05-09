/**
 * Claire Syntalion — Engines Tab
 * Displays all 24 engines in a grid grouped by phase.
 */
const Engines = (() => {
    const PHASE_COLORS = {
        ingestion_semantic: 'info',
        intel_scoring: 'primary',
        strategic_analysis: 'success',
        innovation_breakthrough: 'warning',
        deal_construction: 'danger',
        portfolio_compliance: 'secondary',
    };

    const PHASE_ICONS = {
        ingestion_semantic: 'bi-funnel',
        intel_scoring: 'bi-graph-up',
        strategic_analysis: 'bi-bullseye',
        innovation_breakthrough: 'bi-lightbulb',
        deal_construction: 'bi-briefcase',
        portfolio_compliance: 'bi-shield-check',
    };

    async function load() {
        const grid = document.getElementById('engines-grid');
        try {
            const data = await API.getEngines();
            const phases = data.phases || [];
            let html = '';
            for (const phase of phases) {
                const color = PHASE_COLORS[phase.phase] || 'secondary';
                const icon = PHASE_ICONS[phase.phase] || 'bi-gear';
                html += `
                    <div class="col-12">
                        <h6 class="text-${color} text-uppercase fw-bold mb-2">
                            <i class="bi ${icon} me-1"></i>
                            ${phase.phase.replace(/_/g, ' ')} (${phase.count})
                        </h6>
                    </div>`;
                for (const eng of phase.engines) {
                    const status = eng.registered ? 'success' : 'danger';
                    html += `
                    <div class="col-md-4 col-lg-3">
                        <div class="card engine-card bg-dark border-${color}">
                            <div class="card-body py-2 px-3">
                                <div class="d-flex justify-content-between align-items-start">
                                    <strong class="small">${eng.key.replace(/_/g, ' ')}</strong>
                                    <span class="badge bg-${status}">
                                        <i class="bi bi-circle-fill" style="font-size:0.5rem"></i>
                                    </span>
                                </div>
                                <div class="mt-1">
                                    <span class="badge bg-${color} bg-opacity-25 text-${color}">${eng.class}</span>
                                </div>
                            </div>
                        </div>
                    </div>`;
                }
            }
            html += `
                <div class="col-12 text-end">
                    <span class="badge bg-dark border border-secondary">
                        Total: ${data.total_engines} engines across ${(data.phases || []).length} phases
                    </span>
                </div>`;
            grid.innerHTML = html;
        } catch (e) {
            grid.innerHTML = `<div class="col-12 alert alert-danger">${e.message}</div>`;
        }
    }

    return { load };
})();
