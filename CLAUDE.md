# CLAUDE.md — legal-tax-ops

## Project Overview

Multi-jurisdiction tax compliance toolkit. Scans a YAML profile and generates
interconnected views showing obligations, government perspectives, entity status,
fund flows, and risk exposure across US, UK, and Canada.

## Quick Orientation

```bash
# Install
uv sync

# Generate all views for a profile
uv run python -m src all-views profiles/joel.yaml --open

# Individual commands
uv run python -m src scan profiles/joel.yaml              # terminal report
uv run python -m src dashboard profiles/joel.yaml --open  # Palantir-style dashboard
uv run python -m src deep-view profiles/joel.yaml --open  # per-country auditor view
uv run python -m src roadmap                              # public roadmap (no personal data)
uv run python -m src my-roadmap profiles/joel.yaml        # personal roadmap
```

## Architecture

- `profile.example.yaml` — Template. Users copy to `profiles/<name>.yaml` (gitignored)
- `src/analyzer.py` — Core engine: jurisdiction analyzers (US, UK, CA, FBAR, FATCA, crypto, entities)
- `src/models.py` — Obligation, GovernmentView, ProfileAnalysis dataclasses
- `src/cli.py` — Click CLI with rich output
- `src/report.py` — HTML obligation report
- `src/roadmap.py` — Public + personal roadmap generator
- `src/dashboard.py` — Palantir-style interconnected dashboard
- `src/deep_view.py` — Per-jurisdiction deep intelligence view
- `legal/`, `tax/`, `guides/`, `templates/` — Reference documentation (public)

## Data Separation

- `profiles/` — User data (NEVER committed, gitignored)
- `reports/` — Generated HTML (NEVER committed, gitignored)
- `.env` — Secrets (gitignored)
- Everything in `src/`, `legal/`, `tax/`, `docs/` — public, committed

## Companion Project

`~/div_legal/` has a legal document pipeline with:
- `src/legal_facts.py` — 250+ verified facts (income, payments, accounts, entities)
- Qdrant vector DB at localhost:6333 (collection: legal_docs, 55K+ documents)
- `sdata/index.json` — 55,233 indexed documents
- Joel's profile at `profiles/joel.yaml` was populated from this data

## Current State (as of April 2026)

Phase 1 DONE: Profile scanner with US/UK/CA/FBAR/FATCA/crypto/entity analyzers.
4 HTML views: report, roadmap, dashboard, deep-view.

Phase 2 NEXT: Entity search (SOS websites), FBAR aggregator, compliance calendar.
Phase 3: Tax pro finder, div_legal integration.
Phase 4: IRS/HMRC/CRA automation, family dashboard.

## Development Guidelines

- Every change that affects user-facing output should regenerate views and visually verify
- Keep data source labels on data points (local vs. internet vs. computed)
- Run `uv run python -m src reboot` after any session to update session log
- All HTML output uses dark theme (--bg: #0d1117)
- No personal data in committed files — scan before pushing
