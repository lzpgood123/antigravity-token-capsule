Status: ready-for-agent

# Specification: Antigravity Token Capsule Public GitHub Release & Bilingual Documentation

## Problem Statement

The developer has implemented **Antigravity Token Capsule** (`token-capsule`), a zero-coupling desktop companion for Google Antigravity featuring CDP active session tracking, 5-segment token breakdown, zero-dependency Protobuf decoding for TTFT / generation speed (`tok/s`), 5 dynamic visual themes, and standalone Windows executable building.

However, the tool currently resides solely within the local development repository. Without an official public GitHub repository, open-source licensing, and a high-standard bilingual (Chinese & English) documentation suite, developers and users across the global Antigravity community cannot discover, evaluate, download, run, or contribute to the project. Furthermore, users without a Python runtime cannot easily obtain the pre-compiled standalone executable.

## Solution

1. Establish an open-source public repository on GitHub (`antigravity-token-capsule`) under the maintainer's account (`lzpgood123`).
2. Supply a standard permissive MIT License (`LICENSE`).
3. Author an exhaustive, professional bilingual documentation pair:
   - `README.md`: Primary Chinese edition with language navigation, visual architecture diagrams, operational guides, and technical breakdowns.
   - `README_EN.md`: Complete English edition tailored for the international Antigravity community with equivalent technical rigor.
4. Push all source code, assets, and documentation to the `main` branch of the remote repository.
5. Publish a `v1.0.0` GitHub Release attaching the pre-built portable `token-capsule.exe` for immediate out-of-the-box usage.

## User Stories

1. As a developer using Google Antigravity, I want to find a public GitHub repository with an accurate project description, badges, and tags, so that I can understand what the tool does and decide if it solves my monitoring challenges.
2. As a Chinese-speaking user, I want the default repository landing page (`README.md`) to be written in clear, natural Chinese, so that I can understand the tool's capabilities and usage without language friction.
3. As an international English-speaking user, I want a prominent language switcher badge at the top of the README linking to `README_EN.md`, so that I can read the complete English manual with authentic technical phrasing.
4. As a non-technical end user who does not have Python installed, I want to download a pre-built standalone executable (`token-capsule.exe`) directly from the GitHub Releases section, so that I can run the monitoring capsule with a double click.
5. As an AI engineer, I want the README to explain the **5-segment token breakdown** (System Prompt, Native Tools, Chat Messages, MCP Services, Agent Skills), so that I know how each component contributes to total context consumption.
6. As a performance tuner, I want to see how **TTFT (Time To First Token)** and **generation speed (tok/s)** are captured and computed via Protobuf binary decoding, so that I can monitor model latency and throughput in real time.
7. As a user working with multiple background agents concurrently, I want the documentation to explain how the **CDP port sniffer** locks onto the foreground active session, so that I understand why the widget does not suffer from session jitter.
8. As a desktop user, I want the documentation to detail how to switch between the 5 built-in themes (Light, Dark, Frosted Aurora, Cyberpunk Neon, Warm Paper) and how to configure Windows startup via the system tray, so that I can integrate it into my daily desktop environment.
9. As a developer who prefers running from source, I want step-by-step instructions on setting up a clean Python virtual environment and launching with or without a terminal window, so that I can modify the code locally.
10. As a packager or builder, I want instructions on how to use `build_exe.bat` to re-compile the single-file and directory-based executables, so that I can produce my own standalone binaries.
11. As an open-source contributor, I want the repository to include an official MIT License, so that I have clear legal clarity to reuse, adapt, and distribute the project.
12. As a developer troubleshooting issues, I want an FAQ section addressing common operational questions (CDP port detection, Antigravity process states, firewall or localhost network questions), so that I can self-diagnose issues effectively.

## Implementation Decisions

- **Target Repository Name & Scope**: The remote repository will be named `antigravity-token-capsule`. It represents the public release vehicle for this monitoring companion tool.
- **Bilingual Documentation Matrix**:
  - `README.md` (Chinese primary) and `README_EN.md` (English primary) will mirror each other in structure:
    1. Header navigation badges (`[ 简体中文 ] | [ English ]`).
    2. Status badges (License: MIT, Platform: Windows, Python: 3.10+, Status: Active, GUI: PySide6).
    3. Core value proposition & pain point matrix.
    4. Feature highlights (CDP Sniffing, 5-Segment Breakdown, Zero-dep Protobuf Decoder, Real-time Metrics, 5 Themes, System Tray).
    5. Architecture & workflow diagram (Mermaid flow representation: DevToolsActivePort -> CDP HTTP /json -> SQLite WAL -> Proto Decoder -> PySide6 Signal/Slot).
    6. Launch & execution methods (Pre-compiled EXE, VBS silent background, Console debugging).
    7. Build from source instructions (`build_exe.bat` & PyInstaller).
    8. Tray menu & shortcut features.
    9. FAQ and troubleshooting.
- **License Standard**: Standard MIT License file (`LICENSE`) dated 2026 and attributed to `lzpgood123`.
- **Clean Git Hygiene**: Git repository will track documentation, configuration, and source files; all build artifacts (`dist/`, `build/`, `*.spec`, `*.log`, `.venv/`) remain strictly excluded via `.gitignore` to avoid binary bloat in the git history.
- **Remote Initialization & Push**:
  - Authenticate against GitHub via the established local proxy (`http://127.0.0.1:7897`).
  - Create the public repository `lzpgood123/antigravity-token-capsule` via GitHub REST API / CLI.
  - Link remote `origin` and push the `main` branch.
- **Release Distribution**:
  - Draft and publish GitHub Release `v1.0.0`.
  - Attach the compiled standalone executable (`dist/onefile/token-capsule.exe`) as a release asset.

## Testing Decisions

- **Good Test Definition**: Tests must verify externally observable behaviors and delivery artifacts (file existence, relative link correctness between Chinese and English documents, GitHub remote synchronization, and release asset accessibility), avoiding checks on private implementation details.
- **Seams Tested**:
  1. **Documentation Integrity Seam (High-level static seam)**:
     - Verify both `README.md` and `README_EN.md` exist and their mutual language switch links resolve accurately.
     - Verify `LICENSE` exists and matches standard MIT syntax.
     - Verify all internal relative file links point to existing files.
  2. **Remote Publishing & Synchronization Seam (Integration seam)**:
     - Verify GitHub API reports repository creation success with `private: false`.
     - Verify `git push origin main` succeeds and `git ls-remote origin` matches local `HEAD`.
     - Verify GitHub Release `v1.0.0` is published and accessible via the GitHub API with the `.exe` asset attached.
- **Prior Art**: Repository has a history of atomic Conventional Commits and clean git trees.

## Out of Scope

- Cross-platform packaging for macOS or Linux (the current architecture uses Windows-specific APIs such as `winreg` and Windows process paths).
- Auto-updating client daemon (users download new versions via GitHub Releases).
- Modifying underlying UI or data engine source code during this release cycle.

## Further Notes

- Domain model terminology in this spec aligns strictly with `tools/token-capsule/CONTEXT.md` (Active Session, CDP Port Sniffer, 5-Segment Token Breakdown, Capsule Window, Proto Usage Blob).
- Architecture decisions comply with `docs/adr/0001-multi-tool-sandbox-architecture.md` and `tools/token-capsule/docs/adr/0001-antigravity-cdp-session-tracking.md`.
