Status: closed

# Specification: Subagent Cluster & Hybrid Layout Showcase for Repository READMEs

## Problem Statement

The repository has undergone significant feature and architectural updates over recent commits—specifically the introduction of recursive multi-level Subagent discovery, real-time cluster telemetry, dual-billing linkage, and hybrid layout modes (Compact Tabbed 320px vs Dual-Wing Radar 680px with persistent system tray switching).

However, the public-facing documentation across GitHub (`README.md` and `README_EN.md`) still reflects the initial single-session v1 release:
1. The existing telemetry screenshots show obsolete single-card interfaces without the Subagents tab or dual-billing cost rollups.
2. The revolutionary multi-level Subagent tree hierarchy (L1 -> L2 -> L3) and the expansive Dual-Wing Radar layout mode are completely absent from the visual tour and core feature catalog.
3. Visitors landing on the repository cannot perceive the tool's true capabilities when managing complex, multi-agent AI coding sessions in Google Antigravity.

The maintainer has provided three brand-new, high-resolution screenshots capturing these capabilities in action:
- `D:\agent\gemini\new\图库\屏幕截图 2026-09-04 222916.png` (Dual-Wing Radar Mode with multi-level recursive Subagent tree, global combined billing, and context settings menu).
- `D:\agent\gemini\new\图库\屏幕截图 2026-09-04 221756.png` (Compact Tab Mode - Primary Session view with top tab bar and dual billing summary).
- `D:\agent\gemini\new\图库\屏幕截图 2026-09-04 221746.png` (Compact Tab Mode - Subagents view with live cluster status badges and nested accordion task breakdown).

These new assets must replace the outdated imagery, introduce the major new features, and present a cohesive, bilingual visual showcase aligned with open-source presentation standards.

## Solution

1. **Asset Ingestion and Standardization**:
   - Ingest the three newly captured high-resolution screenshot files from `D:\agent\gemini\new\图库/`.
   - Replace the outdated single-session telemetry card with the new Compact Tab Primary Session view showing the tab bar and dual billing linkage.
   - Standardize and ingest the Compact Subagents Tab Accordion view and the Dual-Wing Radar view into the version-controlled image directory.

2. **Core Feature Section Evolution**:
   - Elevate the Subagent cluster monitoring engine, recursive multi-level hierarchy, and dual billing linkage to prominent top-level features in both Chinese and English READMEs.
   - Introduce the hybrid layout architecture (Compact Tabbed vs Dual-Wing Radar) and system tray/context menu mode switching as flagship usability enhancements.

3. **Product Tour Layout Restructuring**:
   - Restructure the Product Tour into a structured 3-tier showcase matrix:
     - **Tier 1 (Desktop Integration)**: Minimal Floating Pill alongside In-Situ Antigravity IDE Workspace.
     - **Tier 2 (Compact Dual-Tab Perspectives)**: Primary Session Telemetry Card paired side-by-side with Subagent Cluster Accordion Card.
     - **Tier 3 (Full-Scale Radar & Tray Orchestration)**: Dual-Wing Recursive Radar layout alongside the System Tray Theme and Layout Switcher.
   - Accompany each screenshot with authentic, informative captions detailing the exact engineering mechanics displayed.

4. **Architectural Diagram & Bilingual Documentation Symmetry**:
   - Update the Mermaid system architecture flowchart to reflect the multi-file SQLite WAL polling loop and transcript sniffing engine.
   - Maintain strict structural, typographic, and semantic symmetry between the Chinese and English documentation files.
   - Synchronize the tool-scoped documentation to ensure internal consistency.

## User Stories

1. As an open-source explorer landing on the GitHub repository, I want to see an up-to-date visual showcase displaying the latest Subagent cluster monitoring capabilities, so that I immediately recognize the tool's modern feature set.
2. As an AI engineer managing multi-agent workflows in Antigravity, I want to see the Dual-Wing Radar layout screenshot, so that I understand how the tool displays primary sessions and derivative agents side-by-side without context switching.
3. As a developer evaluating desktop footprint, I want to compare the 320px Compact Tab mode with the 680px Dual-Wing Radar mode in the Product Tour, so that I can see how the application adapts to both minimal and expansive workspace needs.
4. As a cost-conscious developer, I want to see how the dual-billing linkage displays combined Primary Session and Subagent cluster expenditure, so that I know I can avoid unexpected API budget overruns.
5. As a user operating nested sub-agents (e.g. Teamwork Lead -> Project Orchestrator -> Workers), I want to see the multi-level tree hierarchy in action, so that I know recursive tasks are grouped and rolled up logically.
6. As a user browsing the Compact Tab mode, I want to see both the Primary Session tab and the Subagents accordion tab, so that I understand the segmented navigation model.
7. As an engineer interested in desktop ergonomics, I want to see the system tray and right-click context menu demonstrating layout mode and theme switching, so that I know how to control the window without opening heavy settings panels.
8. As an English-speaking developer reading the international documentation, I want all captions, table headers, and feature highlights to use precise, idiomatic English terminology, so that I receive the exact same clarity as Chinese readers.
9. As a mobile or narrow-screen reader, I want the image grid tables to adapt smoothly with percentage-based responsive columns, so that the documentation renders cleanly across diverse viewport sizes.
10. As a repository maintainer, I want all referenced image assets tracked locally in version control with kebab-case conventions, so that external CDN degradation or broken relative links are permanently prevented.
11. As a developer inspecting the system architecture, I want an updated Mermaid diagram that shows how `transcript.jsonl` sniffing connects to Subagent WAL polling and Proto decoding, so that I can quickly grasp the telemetry pipeline.
12. As a monorepo contributor, I want the tool-level documentation and the repository root documentation to remain mutually aligned, so that developers working in either directory encounter identical expectations.

