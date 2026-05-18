# Claire v17.84 Governed Single-Query Live Search Probe

Generated: 2026-05-13T11:20:33.043036Z

Status: **BLOCKED_PROVIDER_NOT_READY**

Recommendation: Configure CLAIRE_SEARCH_PROVIDER and its API key locally, then rerun v17.83/v17.84 gates.

## Hard Rules

- This installer does not run a web search.
- A live probe requires explicit operator confirmation.
- Only one query is allowed per request.
- Unknown domains are quarantined.
- Results do not automatically feed runtime truth.
- Automatic updates and agent execution remain disabled.

## Required confirm text

`RUN GOVERNED WEB PROBE`

## Provider

- Provider: `none`
- Known: `False`
- Key present: `False`

## Blockers

- no_provider_selected

## Swagger test body

POST `/internet/live-probe/run`

```json
{
  "query": "OpenAI latest research",
  "confirm_text": "RUN GOVERNED WEB PROBE"
}
```
