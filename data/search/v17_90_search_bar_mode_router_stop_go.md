# Claire Syntalion v17.90 — Search Bar Mode Router Foundation

## Status

READY FOR TESTING

## Purpose

v17.90 creates the permanent search bar mode router foundation.

The search bar must remain permanent and prepare for:

- normal web search
- governed research search
- Claire system search
- governed runtime truth search
- future AI-agent command mode

## Hard Rules

- No automatic updates.
- No autonomous agent execution.
- No self-modification.
- No runtime truth mutation.
- No live web ingestion.
- Future agent command mode may be recognized but must remain execution-disabled.

## Prefix Routing

- /truth or truth: routes to runtime truth search
- /research or research: routes to governed research search
- /system or system: routes to Claire system search
- /agent or agent: routes to future agent command mode, blocked

## Stop / Go

GO only if pytest passes and agent command execution remains blocked.
