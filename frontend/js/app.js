/**
 * Claire Syntalion — App Initializer
 * Boots the SPA: health check, connector status, tab change listeners.
 */
(async function init() {
    // Health check
    const badge = document.getElementById('health-badge');
    try {
        const health = await API.getHealth();
        const ok = health.status === 'healthy';
        badge.className = `badge bg-${ok ? 'success' : 'warning'} me-2`;
        badge.innerHTML = `<i class="bi bi-circle-fill me-1"></i>${health.passed}/${health.total} OK`;
        badge.title = `Status: ${health.status}`;
    } catch (e) {
        badge.className = 'badge bg-danger me-2';
        badge.innerHTML = '<i class="bi bi-circle-fill me-1"></i>Offline';
    }

    // Connector status
    const connBadge = document.getElementById('connector-badge');
    try {
        const conn = await API.getConnectors();
        const count = conn.count || 0;
        connBadge.className = `badge bg-${count > 0 ? 'info' : 'secondary'} me-2`;
        connBadge.innerHTML = `<i class="bi bi-plug me-1"></i>${count} Connectors`;
        connBadge.title = (conn.available || []).join(', ');
    } catch (e) {
        connBadge.innerHTML = '<i class="bi bi-plug me-1"></i>—';
    }

    // Load default tab data
    await Dashboard.load();

    // Tab change listeners — lazy load
    const tabMap = {
        'engines-tab':  () => Engines.load(),
        'modes-tab':    () => Modes.load(),
        'history-tab':  () => History.refresh(),
        'dashboard-tab':() => Dashboard.load(),
    };

    document.querySelectorAll('#mainTabs button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', () => {
            const loader = tabMap[tab.id];
            if (loader) loader();
        });
    });
})();