## Implementation Decisions

- **Asset Replacement and Naming Scheme**:
  - Replace the existing single-session telemetry screenshot (`03-telemetry-card.png`) with the updated Compact Tab Primary Session screenshot (`屏幕截图 2026-09-04 221756.png`), preserving existing inbound references while refreshing the visual to show the tab bar and dual billing.
  - Ingest the Compact Tab Subagents Accordion screenshot (`屏幕截图 2026-09-04 221746.png`) as a newly tracked asset named `06-subagent-accordion-tab.png`.
  - Ingest the Dual-Wing Radar screenshot (`屏幕截图 2026-09-04 222916.png`) as a newly tracked asset named `07-dual-wing-radar.png`.

- **Visual Showcase Matrix Architecture**:
  - Organize the Product Tour into three thematic two-column rows using HTML tables:
    - Row 1 (Form & Flow): Collapsed Floating Pill & In-Situ Workspace.
    - Row 2 (Compact Dual-Mode): Primary Session 5-Segment Telemetry & Subagent Cluster Accordion Card.
    - Row 3 (Full-Scale Radar & Control): Dual-Wing Multi-Level Recursive Radar & System Tray Theme/Layout Control.
  - Use bold title headings and explanatory subtext within `<sub>` tags for each item.

- **Feature Catalog Restructuring**:
  - Add explicit headings for "Subagent Cluster Telemetry & Recursive Tree Hierarchy" and "Hybrid Dual-Layout Modes (Compact Tab vs Dual-Wing Radar)".
  - Highlight key technical guarantees: zero-jitter active session tracking, multi-level cascade cost rollups, non-rebounding accordion state memory, and persistent tray configuration.

- **Architecture Diagram Enhancement**:
  - Expand the Mermaid pipeline: from active session detection to concurrent extraction of Subagent UUIDs via `transcript.jsonl`, parallel SQLite WAL polling, Proto usage blob decoding, and reactive dispatch to Qt UI components.

- **Bilingual Symmetry Mandate**:
  - Every modification applied to `README.md` must be mirrored in `README_EN.md` with idiomatic technical translations (e.g. "Dual-Wing Radar Mode", "Recursive Multi-Level Hierarchy", "Dual-Billing Linkage").

## Testing Decisions

- **Good Test Definition**:
  - A good test validates observable documentation artifacts and asset integrity from an end-user or renderer perspective: file existence, image readability, markdown syntax validity, link resolution, HTML tag completeness, and git tree consistency. It does not probe internal PySide6 or SQLite runtime code.

- **Seams Tested**:
  - **Highest Seam: Documentation & Asset Integrity Seam (Static Verification)**:
    - Verification that all ingested PNG files exist at their target paths with non-zero byte size.
    - Verification that every `<img>` tag and markdown link resolves to a valid, existing relative file path.
    - Verification that all HTML table tags (`<table>`, `<tr>`, `<td>`, `<sub>`, `<p>`) are properly matched and closed.
    - Verification that the Mermaid code block complies with valid Mermaid syntax.
    - Verification that `README.md` and `README_EN.md` have matching heading counts and corresponding image references.

- **Prior Art**:
  - The previous visual showcase release (`tools/token-capsule/.scratch/readme-visual-showcase/`) used automated static verification of image existence and markdown link parity prior to git publication.

## Out of Scope

- Modifying the underlying PySide6 UI or Data Engine source code (the application features are already fully implemented and verified in preceding commits).
- Generating video demonstrations or animated GIF assets (static high-resolution PNGs are specified).
- Changing root monorepo governance files beyond README and image assets.

## Further Notes

- The three source screenshots are located at:
  - `D:\agent\gemini\new\图库\屏幕截图 2026-09-04 222916.png`
  - `D:\agent\gemini\new\图库\屏幕截图 2026-09-04 221756.png`
  - `D:\agent\gemini\new\图库\屏幕截图 2026-09-04 221746.png`
- The spec is published directly to the project issue tracker under `tools/token-capsule/.scratch/readme-subagent-cluster-showcase/spec.md`.
