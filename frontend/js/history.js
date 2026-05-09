/**
 * Claire Syntalion — History Tab
 * Run history table with refresh.
 */
const History = (() => {
    async function refresh() {
        const body = document.getElementById('history-body');
        try {
            const data = await API.getHistory(25);
            const runs = data.runs || [];
            if (runs.length === 0) {
                body.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-3">No runs yet</td></tr>';
                return;
            }
            body.innerHTML = runs.map(r => {
                const cls = r.decision_class || '';
                const clsColor = cls === 'GO' ? 'success' : cls === 'CAUTION' ? 'warning' : 'danger';
                return `<tr>
                    <td><code class="text-info small">${r.run_id || ''}</code></td>
                    <td><span class="badge bg-secondary">${r.mode || ''}</span></td>
                    <td>${(r.decision_score || 0).toFixed(3)}</td>
                    <td><span class="badge bg-${clsColor}">${cls}</span></td>
                    <td>${(r.breakthrough_score || 0).toFixed(3)}</td>
                    <td>${(r.portfolio_score || 0).toFixed(3)}</td>
                    <td class="small text-muted" style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${r.input_preview || ''}</td>
                    <td class="small text-muted">${r.started_at ? new Date(r.started_at).toLocaleDateString() : ''}</td>
                </tr>`;
            }).join('');
        } catch (e) {
            body.innerHTML = `<tr><td colspan="8" class="text-center text-danger">${e.message}</td></tr>`;
        }
    }

    return { refresh };
})();
