/**
 * Lifecycle Stage Card Widget
 * ==============================
 * ACS2-Claire / Syntalion — v10.3.2
 *
 * Compact card for individual lifecycle stage display.
 * Shows stage number, name, status, duration, and evidence count.
 */

class LifecycleStageCard {
    constructor(stage = {}) {
        this.stage = stage;
    }

    render() {
        const s = this.stage;
        const el = document.createElement("div");
        el.className = "claire-card lifecycle-stage-card";
        el.style.cssText = "padding: 12px;";

        const statusColors = {
            completed: "var(--claire-accent-green)",
            skipped: "var(--claire-accent-yellow)",
            skipped_by_route: "var(--claire-accent-yellow)",
            in_progress: "var(--claire-accent-blue)",
            failed: "var(--claire-accent-red)",
            pending: "var(--claire-text-muted)",
            deferred: "var(--claire-accent-purple)",
        };
        const color = statusColors[s.status] || statusColors.pending;

        el.innerHTML = `
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span style="width:28px;height:28px;border-radius:50%;background:${color}22;color:${color};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">${s.stage_number || "?"}</span>
                <span style="font-weight:600;font-size:13px;flex:1">${s.stage_name || "Stage " + (s.stage_number || "?")}</span>
                <span class="claire-badge" style="background:${color}22;color:${color};font-size:10px">${(s.status || "pending").toUpperCase()}</span>
            </div>
            ${s.duration_ms ? `<div style="font-size:11px;color:var(--claire-text-muted)">Duration: ${s.duration_ms}ms</div>` : ""}
            ${s.evidence_ids ? `<div style="font-size:11px;color:var(--claire-text-muted)">Evidence: ${s.evidence_ids.length} items</div>` : ""}
            ${s.skip_reason ? `<div style="font-size:11px;color:var(--claire-accent-yellow);margin-top:4px">Skip: ${s.skip_reason}</div>` : ""}
        `;
        return el;
    }

    update(stage) {
        this.stage = stage;
    }

    static create(stage) {
        return new LifecycleStageCard(stage);
    }
}
