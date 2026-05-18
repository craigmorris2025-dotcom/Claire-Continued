# Claire Syntalion v19.65
## Search Panel Permanent Core Architecture Contract

Generated: 2026-05-11T09:35:06.036203Z

## Decision

The search panel is a permanent core cockpit surface, not a temporary dashboard widget.

Canonical name: **Claire Command Surface**

## Placement Contract

- `top_level`: True
- `default_visible`: True
- `inside_panel_registry`: True
- `can_open_dedicated_workspace`: True
- `must_survive_dashboard_replacement`: True
- `must_not_be_removed_during_simplification`: True

## Core Modes

### normal_web_search
- User-facing web search behavior, routed through governed source trust and provider readiness.
- Required UI states:
  - query input
  - provider availability
  - source trust badges
  - rate-limit/blocked state
  - result list
  - empty result state

### governed_research
- Research mode using governed web architecture, evidence capture, source trust, allowlist/rate visibility, and review state.
- Required UI states:
  - review queue
  - evidence basket
  - source validation status
  - promote-to-runtime-truth disabled/enabled state
  - blocked/quarantined source state

### runtime_project_search
- Search across Claire runtime outputs, project state, payload panels, run history, and system reports.
- Required UI states:
  - project/system filter
  - run/result filter
  - payload section jump
  - lifecycle stage jump
  - report/file reference display

### command_recognition
- Early command surface for routing user text into search, runtime navigation, cockpit navigation, or future agent workflows.
- Required UI states:
  - detected intent
  - safe command preview
  - requires-confirmation state
  - unsupported command state
  - route-to-panel action

### future_ai_agent_entry
- Reserved governed entry point for future Claire AI-agent orchestration.
- Required UI states:
  - agent unavailable/not-yet-enabled
  - governed command preview
  - operator approval
  - execution trace
  - safety block reason

## Backend Truth Boundaries

### Frontend may
- display results
- collect operator query
- route modes
- show source trust and provider states
- navigate to cockpit panels
- show command previews

### Frontend must not
- fabricate source trust
- fabricate runtime truth
- bypass governed web gates
- directly scrape uncontrolled web pages
- promote evidence to truth without backend route support
- execute commands without backend/runtime approval path

## No-Redesign-Later Constraints

- Search must be built as Claire Command Surface from the first cockpit shell build.
- Search must support mode routing from the start, even if some modes initially show unavailable/blocked states.
- Search must be wired through shared api_client and payload_adapter, not direct scattered fetches.
- Search must expose governed web state, source trust, provider readiness, and blocked/rate-limited states.
- Search must reserve future AI-agent entry without pretending full agent autonomy exists yet.
- Search must not be buried inside a secondary settings/debug panel.
- Search must remain permanent during cockpit simplification or redesign.
