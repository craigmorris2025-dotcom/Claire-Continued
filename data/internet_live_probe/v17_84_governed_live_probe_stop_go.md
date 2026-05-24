# Claire v17.84 Governed Single-Query Live Search Probe

Generated: 2026-05-24T22:33:00.941262Z

Status: **READY_FOR_OPERATOR_CONFIRMED_SINGLE_QUERY_PROBE**

Recommendation: Live probe is prepared. Run only one operator-confirmed query. Results are evidence-captured and unknown domains are quarantined.

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

- Provider: `tavily`
- Known: `True`
- Key present: `True`

## Swagger test body

POST `/internet/live-probe/run`

```json
{
  "query": "OpenAI latest research",
  "confirm_text": "RUN GOVERNED WEB PROBE"
}
```
