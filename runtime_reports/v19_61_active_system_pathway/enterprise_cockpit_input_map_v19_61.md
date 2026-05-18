# Enterprise Cockpit Input Map v19.61

Generated: 2026-05-11T09:15:19.964722Z

Canonical rule: The new cockpit consumes backend runtime APIs and canonical payload contracts. It does not own intelligence logic.

## Cockpit Surfaces

### shell_workspace
- Purpose: layout, navigation, docking, workspace state

### runtime_panel
- Purpose: runtime status, lifecycle state, terminal states, run history
- Route feeds: 35
- File feeds: 1146

### dashboard_payload_adapter
- Purpose: single frontend adapter for canonical payload
- Route feeds: 8
- File feeds: 281

### search_command_panel
- Purpose: normal web search, governed research, runtime command surface, project/system search, future AI-agent entry
- Route feeds: 47
- File feeds: 1103

### legacy_fetch_reference
- Purpose: show what old frontend called before replacement
- Rule: Reference only. New cockpit should centralize fetch ownership.

