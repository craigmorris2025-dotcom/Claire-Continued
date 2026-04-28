/**
 * Claire-Syntalion Updater — Self-update checking and application from the running UI.
 * Checks /api/update/status for new versions, displays notification, applies on user confirm.
 */
const ClaireUpdater = (() => {
    const API_BASE = '';
    let _checkInterval = null;
    let _currentVersion = null;

    async function checkForUpdates(silent = true) {
        try {
            const resp = await fetch(`${API_BASE}/api/update/status`);
            if (!resp.ok) return null;
            const data = await resp.json();
            _currentVersion = data.current;

            if (data.update_available && !silent) {
                showUpdateNotification(data.current.version, data.remote_version);
            } else if (data.update_available && silent) {
                showUpdateBadge(data.remote_version);
            }
            return data;
        } catch (e) {
            console.warn('Update check failed:', e);
            return null;
        }
    }

    function showUpdateBadge(remoteVersion) {
        let badge = document.getElementById('claire-update-badge');
        if (badge) return; // Already showing

        badge = document.createElement('div');
        badge.id = 'claire-update-badge';
        badge.style.cssText = `
            position: fixed; bottom: 20px; right: 20px; z-index: 10000;
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            color: white; padding: 10px 18px; border-radius: 10px;
            font-family: 'Segoe UI', system-ui, sans-serif; font-size: 0.9rem;
            cursor: pointer; box-shadow: 0 4px 16px rgba(99,102,241,0.4);
            display: flex; align-items: center; gap: 8px;
            animation: slideUp 0.5s ease-out;
        `;
        badge.innerHTML = `
            <i class="bi bi-arrow-up-circle-fill"></i>
            <span>Update available: v${remoteVersion}</span>
            <button onclick="ClaireUpdater.showDetails()" style="
                background: rgba(255,255,255,0.2); border: none; color: white;
                padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem;
            ">Details</button>
            <button onclick="this.parentElement.remove()" style="
                background: none; border: none; color: rgba(255,255,255,0.6);
                cursor: pointer; font-size: 1.1rem; padding: 0 4px;
            ">&times;</button>
        `;
        document.body.appendChild(badge);

        // Add animation keyframes if not present
        if (!document.getElementById('claire-updater-styles')) {
            const style = document.createElement('style');
            style.id = 'claire-updater-styles';
            style.textContent = `
                @keyframes slideUp {
                    from { transform: translateY(100px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    function showUpdateNotification(currentVer, remoteVer) {
        showUpdateModal(currentVer, remoteVer);
    }

    function showUpdateModal(currentVer, remoteVer) {
        let modal = document.getElementById('claire-update-modal');
        if (modal) modal.remove();

        modal = document.createElement('div');
        modal.id = 'claire-update-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7); z-index: 10001;
            display: flex; align-items: center; justify-content: center;
        `;
        modal.innerHTML = `
            <div style="
                background: #111827; border: 1px solid #1e3a5f; border-radius: 16px;
                max-width: 500px; width: 90%; padding: 2rem; color: #e0e0e0;
                font-family: 'Segoe UI', system-ui, sans-serif;
            ">
                <h4 style="margin: 0 0 1rem; color: #60a5fa;">
                    <i class="bi bi-arrow-up-circle-fill"></i> Update Available
                </h4>
                <p style="color: #94a3b8; margin-bottom: 1rem;">
                    A new version of Claire-Syntalion is available.
                </p>
                <table style="width: 100%; margin-bottom: 1.5rem; font-size: 0.9rem;">
                    <tr><td style="color: #6b7280; padding: 4px 0;">Current:</td>
                        <td style="padding: 4px 0;">v${currentVer}</td></tr>
                    <tr><td style="color: #6b7280; padding: 4px 0;">Available:</td>
                        <td style="padding: 4px 0; color: #4ade80; font-weight: 600;">v${remoteVer}</td></tr>
                </table>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button onclick="document.getElementById('claire-update-modal').remove()"
                        style="background: #374151; border: none; color: #e0e0e0;
                        padding: 8px 20px; border-radius: 8px; cursor: pointer;">
                        Later
                    </button>
                    <button onclick="ClaireUpdater.applyUpdate()"
                        style="background: linear-gradient(135deg, #3b82f6, #6366f1);
                        border: none; color: white; padding: 8px 20px; border-radius: 8px;
                        cursor: pointer; font-weight: 600;">
                        <i class="bi bi-download"></i> Update Now
                    </button>
                </div>
                <div id="claire-update-progress" style="display: none; margin-top: 1rem;">
                    <div style="background: #1e293b; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div id="claire-update-bar" style="height: 100%; width: 0%;
                            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                            border-radius: 3px; transition: width 0.5s;"></div>
                    </div>
                    <div id="claire-update-status" style="color: #94a3b8; font-size: 0.85rem;
                        margin-top: 6px; text-align: center;">Downloading...</div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async function applyUpdate() {
        const progress = document.getElementById('claire-update-progress');
        const bar = document.getElementById('claire-update-bar');
        const status = document.getElementById('claire-update-status');

        if (progress) progress.style.display = 'block';
        if (bar) bar.style.width = '30%';
        if (status) status.textContent = 'Downloading update...';

        try {
            const resp = await fetch(`${API_BASE}/api/update/apply`, { method: 'POST' });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();

            if (bar) bar.style.width = '100%';

            if (data.status === 'updated') {
                if (status) status.innerHTML = `
                    <span style="color: #4ade80;">
                        <i class="bi bi-check-circle-fill"></i>
                        Updated to v${data.version} (${data.files_updated} files).
                        ${data.restart_required ? 'Restarting...' : ''}
                    </span>
                `;
                if (data.restart_required) {
                    setTimeout(() => location.reload(), 3000);
                }
            } else if (data.status === 'already_current') {
                if (status) status.innerHTML = '<span style="color: #fbbf24;">Already up to date.</span>';
            }
        } catch (e) {
            if (bar) bar.style.width = '100%';
            if (bar) bar.style.background = '#dc3545';
            if (status) status.innerHTML = `<span style="color: #f87171;">Update failed: ${e.message}</span>`;
        }
    }

    function showDetails() {
        const badge = document.getElementById('claire-update-badge');
        if (badge) badge.remove();
        checkForUpdates(false);
    }

    async function getCacheStatus() {
        try {
            const resp = await fetch(`${API_BASE}/api/update/cache`);
            return resp.ok ? await resp.json() : null;
        } catch (e) { return null; }
    }

    async function clearCache() {
        try {
            const resp = await fetch(`${API_BASE}/api/update/cache`, { method: 'DELETE' });
            return resp.ok ? await resp.json() : null;
        } catch (e) { return null; }
    }

    function startAutoCheck(intervalMs = 3600000) {
        if (_checkInterval) clearInterval(_checkInterval);
        checkForUpdates(true);
        _checkInterval = setInterval(() => checkForUpdates(true), intervalMs);
    }

    function stopAutoCheck() {
        if (_checkInterval) {
            clearInterval(_checkInterval);
            _checkInterval = null;
        }
    }

    function getVersion() { return _currentVersion; }

    return {
        checkForUpdates,
        applyUpdate,
        showDetails,
        getCacheStatus,
        clearCache,
        startAutoCheck,
        stopAutoCheck,
        getVersion,
    };
})();

// Auto-start checking when loaded (hourly)
document.addEventListener('DOMContentLoaded', () => {
    ClaireUpdater.startAutoCheck();
});
