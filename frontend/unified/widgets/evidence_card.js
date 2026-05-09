/**
 * Evidence Card Widget
 * ======================
 * ACS2-Claire / Syntalion — v10.3.2
 *
 * Card component for displaying individual evidence items with
 * source provenance, relevance scoring, and content preview.
 */

class EvidenceCard {
    constructor(evidence = {}) {
        this.evidence = evidence;
    }

    render() {
        const e = this.evidence;
        const el = document.createElement("div");
        el.className = "claire-card evidence-card";
        el.style.cssText = "padding: 14px; margin-bottom: 8px;";

        const relevance = e.relevance || 0;
        const relColor = relevance >= 80 ? "var(--claire-accent-green)" : relevance >= 50 ? "var(--claire-accent-blue)" : "var(--claire-accent-yellow)";

        el.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <div style="display:flex;align-items:center;gap:8px">
                    <span class="claire-badge claire-badge-blue">${e.source || "Unknown"}</span>
                    <span style="font-size:11px;color:var(--claire-text-muted)">${e.timestamp || ""}</span>
                </div>
                <span style="font-weight:700;color:${relColor}">${relevance}%</span>
            </div>
            <p style="font-size:13px;color:var(--claire-text-primary);line-height:1.5">${(e.content || "").substring(0, 300)}</p>
            ${e.url ? `<div style="margin-top:8px"><a href="${e.url}" style="font-size:12px;color:var(--claire-accent-cyan);text-decoration:none">${e.url}</a></div>` : ""}
        `;
        return el;
    }

    update(evidence) {
        this.evidence = evidence;
    }

    static create(evidence) {
        return new EvidenceCard(evidence);
    }
}
