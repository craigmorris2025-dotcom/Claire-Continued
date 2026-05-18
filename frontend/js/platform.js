/**
 * Claire Platform Awareness — Dashboard widget showing completion state.
 * Auto-loads on startup, shows progress bar + gap list + resolve button.
 */
const Platform = (() => {
    let _status = null;

    async function load() {
        try {
            const resp = await window.ClaireCanonicalFetch.fetchLegacy('/api/platform/status');
            if (!resp.ok) return;
            _status = await resp.json();
            renderWidget();
        } catch (e) {
            console.warn('Platform status unavailable:', e);
        }
    }

    function renderWidget() {
        if (!_status) return;
        let container = document.getElementById('platform-status-widget');
        if (!container) {
            container = document.createElement('div');
            container.id = 'platform-status-widget';
            const main = document.querySelector('.tab-pane.active') || document.querySelector('main');
            if (main) main.prepend(container);
        }

        const pct = _status.completion_pct || 0;
        const gaps = _status.total_gaps || 0;
        const autoFix = _status.auto_resolvable || 0;
        const sev = _status.by_severity || {};
        const barColor = pct >= 90 ? '#3fb950' : pct >= 60 ? '#d29922' : '#f85149';

        container.innerHTML = `
            <div class="card bg-dark border-secondary mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="card-title mb-0 text-info">
                            <i class="bi bi-bullseye me-1"></i>Platform Completion
                        </h6>
                        <span class="badge bg-${pct >= 90 ? 'success' : pct >= 60 ? 'warning' : 'danger'}">
                            ${pct}% complete &rarr; v${_status.target_version}
                        </span>
                    </div>
                    <div class="progress mb-2" style="height: 8px;">
                        <div class="progress-bar" style="width: ${pct}%; background: ${barColor};" role="progressbar"></div>
                    </div>
                    <div class="d-flex gap-3 small text-muted mb-2">
                        <span><i class="bi bi-check-circle text-success me-1"></i>${(_status.resolved || []).length} resolved</span>
                        ${sev.critical ? '<span><i class="bi bi-exclamation-triangle text-danger me-1"></i>' + sev.critical + ' critical</span>' : ''}
                        ${sev.high ? '<span><i class="bi bi-exclamation-circle text-warning me-1"></i>' + sev.high + ' high</span>' : ''}
                        ${sev.medium ? '<span><i class="bi bi-info-circle text-info me-1"></i>' + sev.medium + ' medium</span>' : ''}
                        ${gaps === 0 ? '<span class="text-success fw-bold"><i class="bi bi-trophy me-1"></i>ALL CLEAR</span>' : ''}
                    </div>
                    ${autoFix > 0 ? `
                    <button class="btn btn-sm btn-outline-info" onclick="Platform.resolve()">
                        <i class="bi bi-wrench me-1"></i>Auto-Resolve ${autoFix} Gaps
                    </button>` : ''}
                    <button class="btn btn-sm btn-outline-secondary ms-1" onclick="Platform.showDetails()">
                        <i class="bi bi-list-check me-1"></i>Details
                    </button>
                    ${renderCapabilities()}
                </div>
            </div>
        `;
    }

    function renderCapabilities() {
        if (!_status || !_status.capabilities) return '';
        const caps = Object.entries(_status.capabilities);
        return `
            <div class="mt-2 pt-2 border-top border-secondary">
                <small class="text-muted d-block mb-1">Capabilities:</small>
                <div class="d-flex flex-wrap gap-1">
                    ${caps.map(([name, info]) => `
                        <span class="badge bg-${info.satisfied ? 'success' : 'danger'} bg-opacity-25
                              text-${info.satisfied ? 'success' : 'danger'}" title="${info.desc}">
                            <i class="bi bi-${info.satisfied ? 'check' : 'x'}-circle me-1"></i>${name.replace(/_/g, ' ')}
                        </span>
                    `).join('')}
                </div>
            </div>
        `;
    }

    async function resolve() {
        try {
            const resp = await window.ClaireCanonicalFetch.fetchLegacy('/api/platform/resolve', { method: 'POST' });
            const data = await resp.json();
            const msg = 'Resolved: ' + (data.resolved_count || 0) + ' gaps\nFailed: ' + (data.failed_count || 0) +
                        '\nCompletion: ' + (data.completion_before || 0) + '% -> ' + (data.completion_after || 0) + '%';
            alert(msg);
            await load();
        } catch (e) {
            alert('Resolution failed: ' + e.message);
        }
    }

    function showDetails() {
        if (!_status) return;
        let modal = document.getElementById('platform-detail-modal');
        if (modal) modal.remove();

        modal = document.createElement('div');
        modal.id = 'platform-detail-modal';
        modal.className = 'modal fade show';
        modal.style.cssText = 'display:block; background:rgba(0,0,0,0.7); z-index:10000;';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-scrollable">
                <div class="modal-content bg-dark text-light border-secondary">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title text-info"><i class="bi bi-bullseye me-2"></i>Platform Gap Analysis</h5>
                        <button class="btn-close btn-close-white" onclick="document.getElementById('platform-detail-modal').remove()"></button>
                    </div>
                    <div class="modal-body">
                        <table class="table table-dark table-sm table-hover">
                            <thead><tr><th>Severity</th><th>Category</th><th>Component</th><th>Issue</th><th>Fix</th></tr></thead>
                            <tbody>
                                ${(_status.gaps || []).map(g => `
                                    <tr>
                                        <td><span class="badge bg-${g.sev === 'critical' ? 'danger' : g.sev === 'high' ? 'warning' : g.sev === 'medium' ? 'info' : 'secondary'}">${g.sev}</span></td>
                                        <td>${g.cat}</td>
                                        <td><code>${g.comp}</code></td>
                                        <td class="small">${g.desc}</td>
                                        <td>${g.fix && g.fix.type === 'auto' ? '<span class="badge bg-success">auto</span>' : '<span class="badge bg-secondary">manual</span>'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
    }

    function getStatus() { return _status; }

    return { load, resolve, showDetails, getStatus };
})();

document.addEventListener('DOMContentLoaded', () => { Platform.load(); });
