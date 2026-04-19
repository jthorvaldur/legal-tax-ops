# Legal & Tax Operations Toolkit

A practical guide and operational framework for managing legal matters and multi-jurisdiction taxes without enterprise-level firm support.

Built for individuals, families, small LLCs, and anyone navigating:
- **Pro se litigation** (self-represented in court)
- **Multi-country tax compliance** (US, UK, Canada, and others)
- **Multiple LLC/entity management** (including forgotten ones)
- **Family and small-business tax coordination**

---

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Create your tax profile

```bash
mkdir -p profiles
cp profile.example.yaml profiles/your_name.yaml
```

Edit `profiles/your_name.yaml` with your actual data — citizenships, income, entities, accounts, filing history. This file is **gitignored** and never committed.

### 3. Run the scanner

```bash
# Terminal report (rich-formatted)
uv run python -m src scan profiles/your_name.yaml

# With HTML report
uv run python -m src scan profiles/your_name.yaml --html reports/your_name.html

# Government perspective view
uv run python -m src governments profiles/your_name.yaml
```

The scanner will:
- Determine every filing obligation across all your jurisdictions
- Show what each government knows about you (FATCA, CRS, PAYE, citizenship)
- Identify gaps between what's expected and what's been filed
- Calculate penalty exposure
- Flag delinquent entities
- Generate a prioritized action list

---

## What This Is

- An **operational playbook** — what tools to use, how to organize, what processes to run
- A **scanner** that analyzes your tax profile and identifies obligations
- **Reference guides** for legal tech, multi-jurisdiction tax, entity management
- **Templates** for tracking entities, deadlines, and professional engagements

## What This Is Not

- Legal or tax advice (consult licensed professionals)
- A substitute for a CPA or attorney on complex matters
- A filing tool (it tells you *what* to file, not *how* to file it)

---

## Architecture

```
legal-tax-ops/
├── README.md                     # This file
├── pyproject.toml                # uv project — pyyaml, pydantic, rich, click, jinja2
│
├── profile.example.yaml          # Template — copy to profiles/ and fill in
├── profiles/                     # YOUR DATA (gitignored, never committed)
│   └── your_name.yaml            # Your tax profile
├── reports/                      # Generated reports (gitignored, regenerable)
│
├── src/                          # Python scanner and tools
│   ├── models.py                 # Obligation, GovernmentView, ProfileAnalysis
│   ├── analyzer.py               # Jurisdiction analyzers (US, UK, CA, FBAR, FATCA, crypto, entities)
│   ├── cli.py                    # Rich terminal CLI — scan, init, governments
│   └── report.py                 # Dark-themed HTML report generator
│
├── legal/                        # Reference guides
│   ├── tools.md                  # Legal tech tools rated by tier ($0 to $100K+)
│   ├── pro-se-guide.md           # Self-representation playbook
│   ├── firm-evaluation.md        # How to evaluate and work with law firms
│   ├── document-management.md    # Replicate Relativity at zero cost
│   └── ai-for-law.md             # AI tools for legal research and drafting
│
├── tax/                          # Tax reference guides
│   ├── multi-jurisdiction.md     # US + UK + Canada coordination
│   ├── llc-management.md         # Managing and finding forgotten entities
│   ├── annual-checklist.md       # Month-by-month tax calendar
│   ├── tools.md                  # Tax software and services rated
│   └── family-coordination.md    # Cross-family tax coordination
│
├── guides/                       # How-to guides
│   ├── first-llc.md              # Setting up an LLC properly
│   ├── foreign-income.md         # FBAR, FATCA, FTC, FEIE explained
│   └── closing-an-entity.md     # Dissolving forgotten LLCs
│
└── templates/                    # Reusable templates
    ├── entity-registry.md        # Track all your entities
    ├── tax-calendar.md           # Deadline tracker by jurisdiction
    └── engagement-letter.md      # What to ask before hiring counsel
```

### Data Separation (Critical)

| Directory | Contents | In Git? |
|-----------|----------|---------|
| `src/`, `legal/`, `tax/`, `guides/`, `templates/` | Code + reference docs | Yes (public) |
| `profiles/` | Your personal tax data | **NO — gitignored** |
| `reports/` | Generated HTML reports | **NO — gitignored** |
| `.env` | Tax IDs, API keys | **NO — gitignored** |

Each user creates their own `profiles/name.yaml` from the template. Multiple family members can each have a profile in the same local checkout.

---

## Development Roadmap

### Phase 1 — Profile & Scanner (DONE)

- [x] Profile YAML schema (identity, income, entities, accounts, filings, crypto)
- [x] US analyzer (1040, state returns, estimated payments)
- [x] UK analyzer (Self Assessment, PAYE, departure year)
- [x] Canada analyzer (T1, T1135, residency-based)
- [x] FBAR analyzer (foreign account aggregate threshold)
- [x] FATCA analyzer (Form 8938, threshold by residence)
- [x] Entity analyzer (annual reports, franchise tax, missing returns)
- [x] Crypto analyzer (Schedule D, exchange tracking)
- [x] Government View — what each country knows about you
- [x] Rich terminal output
- [x] HTML report generator (dark theme)

