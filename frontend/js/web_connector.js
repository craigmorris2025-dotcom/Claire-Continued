/**
 * ClaireWebConnector — Browser-side web access through the backend proxy.
 * Routes outbound requests through /api/proxy to avoid CORS.
 * Provides real-time data for dashboard widgets and engine feeds.
 */
const ClaireWebConnector = (() => {
    const API_BASE = '';

    /**
     * Proxy a GET request through the backend.
     * @param {string} url - Target URL to fetch
     * @param {Object} params - Query parameters
     * @param {boolean} useCache - Whether to use server-side cache
     * @returns {Promise<Object|null>}
     */
    async function proxyGet(url, params = {}, useCache = true) {
        try {
            const query = new URLSearchParams({
                url: url,
                use_cache: useCache.toString(),
                ...params
            });
            const resp = await fetch(`${API_BASE}/api/proxy/get?${query}`);
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            console.warn('WebConnector proxy GET failed:', e);
            return null;
        }
    }

    /**
     * Proxy a POST request through the backend.
     */
    async function proxyPost(url, payload = {}) {
        try {
            const resp = await fetch(`${API_BASE}/api/proxy/post`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, payload })
            });
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            console.warn('WebConnector proxy POST failed:', e);
            return null;
        }
    }

    /**
     * Check connectivity status — tests if backend can reach the internet.
     */
    async function checkConnectivity() {
        try {
            const resp = await fetch(`${API_BASE}/api/proxy/ping`);
            if (!resp.ok) return { online: false, reason: 'Backend unreachable' };
            return await resp.json();
        } catch (e) {
            return { online: false, reason: e.message };
        }
    }

    /**
     * Fetch connector-specific live data through the backend.
     * @param {string} connectorName - 'market', 'patent', or 'financial'
     * @param {Object} query - Connector-specific query params
     * @param {string} mode - 'connected', 'hybrid', or 'deterministic'
     */
    async function fetchConnectorData(connectorName, query = {}, mode = 'connected') {
        try {
            const resp = await fetch(`${API_BASE}/api/connectors/${connectorName}/fetch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, mode })
            });
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            console.warn(`Connector ${connectorName} fetch failed:`, e);
            return null;
        }
    }

    /**
     * Get status of all connectors.
     */
    async function getConnectorStatus() {
        try {
            const resp = await fetch(`${API_BASE}/api/connectors/status`);
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) { return null; }
    }

    return {
        proxyGet,
        proxyPost,
        checkConnectivity,
        fetchConnectorData,
        getConnectorStatus,
    };
})();
