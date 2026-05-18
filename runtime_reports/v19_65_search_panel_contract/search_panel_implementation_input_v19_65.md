# Search Panel Implementation Input v19.65

Generated: 2026-05-11T09:35:06.036203Z

Goal: Prepare v19.66+ cockpit shell to include search as permanent top-level command surface.

## Must Create Later

### Folders
- `frontend/cockpit/`
- `frontend/cockpit/shell/`
- `frontend/cockpit/shared/`
- `frontend/cockpit/intelligence/`

### Search Files
- `frontend/cockpit/intelligence/command_surface.js`
- `frontend/cockpit/intelligence/search_panel.js`
- `frontend/cockpit/intelligence/governed_research_panel.js`
- `frontend/cockpit/intelligence/search_results_view.js`
- `frontend/cockpit/intelligence/search_mode_router.js`
- `frontend/cockpit/intelligence/search_state_model.js`
- `frontend/cockpit/intelligence/source_trust_badges.js`
- `frontend/cockpit/intelligence/provider_status_view.js`
- `frontend/cockpit/intelligence/command_suggestions.js`
- `frontend/cockpit/intelligence/search_panel.css`

### Shared Files
- `frontend/cockpit/shared/api_client.js`
- `frontend/cockpit/shared/payload_adapter.js`
- `frontend/cockpit/shared/state_store.js`
- `frontend/cockpit/shared/error_state.js`
- `frontend/cockpit/shared/loading_state.js`

## Minimum First Render

- Visible name: Claire Command Surface
- Placeholder modes:
  - normal_web_search
  - governed_research
  - runtime_project_search
  - command_recognition
  - future_ai_agent_entry

## Future Test Requirements

- search surface file exists
- search mode router exists
- search panel is registered in panel registry
- search panel is default-visible/top-level
- no direct fetch calls outside shared api_client/payload_adapter after consolidation
- blocked/unavailable states render truthfully