### Phase 2 — Entity & Account Tools (NEXT)

- [ ] **Entity search tool** — auto-check Secretary of State websites for entity status
  - Wyoming: wyobiz.wyo.gov API
  - Texas: mycpa.cpa.state.tx.us
  - Delaware, California, Illinois, etc.
  - Compare profile against actual state records
  - Flag: missing entities, dissolved entities you think are active, delinquent filings

- [ ] **FBAR account aggregator** — from profile, generate:
  - Account list with max balances per year
  - Aggregate threshold check
  - Pre-formatted data for FinCEN 114 e-filing
  - Multi-year FBAR worksheet

- [ ] **Entity compliance calendar** — from profile entities, generate:
  - Per-entity annual report deadlines
  - Franchise tax due dates
  - Tax return due dates
  - Registered agent renewal dates
  - iCal (.ics) export

### Phase 3 — Professional Matching & Integration

- [ ] **Tax professional finder** — from profile, determine:
  - What type of professional you need (EA, CPA, international CPA, Big 4)
  - Jurisdiction-specific requirements
  - Generate an intake document for the professional (what they need to know about you)
  - Questions to ask during initial consultation

- [ ] **Integration with div_legal** — for users who have a companion case management repo:
  - Pull financial facts from Qdrant vector database
  - Cross-reference case payments against tax deductions (medical expenses, support payments)
  - Generate evidence summaries for tax positions (e.g., "income = $0 since Dec 5, 2025")
  - Sync entity data between legal facts and tax profile

### Phase 4 — Automation & Monitoring

- [ ] **IRS transcript request helper** — generate Form 4506-T data from profile
- [ ] **HMRC API integration** — check UK tax status (requires Government Gateway login)
- [ ] **CRA My Account scraper** — check Canadian filing status
- [ ] **Automated penalty calculator** — precise penalty estimates by jurisdiction
- [ ] **Annual review generator** — year-end report comparing filed vs. required

---

## Companion Project: div_legal

This toolkit was built alongside a legal document management system at `~/div_legal/`:

| System | Purpose | Data |
|--------|---------|------|
| `legal-tax-ops` (this repo) | Tax compliance, entity management, obligation tracking | Profile YAML, reference guides |
| `div_legal` | Case document pipeline, vector search, motion generation | 55K+ indexed documents, Qdrant DB, case facts |

The two systems share an individual's financial data but serve different purposes. Phase 3 will build a bridge between them.

### Key data in div_legal useful for tax work:

- `src/legal_facts.py` — KNOWN_FACTS dict with 250+ verified facts including income, payments, accounts, entities
- `sdata/index.json` — 55,233 indexed documents (emails, PDFs, financials)
- Qdrant collection `legal_docs` at `localhost:6333` — semantic search across all documents
- `claude_code_integration_notes.md` — comprehensive case strategy with financial data

---

## Profile Schema Reference

See `profile.example.yaml` for the complete schema. Key sections:

| Section | What It Captures |
|---------|-----------------|
| `identity` | Name, citizenships, current and prior residences with dates |
| `tax_ids` | SSN, UTR, NINO, SIN (keep in .env or gitignored profile) |
| `income` | Per-year income sources with employer, country, gross, tax withheld |
| `entities` | Every LLC/corp — state, EIN, status, tax classification, members, annual fees |
| `accounts` | Every financial account — institution, country, type, max balance, currency |
| `filings` | What you've filed (or haven't) — jurisdiction, form, year, status |
| `distributions` | 401k/IRA distributions with amounts, types, penalties |
| `crypto` | Exchanges, 1099 availability, realized gains |
| `notes` | Free-form context, open questions, action items |

---

## Running Commands

```bash
# Install
uv sync

# Scan a profile (terminal output)
uv run python -m src scan profiles/joel.yaml

# Scan with HTML report
uv run python -m src scan profiles/joel.yaml --html reports/joel.html

# View government perspective
uv run python -m src governments profiles/joel.yaml

# Create a new profile interactively
uv run python -m src init
```

---

## For Family / Friends / New Users

1. Clone this repo
2. Run `uv sync`
3. Copy `profile.example.yaml` to `profiles/your_name.yaml`
4. Fill in your data (citizenships, income, accounts, entities)
5. Run `uv run python -m src scan profiles/your_name.yaml`
6. Review the output, address critical items first
7. Share the HTML report with your tax professional

Your data never leaves your machine. Nothing in `profiles/` or `reports/` is committed to git.

---

## Contributing

PRs welcome. If you've navigated a multi-jurisdiction tax situation or built a pro se litigation workflow, share what worked.

## License

MIT — use freely.
