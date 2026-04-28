/**
 * Claire Syntalion — Modes Tab
 * Displays available operating modes as interactive cards.
 */
const Modes = (() => {
    const MODE_META = {
        deterministic: {
            icon: 'bi-shield-lock-fill',
            color: 'success',
            subtitle: 'Air-Gapped Processing',
        },
        connected: {
            icon: 'bi-wifi',
            color: 'info',
            subtitle: 'Live Data Integration',
        },
        hybrid: {
            icon: 'bi-layers-fill',
            color: 'warning',
            subtitle: 'Full Capability',
        },
    };

    async function load() {
        const grid = document.getElementById('modes-grid');
        try {
            const data = await API.getModes();
            const modes = data.modes || [];
            let html = '';
            for (const m of modes) {
                const meta = MODE_META[m.mode] || { icon: 'bi-gear', color: 'secondary', subtitle: '' };
                const caps = m.capabilities || [];
                html += `
                <div class="col-md-4">
                    <div class="card mode-card bg-dark border-${meta.color}">
                        <div class="card-body text-center">
                            <i class="bi ${meta.icon} fs-1 text-${meta.color} d-block mb-2"></i>
                            <h5 class="text-${meta.color}">${m.mode.charAt(0).toUpperCase() + m.mode.slice(1)}</h5>
                            <p class="text-muted small mb-3">${meta.subtitle}</p>
                            <p class="small">${m.description || ''}</p>
                            <hr class="border-secondary">
                            <div class="text-start">
                                <small class="text-muted d-block mb-1">Capabilities (${caps.length}):</small>
                                ${caps.map(c => `<span class="badge bg-${meta.color} bg-opacity-25 text-${meta.color} me-1 mb-1">${c}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                </div>`;
            }
            grid.innerHTML = html;
        } catch (e) {
            grid.innerHTML = `<div class="col-12 alert alert-danger">${e.message}</div>`;
        }
    }

    return { load };
})();
