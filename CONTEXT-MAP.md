# Context Map

This repository is organized as a multi-context toolbox monorepo. Each operational tool under `tools/` represents a self-contained bounded context with its own glossary, architecture decisions, and local issue tracking.

## Context Directory

| Context Name | Description | Path | Glossary |
| :--- | :--- | :--- | :--- |
| **`token-capsule`** | Antigravity 实时悬浮 Token 监控胶囊与 CDP 探针 | `tools/token-capsule/` | [`tools/token-capsule/CONTEXT.md`](tools/token-capsule/CONTEXT.md) |

## Context Discovery Rules

1. **Active Context Resolution**: When working on a request that targets a specific tool, the active context is `tools/<tool-name>/`.
2. **Context Glossary**: Always read `tools/<tool-name>/CONTEXT.md` before writing code or specifications for that tool.
3. **Architecture Decisions**: Tool-specific architectural decisions reside in `tools/<tool-name>/docs/adr/`. System-wide/repository-level decisions reside in `docs/adr/`.
4. **Issue Tracking**: Features and bug tickets for a tool are tracked in its local `tools/<tool-name>/.scratch/<feature-slug>/` directory.
