# v17.50 Static Dashboard Action Script

The installer wrote `src/frontend/claire_dashboard_actions.js`. If your FastAPI app does not already serve `src/frontend` as static files, mount it with StaticFiles so `/claire_dashboard_actions.js` is reachable.

Example:

```python
from fastapi.staticfiles import StaticFiles
app.mount('/', StaticFiles(directory='src/frontend', html=True), name='frontend')
```
