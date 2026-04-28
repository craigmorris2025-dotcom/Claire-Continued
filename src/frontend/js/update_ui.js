import { apiGet, apiPost } from "./api.js";

export class UpdateUI {
    constructor() {
        this.statusBox = document.getElementById("update-status");
        this.checkBtn = document.getElementById("btn-check-updates");
        this.prepareBtn = document.getElementById("btn-prepare-update");
        this.installBtn = document.getElementById("btn-install-update");
        this.packageSelect = document.getElementById("update-package-select");

        if (!this.statusBox || !this.checkBtn || !this.prepareBtn || !this.installBtn || !this.packageSelect) {
            console.warn("UpdateUI: required elements not found in DOM.");
            return;
        }

        this._bindEvents();
    }

    _bindEvents() {
        this.checkBtn.addEventListener("click", () => this.checkUpdates());
        this.prepareBtn.addEventListener("click", () => this.prepareUpdate());
        this.installBtn.addEventListener("click", () => this.installUpdate());
    }

    async checkUpdates() {
        this._setStatus("Checking for updates...");

        const result = await apiGet("/api/update/check");

        if (!result.update_available) {
            this._setStatus("No updates available.");
            this.packageSelect.innerHTML = "";
            return;
        }

        this._setStatus("Update(s) found.");
        this.packageSelect.innerHTML = "";

        (result.packages || []).forEach(pkg => {
            const opt = document.createElement("option");
            opt.value = pkg;
            opt.textContent = pkg;
            this.packageSelect.appendChild(opt);
        });
    }

    async prepareUpdate() {
        const pkg = this.packageSelect.value;
        if (!pkg) {
            this._setStatus("No package selected.");
            return;
        }

        this._setStatus(`Staging update package: ${pkg}...`);

        const result = await apiPost("/api/update/prepare", { package: pkg });

        if (result.error) {
            this._setStatus(`Error: ${result.error}`);
            return;
        }

        this._setStatus(`Package staged: ${result.package}`);
    }

    async installUpdate() {
        const pkg = this.packageSelect.value;
        if (!pkg) {
            this._setStatus("No package selected.");
            return;
        }

        this._setStatus(`Installing update: ${pkg}...`);

        const result = await apiPost("/api/update/install", { package: pkg });

        if (result.error) {
            this._setStatus(`Error: ${result.error}`);
            return;
        }

        this._setStatus(`Update installed. Backup created at: ${result.backup || "N/A"}`);
    }

    _setStatus(msg) {
        if (this.statusBox) {
            this.statusBox.textContent = msg;
        }
    }
}