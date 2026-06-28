# Contributing to VoceLab

Thanks for your interest! VoceLab is a small, focused project — issues, ideas, and PRs are all welcome.

## Ways to help

- 🐞 **Report a bug** — open an issue with your OS, audio interface, and what happened.
- 💡 **Suggest a feature** — especially metrics, scales, or workflow ideas from real practice.
- 🌐 **Translations** — UI strings live in `frontend/src/lib/i18n.tsx` and `content.ts`. Adding a language is mostly filling in those tables.
- 🔬 **Acoustic analysis** — improvements to metrics live in `src/vocelab/analysis/`, backed by sources in `docs/REFERENCES.md`.

## Dev setup

Prerequisites: **Python 3.11+**, **Node 18+**.

```bash
# Web UI
cd frontend && npm install && npm run build && cd ..

# Backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e .
python -m vocelab
```

Frontend-only iteration (mock data, no audio backend): `cd frontend && npm run dev`.

## Before opening a PR

```bash
PYTHONPATH=src pytest          # backend unit tests (no audio hardware needed)
cd frontend && npm run build   # type-check + build the UI
```

- Keep the backend **UI-agnostic** — core audio/analysis code shouldn't import anything UI-specific.
- Match the surrounding style; keep changes focused and small.
- All UI strings should go through `t(...)` so both languages stay in sync.

## Scope & ground rules

VoceLab is a practice aid, **not a medical/diagnostic tool** — please keep claims grounded and cite sources (`docs/REFERENCES.md`) for any metric changes.

By contributing, you agree your work is licensed under the project's [MIT License](./LICENSE).
