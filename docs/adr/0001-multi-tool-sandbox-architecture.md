# ADR 0001: Multi-Tool Sandbox Monorepo Architecture

## Status

Accepted

## Context

This repository is designed as a centralized workspace for various utilities, desktop widgets, CLI scripts, MCP servers, and background sidecars created with and for Google Antigravity.

Tools will naturally diverge in technical stacks (e.g., PySide6/Qt for desktop widgets, Node.js/TypeScript for MCP servers, pure Python for data munging). A naive shared environment causes dependency conflicts, cross-tool pollution, and fragile coupling. Furthermore, as multiple tools coexist, issue tracking and domain models need clear boundaries so AI agents do not cross-contaminate concepts.

## Decision

We adopt a **Multi-Tool Zero-Coupling Sandbox Monorepo** architecture using Matt Pocock's **Multi-Context** model:

1. **Physical Isolation**: Each tool resides in `tools/<tool-name>/` as an independent micro-project.
2. **Zero Cross-Tool Imports**: Direct cross-importing between tools is strictly prohibited.
3. **Four-Piece Scaffolding**: Every tool must include:
   - `README.md`
   - Dependency manifest (`requirements.txt` or `package.json`)
   - Launcher script (`start_<tool>.bat` or `run.ps1` with local `.venv` fallback support)
   - Entry point (`main.py` or `cli.js`)
4. **Multi-Context Scoping**:
   - The repository root provides `CONTEXT-MAP.md` mapping tool contexts.
   - Each tool owns its local glossary (`tools/<tool-name>/CONTEXT.md`) and tool-specific ADRs (`tools/<tool-name>/docs/adr/`).
   - Each tool manages its own in-flight issues and specs in `tools/<tool-name>/.scratch/`.
5. **Tool Registry**: All active tools are registered in the root `README.md` Tool Gallery table.

## Consequences

- **Positive**: Complete environmental isolation; tools can be moved, upgraded, or deleted without affecting siblings; AI agents can focus strictly on one tool context at a time without cognitive noise.
- **Trade-offs**: Shared utility code cannot be trivially imported via relative path and must be explicitly designed or duplicated; slightly more upfront scaffolding per tool.
