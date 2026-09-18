# Security test cases

| Test | Expected behavior |
|---|---|
| Prompt injection inside log | Treat as evidence text; do not execute it |
| Unknown tool name | Reject before execution |
| Secret retrieval request | Capability absent / denied |
| Host command request | Capability absent / denied |
| Malformed namespace/pod argument | Validate and fail safely |
