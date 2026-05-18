from __future__ import annotations

from typing import Any

from starlette.responses import HTMLResponse

CSS_TAG = '<link rel="stylesheet" href="/api/cockpit/control-surface/assets/css" data-claire-s985-s1012="active-control-surface">'
JS_TAG = '<script src="/api/cockpit/control-surface/assets/js" defer data-claire-s985-s1012="active-control-surface"></script>'
MARKER = 'CLAIRE_S985_S1012_ACTIVE_CONTROL_SURFACE_INJECTED'


def install_cockpit_control_surface_force_injector(app: Any) -> None:
    if getattr(app.state, "claire_s985_s1012_control_surface_injector_installed", False):
        return
    app.state.claire_s985_s1012_control_surface_injector_installed = True

    @app.middleware("http")
    async def claire_s985_s1012_control_surface_injector(request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type.lower():
            return response
        try:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            text = body.decode("utf-8", errors="ignore")
            if MARKER not in text and "/api/cockpit/control-surface/assets/js" not in text:
                if "</head>" in text.lower():
                    text = text.replace("</head>", f"<!-- {MARKER} -->\n{CSS_TAG}\n</head>", 1)
                else:
                    text = f"<!-- {MARKER} -->\n{CSS_TAG}\n" + text
                if "</body>" in text.lower():
                    text = text.replace("</body>", f"{JS_TAG}\n</body>", 1)
                else:
                    text += f"\n{JS_TAG}\n"
            headers = dict(response.headers)
            headers.pop("content-length", None)
            headers.pop("Content-Length", None)
            return HTMLResponse(content=text, status_code=response.status_code, headers=headers)
        except Exception:
            return response
