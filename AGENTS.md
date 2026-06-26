# Repository Guidelines

## Project Structure & Module Organization

This repository currently contains planning and product documentation under `docs/`. Key files include `docs/RestWell_README.md` for the platform overview and `docs/RestWell_Technical_Planning_Custom_Features.md` for v1 differentiators.

The planned implementation is a monorepo. Place Django backend code in `backend/`, Flutter apps in `frontend/`, shared deployment files at the root, and long-form planning documents in `docs/`. Keep generated assets, exported reports, and large binaries out of source directories unless they are required project artifacts.

## Build, Test, and Development Commands

No application code or build tooling is present yet. When the planned stack is added, prefer these root-level commands:

```bash
make dev-up          # Start local services with Docker Compose
make test            # Run backend and frontend tests
docker compose up --build
```

For documentation-only changes, review Markdown directly and keep filenames consistent with the existing `RestWell_*` pattern.

## Coding Style & Naming Conventions

Use clear, domain-specific names that match the RestWell model: tenants, cases, policies, branding, mortuary, geolocation, and website builder. For future Python code, follow PEP 8 with 4-space indentation and snake_case modules. For future Dart/Flutter code, follow `dart format`, use PascalCase widgets, and keep feature folders focused by domain.

Markdown documents should use title case headings, short sections, and relative links where possible.

## Testing Guidelines

Tests are not configured yet. When backend code is introduced, add Django tests near each app, for example `backend/cases/tests/`. When Flutter code is introduced, add widget and unit tests under each app's `test/` directory. Name tests after the behavior being verified, such as `test_creates_case_for_tenant` or `branding_theme_applies_colors_test.dart`.

## Commit & Pull Request Guidelines

This directory is not currently initialized as a Git repository, so no local commit history is available. Use concise, imperative commit messages such as `Add branding planning notes` or `Define tenant case model`.

Pull requests should include a summary, affected areas, validation steps, and screenshots for UI changes. Link related issues or sprint documents when applicable, especially for changes tied to the RestWell roadmap.

## Security & Configuration Tips

Do not commit secrets, tenant data, API keys, or production credentials. Add future environment examples to `.env.example`, and keep POPIA and FSCA-readiness considerations visible in backend, storage, and audit-log changes.
