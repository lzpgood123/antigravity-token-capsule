Status: closed

# Specification: Visual Showcase Enhancement for Antigravity Token Capsule README (Inspired by open-design)

## Problem Statement

While the existing `README.md` and `README_EN.md` comprehensively explain Antigravity Token Capsule's technical architecture, CDP sniffing mechanism, and command-line instructions, the documentation on GitHub is currently purely text-and-diagram based and lacks real product screenshots. 

Prospective users, AI engineers, and community developers browsing the repository cannot intuitively perceive the aesthetic quality of the frameless floating pill, the 5-segment breakdown telemetry card, the in-situ Antigravity IDE workflow, or the 5-theme system tray ecosystem. Referencing industry benchmarks like [`nexu-io/open-design`](https://github.com/nexu-io/open-design), high-impact open-source projects rely on prominent Hero banners and structured Product Tour table grids to rapidly communicate product value and elevate repository credibility.

The maintainer has provided 5 distinctive screenshots in `D:\agent\gemini\new\图库` representing key aspects of the application. These assets need to be ingested, standardized, and integrated into both Chinese and English README documents.

## Solution

1. Ingest all 5 screenshot assets from `D:\agent\gemini\new\图库`, standardize them with descriptive kebab-case names, and store them under the repository's `docs/images/` directory.
2. Mirror `open-design`'s proven visual layout architecture:
   - **Hero Banner**: Embed a centered, high-resolution full-width showcase of the floating capsule operating seamlessly inside the active Antigravity IDE (`01-hero-antigravity.png`).
   - **Product Tour (产品功能巡礼)**: Construct a responsive, two-column HTML table grid (`<table><tr><td width="50%">...</td></tr></table>`) presenting the core visual features with bold headlines and informative sub-captions:
     - Row 1: Minimal Floating Pill (`02-capsule-pill.png`) & Telemetry Detail Card (`03-telemetry-card.png`).
     - Row 2: In-Situ Workspace Workflow (`04-in-situ-expanded.png`) & System Tray 5-Theme Switcher (`05-tray-menu-themes.png`).
3. Apply this visual structure symmetrically to both `README.md` (Chinese) and `README_EN.md` (English) with authentic, localized captions.
4. Commit the new visual assets and updated documentation, push to GitHub, and verify rendered output on the remote repository.

## User Stories

1. As a GitHub visitor landing on the repository, I want to see a prominent hero screenshot of Token Capsule floating inside Google Antigravity right beneath the header badges, so that I immediately understand what the tool looks like in a real workspace.
2. As a user evaluating desktop footprint, I want to see the minimal collapsed pill widget in the Product Tour, so that I can appreciate its non-intrusive, space-saving design.
3. As an AI engineer optimizing prompt budgets, I want to inspect a high-resolution close-up of the telemetry card showing the 5-segment breakdown (System, Native Tools, Messages, MCP, Skills) and real performance metrics (TTFT, tok/s, Cache hit ratio), so that I understand the exact telemetry data provided.
4. As a developer curious about daily desktop integration, I want to see the system tray context menu showing the 5 live theme styles (Pure Light, Obsidian Dark, Frosted Aurora, Matrix Neon, Warm Paper) and startup options, so that I know how the tool fits into my operating system.
5. As an English-speaking user reading `README_EN.md`, I want all image captions, table headers, and accessibility alt text to be written in natural, idiomatic technical English, so that my visual browsing experience is first-class.
6. As a mobile or split-screen reader, I want the visual showcase structured in responsive HTML tables with percentage widths and clean typography, so that the images and text adapt neatly across various screen widths.
7. As an open-source maintainer, I want all image assets stored cleanly in `docs/images/` and tracked in git, so that image links never suffer from third-party hosting degradation or broken links.

## Implementation Decisions

- **Asset Ingestion & Standardization**:
  - `屏幕截图 2026-09-04 173126.png` ➔ `docs/images/01-hero-antigravity.png` (Full desktop Antigravity IDE hero showcase)
  - `屏幕截图 2026-09-04 172834.png` ➔ `docs/images/02-capsule-pill.png` (Minimal collapsed floating pill)
  - `屏幕截图 2026-09-04 173619.png` ➔ `docs/images/03-telemetry-card.png` (Detailed 5-segment breakdown card close-up)
  - `屏幕截图 2026-09-04 173132.png` ➔ `docs/images/04-in-situ-expanded.png` (Full in-situ Antigravity workspace with expanded card)
  - `屏幕截图 2026-09-04 173201.png` ➔ `docs/images/05-tray-menu-themes.png` (System tray menu & 5-theme switcher)

- **Layout Structure (open-design Paradigm)**:
  - **Section 1: Hero Banner** placed directly after the badges / language switch and before "Why Token Capsule":
    ```html
    <p align="center">
      <img src="docs/images/01-hero-antigravity.png" alt="Antigravity Token Capsule Hero Showcase" width="100%" />
    </p>
    ```
  - **Section 2: Product Tour (产品功能巡礼)** placed between "Core Features" and "System Architecture", formatted as a clean 2x2 HTML table grid with `<sub><b>Title</b> — Description.</sub>` subtext.

- **Bilingual Symmetry**:
  - `README.md`: Chinese descriptions and annotations.
  - `README_EN.md`: English descriptions and annotations.

- **Git Tracking & Remote Push**:
  - Track `docs/images/*.png` in git.
  - Commit with Conventional Commit: `docs(readme): add visual showcase and product tour inspired by open-design`.
  - Push to remote `main`.

## Testing Decisions

- **Good Test Definition**: Verify verifiable external outputs (image file existence in `docs/images/`, markdown image link resolution, HTML table tag matching, and GitHub remote rendering) without touching application runtime logic.
- **Seams Tested**:
  - **Seam 1: Asset & Link Integrity Seam (High-level static seam)**:
    - Verify that all 5 image files exist in `docs/images/` and are non-empty.
    - Verify that all `<img src="docs/images/...">` paths in both `README.md` and `README_EN.md` exactly match the filesystem.
    - Verify that all HTML tags (`<table>`, `<tr>`, `<td>`, `<sub>`, `<p>`) are properly paired and closed.
  - **Seam 2: Remote Publishing & Rendering Seam (Integration seam)**:
    - Verify that `git push origin main` executes cleanly.
    - Verify that GitHub REST API returns commit synchronization on `main`.
- **Prior Art**: Previous atomic release commits and git verification procedures.

## Out of Scope

- Video or GIF screen recordings (the 5 provided static screenshots will be the focus).
- Changing application source code (`capsule_ui.py`, `data_engine.py`, etc.).

## Further Notes

- Inspired directly by the visual layout structure of `nexu-io/open-design`.
- All images are located locally in `D:\agent\gemini\new\图库` and ready for immediate ingestion.
