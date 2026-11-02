# API conventions

These rules apply to new endpoints under `/api/v1`. A breaking contract change
requires a new major path such as `/api/v2`; additive fields and endpoints may stay
in v1. The OpenAPI document is available at `/openapi.json` and the interactive
reference at `/docs` in development.

## Responses

Successful JSON responses use an object with a `data` member. The health endpoint
currently returns:

```json
{"data":{"status":"ok","service":"gaitmate-api","timestamp":"2026-11-01T00:00:00Z"}}
```

Errors use a stable machine-readable `code`, a safe human-readable `message`, and
the same `request_id` sent in the `X-Request-ID` response header:

```json
{"error":{"code":"NOT_FOUND","message":"Not Found"},"request_id":"6e81a2b2-f2e0-4ff9-9b7b-5b1250f736b6"}
```

Validation failures use HTTP 422, code `VALIDATION_ERROR`, and a `details` array
of `{field, message, type}`. `field` identifies the request location, for example
`query.value`. The rejected input is never returned. Unhandled failures use HTTP
500, code `INTERNAL_ERROR`, and a generic message. HTTP 401, 403, 404, and 405
use `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, and `METHOD_NOT_ALLOWED`.
Clients should branch on HTTP status and `error.code`, not on `message` text.
Every response carries a server-generated request ID; send that ID when reporting
an API problem. Do not treat it as authentication or accept it as a trusted client
identifier.

## Time

Store and emit instants in UTC. JSON timestamps use ISO 8601 with a trailing `Z`,
for example `2026-11-01T00:00:00Z`. Require an explicit offset on future timestamp
inputs; convert to UTC at the API boundary. Do not interpret naive datetimes as
local time. The browser may display local time, but must retain the UTC instant.

## Logging

The API emits one JSON request log per completed request with `timestamp` (UTC),
`level`, `event`, `request_id`, `method`, `path`, `status_code`, and `duration_ms`.
Unexpected failures emit `request_failed` at ERROR with `exception_type` and a
generic client response. New modules should use the `gaitmate.api` logger and
include the request ID for related events. Log route paths without query strings;
never log tokens, passwords, request or response bodies, sensor readings, or
patient messages. Log route templates; use `<unmatched>` when no route matches so
unrecognized URLs cannot expose sensitive path segments. Use INFO for normal
operations, WARNING for recoverable issues,
and ERROR for failures. Keep logs on stdout for container capture.

