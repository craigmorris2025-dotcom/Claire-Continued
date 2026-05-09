/**
 * Claire Syntalion — Pipeline Tab
 * Submit evaluation, render radar + bar charts, engine detail accordion,
 * acquirer match list, JSON/CSV export.
 */
const Pipeline = (() => {
    let pipelineChart = null;
    let radarChart = null;
    let lastResult = null;

    // Character counter
    document.addEventListener('DOMContentLoaded', () => {
        const input = document.getElementById('eval-input');
        const counter = document.getElementById('eval-char-count');
        if (input && counter) {
            input.addEventListener('input', () => {
                counter.textContent = `${input.value.length} characters`;
            });
        }
    });

    // Radar chart dimension groups
    const RADAR_GROUPS = {
        'Market Intelligence':   ['market_score', 'competitive_score', 'strategy_score'],
        'Innovation & Tech':     ['innovation_score', 'engineering_score', 'breakthrough_score'],
        'Financial Viability':   ['financial_score', 'deal_score', 'forecasting_score'],
        'Risk & Compliance':     ['risk_score', 'compliance_score'],
        'Strategic Fit':         ['synergy_score', 'acquirer_matching_score', 'portfolio_engine_score'],
        'Data Quality':          ['ingestion_score', 'semantic_score', 'fusion_score'],
    };

    function computeRadarData(scores) {
        const labels = [];
        const values = [];
        for (const [group, keys] of Object.entries(RADAR_GROUPS)) {
            const vals = keys.map(k => scores[k] || 0).filter(v => v > 0);
            labels.push(group);
            values.push(vals.length ? vals.reduce((a, b) => a + b) / vals.length : 0);
        }
        return { labels, values };
    }

    async function runEvaluation() {
        const input = document.getElementById('eval-input').value.trim();
        if (!input || input.length < 3) {
            alert('Please enter at least 3 characters.');
            return;
        }
        const mode = document.getElementById('eval-mode').value;
        const reqType = document.getElementById('eval-type').value;
        const btn = document.getElementById('btn-evaluate');
        const resultsDiv = document.getElementById('pipeline-results');

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Running 24 engines...';
        resultsDiv.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border text-info"></div>
                <p class="mt-2 mb-1">Processing through 24 engines across 6 phases...</p>
                <div class="progress mx-auto" style="width:60%;height:4px">
                    <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" style="width:100%"></div>
                </div>
            </div>`;

        try {
            const result = await API.evaluate({
                input_text: input,
                mode: mode,
                request_type: reqType,
            });
            lastResult = result;

            // Summary
            const cls = result.decision_classification || 'UNKNOWN';
            const clsColor = cls === 'GO' ? 'success' : cls === 'CAUTION' ? 'warning' : 'danger';
            const brkCls = result.breakthrough_classification || '';
            const brkColor = brkCls === 'HIGH' ? 'warning' : brkCls === 'MODERATE' ? 'info' : 'secondary';

            resultsDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <span class="badge bg-${clsColor} fs-6 me-2 px-3 py-2">${cls}</span>
                        <span class="badge bg-${brkColor} fs-6 px-3 py-2">${brkCls} Breakthrough</span>
                    </div>
                    <div class="text-end">
                        <small class="text-muted">Run:</small>
                        <code class="text-info">${result.run_id || ''}</code>
                    </div>
                </div>
                <div class="row g-2 text-center">
                    <div class="col"><small class="text-muted d-block">Confidence</small><strong>${(result.confidence || 0).toFixed(3)}</strong></div>
                    <div class="col"><small class="text-muted d-block">Domain</small><span class="badge bg-info bg-opacity-25 text-info">${result.domain || 'general'}</span></div>
                    <div class="col"><small class="text-muted d-block">Syntalion</small><strong class="${result.syntalion_ready ? 'text-success' : 'text-warning'}">${result.syntalion_ready ? 'READY' : 'NOT READY'}</strong></div>
                    <div class="col"><small class="text-muted d-block">Mode</small><span class="badge bg-secondary">${result.mode}</span></div>
                    <div class="col"><small class="text-muted d-block">Keywords</small><strong>${(result.keywords || []).length}</strong></div>
                    <div class="col"><small class="text-muted d-block">Acquirers</small><strong>${(result.acquirer_matches || []).length}</strong></div>
                </div>
                ${result.connector_sources ? `
                <div class="mt-2 text-center">
                    <small class="text-muted">Connectors: </small>
                    ${Object.entries(result.connector_sources || {}).map(([k,v]) =>
                        `<span class="badge bg-dark border border-secondary me-1">${k}: ${v}</span>`
                    ).join('')}
                </div>` : ''}
            `;

            // Show export buttons
            document.getElementById('export-buttons').style.display = '';

            // Charts
            const scores = result.scores || {};
            const keys = Object.keys(scores).filter(k => !k.startsWith('_'));

            if (keys.length > 0) {
                document.getElementById('charts-row').style.display = '';

                // Radar chart
                const radar = computeRadarData(scores);
                const radarCtx = document.getElementById('chart-radar');
                if (radarChart) radarChart.destroy();
                radarChart = new Chart(radarCtx, {
                    type: 'radar',
                    data: {
                        labels: radar.labels,
                        datasets: [{
                            label: 'Score',
                            data: radar.values,
                            backgroundColor: 'rgba(88,166,255,0.15)',
                            borderColor: '#58a6ff',
                            borderWidth: 2,
                            pointBackgroundColor: radar.values.map(v => scoreColor(v)),
                            pointRadius: 5,
                        }],
                    },
                    options: {
                        responsive: true,
                        scales: {
                            r: {
                                beginAtZero: true, max: 1,
                                grid: { color: '#30363d' },
                                angleLines: { color: '#30363d' },
                                pointLabels: { color: '#c9d1d9', font: { size: 10 } },
                                ticks: { display: false },
                            }
                        },
                        plugins: { legend: { display: false } },
                    },
                });

                // Bar chart
                const barCtx = document.getElementById('chart-pipeline');
                if (pipelineChart) pipelineChart.destroy();
                const sortedKeys = keys.sort((a, b) => scores[b] - scores[a]);
                pipelineChart = new Chart(barCtx, {
                    type: 'bar',
                    data: {
                        labels: sortedKeys.map(k => k.replace(/_score$/,'').replace(/_/g, ' ')),
                        datasets: [{
                            label: 'Score',
                            data: sortedKeys.map(k => scores[k]),
                            backgroundColor: sortedKeys.map(k => scoreColor(scores[k])),
                            borderRadius: 3,
                        }],
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        scales: {
                            x: { beginAtZero: true, max: 1, ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
                            y: { ticks: { color: '#c9d1d9', font: { size: 9 } }, grid: { display: false } },
                        },
                        plugins: { legend: { display: false } },
                    },
                });
            }

            // Acquirer matches
            renderAcquirerMatches(result.acquirer_matches || []);

            // Engine details accordion
            renderEngineDetails(result.engine_details || {}, scores);

            // Raw JSON
            document.getElementById('pipeline-detail').style.display = '';
            document.getElementById('pipeline-json').textContent = JSON.stringify(result, null, 2);

            // Refresh other tabs
            Dashboard.load();
            History.refresh();
        } catch (e) {
            resultsDiv.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-1"></i>${e.message}</div>`;
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Run Pipeline';
        }
    }

    function renderAcquirerMatches(matches) {
        const container = document.getElementById('acquirer-results');
        const list = document.getElementById('acquirer-match-list');
        if (!matches.length) { container.style.display = 'none'; return; }
        container.style.display = '';

        list.innerHTML = matches.slice(0, 8).map((m, i) => {
            const pct = Math.round((m.match_score || 0) * 100);
            const color = pct >= 65 ? 'success' : pct >= 35 ? 'warning' : 'danger';
            const rank = i + 1;
            const focus = (m.matched_focus || m.focus || []).slice(0, 4);
            return `
            <a href="#" class="list-group-item list-group-item-action bg-dark border-secondary"
               onclick="event.preventDefault(); Pipeline.showAcquirerModal(${JSON.stringify(m).replace(/"/g, '&quot;')})">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-dark border border-${color} me-2">#${rank}</span>
                        <strong>${m.name || m.ticker}</strong>
                        <code class="text-muted ms-2">${m.ticker || ''}</code>
                    </div>
                    <div>
                        <span class="badge bg-${color} fs-6">${pct}%</span>
                    </div>
                </div>
                <div class="mt-1">
                    <div class="progress" style="height:4px">
                        <div class="progress-bar bg-${color}" style="width:${pct}%"></div>
                    </div>
                </div>
                <div class="mt-1">
                    ${focus.map(f => `<span class="badge bg-secondary bg-opacity-50 me-1 small">${f}</span>`).join('')}
                </div>
            </a>`;
        }).join('');
    }

    function renderEngineDetails(details, scores) {
        const container = document.getElementById('engine-detail-card');
        const accordion = document.getElementById('engine-details-accordion');
        if (!Object.keys(details).length) { container.style.display = 'none'; return; }
        container.style.display = '';

        const phases = [
            ['Ingestion & Semantic', ['ingestion', 'semantic', 'fusion']],
            ['Intel Scoring', ['company', 'engineering', 'product', 'customer', 'competitive', 'operational', 'financial']],
            ['Strategic Analysis', ['synergy', 'strategy', 'risk', 'market']],
            ['Innovation & Breakthrough', ['innovation', 'breakthrough', 'predictive', 'forecasting']],
            ['Deal Construction', ['deal', 'decision', 'discovery', 'acquirer_matching']],
            ['Portfolio & Compliance', ['portfolio', 'compliance']],
        ];

        let html = '';
        let idx = 0;
        for (const [phaseName, engines] of phases) {
            for (const eng of engines) {
                const d = details[eng];
                if (!d) continue;
                const score = d.score || scores[eng + '_score'] || 0;
                const color = scoreColor(score);
                const pct = Math.round(score * 100);
                const id = `detail-${idx++}`;
                const detailEntries = Object.entries(d)
                    .filter(([k]) => !['score', 'phase'].includes(k))
                    .map(([k, v]) => {
                        const display = Array.isArray(v) ? v.join(', ') : (typeof v === 'number' ? v.toFixed(3) : String(v));
                        return `<tr><td class="text-muted small">${k.replace(/_/g, ' ')}</td><td class="small">${display}</td></tr>`;
                    }).join('');

                html += `
                <div class="accordion-item bg-dark border-secondary">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed bg-dark text-light py-2 px-3" type="button"
                                data-bs-toggle="collapse" data-bs-target="#${id}">
                            <span class="me-auto">${eng.replace(/_/g, ' ')}</span>
                            <span class="badge me-2" style="background:${color};color:#0d1117">${pct}%</span>
                            <small class="text-muted">${phaseName}</small>
                        </button>
                    </h2>
                    <div id="${id}" class="accordion-collapse collapse">
                        <div class="accordion-body p-2">
                            <table class="table table-dark table-sm mb-0">
                                <tbody>${detailEntries}</tbody>
                            </table>
                        </div>
                    </div>
                </div>`;
            }
        }
        accordion.innerHTML = html;
    }

    function showAcquirerModal(acq) {
        document.getElementById('modal-acq-name').textContent = `${acq.name} (${acq.ticker})`;
        const body = document.getElementById('modal-acq-body');

        const matchPct = Math.round((acq.match_score || 0) * 100);
        const mColor = matchPct >= 65 ? 'success' : matchPct >= 35 ? 'warning' : 'danger';

        body.innerHTML = `
            <div class="row g-3 mb-3">
                <div class="col-md-4 text-center">
                    <h6 class="text-muted">Match Score</h6>
                    <h1 class="text-${mColor}">${matchPct}%</h1>
                    <div class="progress" style="height:6px">
                        <div class="progress-bar bg-${mColor}" style="width:${matchPct}%"></div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="row g-2 text-center">
                        ${makeMetric('Fit', acq.fit)}
                        ${makeMetric('Capacity', acq.capacity)}
                        ${makeMetric('Strategy', acq.strategy_alignment)}
                        ${makeMetric('Tech', acq.tech_alignment)}
                    </div>
                </div>
            </div>
            <hr class="border-secondary">
            <div class="row g-3">
                <div class="col-md-6">
                    <h6 class="text-info"><i class="bi bi-tag me-1"></i>Sector</h6>
                    <p>${acq.sector || 'N/A'}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-info"><i class="bi bi-crosshair me-1"></i>Domain Match</h6>
                    <p>${acq.domain_match ? '<span class="badge bg-success">Yes</span>' : '<span class="badge bg-secondary">No</span>'}</p>
                </div>
            </div>
            <h6 class="text-info mt-2"><i class="bi bi-bullseye me-1"></i>Focus Areas</h6>
            <div class="mb-2">
                ${(acq.focus || []).map(f => {
                    const matched = (acq.matched_focus || []).includes(f);
                    return `<span class="badge ${matched ? 'bg-info' : 'bg-secondary bg-opacity-50'} me-1 mb-1">${matched ? '<i class="bi bi-check-circle me-1"></i>' : ''}${f}</span>`;
                }).join('')}
            </div>
        `;

        new bootstrap.Modal(document.getElementById('acquirerModal')).show();
    }

    function makeMetric(label, value) {
        const v = value || 0;
        const pct = Math.round(v * 100);
        return `<div class="col-3">
            <small class="text-muted d-block">${label}</small>
            <strong>${pct}%</strong>
            <div class="progress mt-1" style="height:3px">
                <div class="progress-bar" style="width:${pct}%;background:${scoreColor(v)}"></div>
            </div>
        </div>`;
    }

    function scoreColor(v) {
        if (v >= 0.65) return '#3fb950';
        if (v >= 0.35) return '#d29922';
        return '#f85149';
    }

    function exportJSON() {
        if (!lastResult) return;
        const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
        downloadBlob(blob, `claire_${lastResult.run_id || 'result'}.json`);
    }

    function exportCSV() {
        if (!lastResult) return;
        const scores = lastResult.scores || {};
        const keys = Object.keys(scores).filter(k => !k.startsWith('_'));
        let csv = 'Engine,Score\n';
        keys.sort((a, b) => scores[b] - scores[a]);
        for (const k of keys) csv += `${k},${scores[k]}\n`;
        csv += `\nDecision,${lastResult.decision_classification}\n`;
        csv += `Breakthrough,${lastResult.breakthrough_classification}\n`;
        csv += `Domain,${lastResult.domain}\n`;
        csv += `\nAcquirer,Ticker,Match Score\n`;
        for (const m of (lastResult.acquirer_matches || []).slice(0, 12)) {
            csv += `${m.name},${m.ticker},${m.match_score}\n`;
        }
        const blob = new Blob([csv], { type: 'text/csv' });
        downloadBlob(blob, `claire_${lastResult.run_id || 'result'}.csv`);
    }

    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = filename;
        document.body.appendChild(a); a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function toggleDetails() {
        const items = document.querySelectorAll('#engine-details-accordion .accordion-collapse');
        const allOpen = Array.from(items).every(el => el.classList.contains('show'));
        items.forEach(el => {
            if (allOpen) el.classList.remove('show');
            else el.classList.add('show');
        });
    }

    return { runEvaluation, exportJSON, exportCSV, showAcquirerModal, toggleDetails };
})();
