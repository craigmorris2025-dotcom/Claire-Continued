
# Claire Syntalion v19.89.8-A9
# Backend HTML Beacon Injection

from __future__ import annotations

from starlette.responses import HTMLResponse

A9_MARKER = "CLAIRE_A9_BACKEND_HTML_BEACON"

A9_SCRIPT = """
<script id="CLAIRE_A9_BACKEND_HTML_BEACON">
(function () {
  "use strict";
  var VERSION = "v19.89.8-A9";

  function listScripts() {
    return Array.from(document.scripts || []).map(function (s) {
      return s.src || s.getAttribute("src") || "[inline:" + (s.id || "anonymous") + "]";
    });
  }

  function payload() {
    var loadedScripts = listScripts();
    return {
      version: VERSION,
      reported_at: new Date().toISOString(),
      backend_owns_truth: true,
      cockpit_presentation_only: true,
      frontend_truth_allowed: false,
      runtime_authority_expanded: false,
      autonomous_runtime_enabled: false,
      shell: {
        href: window.location.href,
        protocol: window.location.protocol,
        pathname: window.location.pathname,
        title: document.title || "",
        body_class: document.body ? Array.from(document.body.classList || []) : []
      },
      loaded_scripts: loadedScripts,
      detected: {
        http_origin: window.location.protocol === "http:" || window.location.protocol === "https:",
        backend_html_beacon_loaded: true,
        active_route_truth_text_present: document.documentElement.innerText.indexOf("Active Route Truth") >= 0,
        live_backend_widget_text_present: document.documentElement.innerText.indexOf("Claire Live Backend") >= 0,
        canonical_fetch_client_present: !!window.ClaireCanonicalFetch,
        likely_payload_bridge_loaded: loadedScripts.some(function (s) {
          var low = String(s).toLowerCase();
          return low.indexOf("payload") >= 0 || low.indexOf("bridge") >= 0;
        })
      }
    };
  }

  async function probeBackend() {
    var routes = [
      "/dashboard/payload",
      "/dashboard/payload/status",
      "/system/cockpit-fetch-map/summary",
      "/system/route-owner-registry/summary",
      "/system/duplicate-route-fail-test/summary"
    ];
    var out = {};
    for (var i = 0; i < routes.length; i++) {
      var route = routes[i];
      try {
        var res = await fetch(route, {
          method: "GET",
          headers: { "Accept": "application/json" },
          cache: "no-store"
        });
        out[route] = { ok: res.ok, status: res.status };
      } catch (err) {
        out[route] = { ok: false, error: String(err && err.message ? err.message : err) };
      }
    }
    return out;
  }

  async function run() {
    var p = payload();
    p.backend_probe = await probeBackend();
    window.ClaireLiveCockpitAuthorityBeacon = p;
    window.ClaireA9BackendHtmlBeacon = p;
    window.dispatchEvent(new CustomEvent("claire:a9-backend-html-beacon", { detail: p }));
    return p;
  }

  window.ClaireLiveCockpitAuthorityBeaconTools = {
    version: VERSION,
    payload: payload,
    probeBackend: probeBackend,
    run: run
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
</script>
"""

def _inject(html: str) -> str:
    if A9_MARKER in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", A9_SCRIPT + "\n</body>", 1)
    if "</html>" in html:
        return html.replace("</html>", A9_SCRIPT + "\n</html>", 1)
    return html + "\n" + A9_SCRIPT

async def _read_response_body(response) -> bytes:
    body = b""
    async for chunk in response.body_iterator:
        body += chunk
    return body

def install_cockpit_beacon_injector(app):
    if getattr(app.state, "claire_a9_backend_html_beacon_installed", False):
        return app

    @app.middleware("http")
    async def claire_a9_backend_html_beacon_middleware(request, call_next):
        response = await call_next(request)
        content_type = response.headers.get("content-type", "")

        if "text/html" not in content_type.lower():
            return response

        try:
            body = await _read_response_body(response)
            html = body.decode("utf-8", errors="ignore")
            updated = _inject(html)
            headers = dict(response.headers)
            headers.pop("content-length", None)
            return HTMLResponse(
                content=updated,
                status_code=response.status_code,
                headers=headers,
                media_type="text/html",
            )
        except Exception:
            return response

    app.state.claire_a9_backend_html_beacon_installed = True
    return app
