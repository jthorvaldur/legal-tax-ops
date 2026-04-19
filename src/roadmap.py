"""Roadmap HTML generator — public version + personalized version from profile."""
from __future__ import annotations

from pathlib import Path
from datetime import date

from jinja2 import Template

from .models import ProfileAnalysis, Severity


# ─── Roadmap Data ────────────────────────────────────────────

PHASES = [
    {
        "id": 1,
        "title": "Profile & Scanner",
        "status": "done",
        "description": "YAML profile schema + multi-jurisdiction obligation analyzer",
        "tasks": [
            {"name": "Profile YAML schema", "status": "done", "detail": "Identity, income, entities, accounts, filings, crypto, distributions"},
            {"name": "US analyzer", "status": "done", "detail": "1040, state returns, estimated payments, Form 1116 FTC"},
            {"name": "UK analyzer", "status": "done", "detail": "Self Assessment, PAYE detection, departure year, high-earner rules"},
            {"name": "Canada analyzer", "status": "done", "detail": "T1, T1135 foreign property, residency-based obligations"},
            {"name": "FBAR analyzer", "status": "done", "detail": "FinCEN 114 — aggregate $10K threshold, per-account penalties"},
            {"name": "FATCA analyzer", "status": "done", "detail": "Form 8938 — threshold by residence ($50K domestic, $200K abroad)"},
            {"name": "Entity analyzer", "status": "done", "detail": "Annual reports, franchise tax, delinquent status, missing returns"},
            {"name": "Crypto analyzer", "status": "done", "detail": "Schedule D/8949, exchange tracking, cost basis alerts"},
            {"name": "Government View", "status": "done", "detail": "What each country knows via FATCA, CRS, PAYE, citizenship, EINs"},
            {"name": "Rich terminal CLI", "status": "done", "detail": "scan, init, governments commands with color-coded output"},
            {"name": "HTML report generator", "status": "done", "detail": "Dark-themed report for sharing with tax professionals"},
        ],
    },
    {
        "id": 2,
        "title": "Entity & Account Tools",
        "status": "next",
        "description": "Automated entity verification + FBAR preparation + compliance calendars",
        "tasks": [
            {"name": "Entity search tool", "status": "planned", "detail": "Auto-check Secretary of State websites (WY, TX, DE, CA, IL) for entity status. Compare profile against actual state records. Flag dissolved/delinquent/missing."},
            {"name": "FBAR account aggregator", "status": "planned", "detail": "Generate account list with max balances per year. Aggregate threshold check. Pre-formatted data for FinCEN 114 e-filing. Multi-year worksheet."},
            {"name": "Entity compliance calendar", "status": "planned", "detail": "Per-entity deadlines: annual reports, franchise tax, tax returns, registered agent renewals. iCal (.ics) export."},
            {"name": "IRS transcript request helper", "status": "planned", "detail": "Generate Form 4506-T data from profile to request IRS transcripts and verify filing history."},
        ],
    },
    {
        "id": 3,
        "title": "Professional Matching & Integration",
        "status": "future",
        "description": "Connect with the right professionals + bridge to case management",
        "tasks": [
            {"name": "Tax professional finder", "status": "planned", "detail": "From profile, determine professional type needed (EA, CPA, international, Big 4). Generate intake document. Checklist of questions for initial consultation."},
            {"name": "div_legal integration", "status": "planned", "detail": "Pull financial facts from Qdrant vector DB. Cross-reference case payments against tax deductions. Sync entity data between legal facts and tax profile."},
            {"name": "Professional intake generator", "status": "planned", "detail": "One-page PDF summarizing your tax situation for a new CPA — jurisdictions, entities, open items, key numbers."},
        ],
    },
    {
        "id": 4,
        "title": "Automation & Monitoring",
        "status": "future",
        "description": "Continuous compliance monitoring across jurisdictions",
        "tasks": [
            {"name": "HMRC API integration", "status": "planned", "detail": "Check UK tax status via Government Gateway. Verify Self Assessment registration and submissions."},
            {"name": "CRA My Account bridge", "status": "planned", "detail": "Check Canadian filing status, NOAs, benefit entitlements."},
            {"name": "Automated penalty calculator", "status": "planned", "detail": "Precise penalty estimates by jurisdiction — late filing, late payment, information return penalties."},
            {"name": "Annual review generator", "status": "planned", "detail": "Year-end report: filed vs. required, entity status, account changes, upcoming deadlines."},
            {"name": "Family dashboard", "status": "planned", "detail": "Multi-profile view — aggregate obligations across family members. Shared deadline calendar."},
        ],
    },
]


# ─── Public Roadmap (no personal data) ───────────────────────

ROADMAP_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<style>
  :root { --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #c9d1d9;
          --heading: #f0f6fc; --accent: #58a6ff; --green: #3fb950; --red: #f85149;
          --yellow: #d29922; --purple: #bc8cff; --dim: #8b949e; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); padding: 2rem 1rem;
         max-width: 960px; margin: 0 auto; line-height: 1.6; }
  h1 { color: var(--heading); font-size: 1.6rem; margin-bottom: 0.25rem; }
  .subtitle { color: var(--dim); font-size: 0.9rem; margin-bottom: 1.5rem; }
  h2 { color: var(--accent); font-size: 1.15rem; margin: 2rem 0 0.5rem;
       border-bottom: 1px solid var(--border); padding-bottom: 6px; }

  .phase { background: var(--card); border: 1px solid var(--border);
           border-radius: 10px; padding: 1.25rem; margin-bottom: 1.25rem;
           transition: border-color 0.15s; }
  .phase:hover { border-color: var(--accent); }
  .phase-header { display: flex; justify-content: space-between; align-items: center;
                  margin-bottom: 0.75rem; }
  .phase-title { font-size: 1.1rem; font-weight: 700; color: var(--heading); }
  .phase-desc { color: var(--dim); font-size: 0.85rem; margin-bottom: 0.75rem; }

  .badge { display: inline-block; padding: 0.15rem 0.6rem; border-radius: 12px;
           font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; }
  .badge-done { background: rgba(63,185,80,0.15); color: var(--green); }
  .badge-next { background: rgba(210,153,34,0.15); color: var(--yellow); }
  .badge-future { background: rgba(188,140,255,0.15); color: var(--purple); }
  .badge-planned { background: rgba(88,166,255,0.1); color: var(--accent); }

  .items { list-style: none; padding: 0; }
  .item { display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.4rem 0;
          border-bottom: 1px solid rgba(48,54,61,0.5); font-size: 0.85rem; }
  .item:last-child { border-bottom: none; }
  .check { flex-shrink: 0; width: 18px; height: 18px; margin-top: 2px; }
  .check-done { color: var(--green); }
  .check-planned { color: var(--border); }
  .item-name { font-weight: 600; }
  .item-detail { color: var(--dim); font-size: 0.8rem; margin-top: 2px; }

  .progress-bar { height: 6px; background: var(--border); border-radius: 3px;
                  margin: 0.75rem 0 0.25rem; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
  .progress-fill.green { background: var(--green); }
  .progress-fill.yellow { background: var(--yellow); }
  .progress-fill.purple { background: var(--purple); }
  .progress-label { font-size: 0.7rem; color: var(--dim); }

  {% if personal %}
  .personal-section { background: rgba(248,81,73,0.08); border: 1px solid rgba(248,81,73,0.2);
                      border-radius: 10px; padding: 1.25rem; margin-bottom: 1.5rem; }
  .personal-section h2 { color: var(--red); border-bottom-color: rgba(248,81,73,0.3); margin-top: 0; }
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
               gap: 0.6rem; margin: 0.75rem 0; }
  .stat { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem; }
  .stat .label { font-size: 0.65rem; color: var(--dim); text-transform: uppercase; letter-spacing: 0.04em; }
  .stat .value { font-size: 1.1rem; font-weight: 700; margin-top: 0.15rem; }
  .action-list { list-style: none; padding: 0; margin-top: 0.5rem; }
  .action-list li { padding: 0.35rem 0; font-size: 0.85rem; border-bottom: 1px solid rgba(48,54,61,0.3); }
  .action-list li:last-child { border-bottom: none; }
  .sev-critical { color: var(--red); font-weight: 700; }
  .sev-high { color: #f97583; }
  .sev-medium { color: var(--yellow); }
  {% endif %}

  .footer { text-align: center; color: #484f58; font-size: 0.75rem; margin-top: 2rem;
            padding-top: 1rem; border-top: 1px solid var(--border); }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>

<h1>{{ title }}</h1>
<div class="subtitle">{{ subtitle }}</div>

{% if personal and analysis %}
<div class="personal-section">
  <h2>Your Status — {{ analysis.name }}</h2>
  <div class="stat-grid">
    <div class="stat">
      <div class="label">Obligations</div>
      <div class="value">{{ analysis.obligations | length }}</div>
    </div>
    <div class="stat">
      <div class="label">Critical</div>
      <div class="value" style="color:var(--red)">{{ critical_count }}</div>
    </div>
    <div class="stat">
      <div class="label">High</div>
      <div class="value" style="color:#f97583">{{ high_count }}</div>
    </div>
    <div class="stat">
      <div class="label">Penalty Exposure</div>
      <div class="value" style="color:var(--red)">${{ penalty_exposure }}</div>
    </div>
    <div class="stat">
      <div class="label">FBAR</div>
      <div class="value" style="color:{% if analysis.fbar_required %}var(--red){% else %}var(--green){% endif %}">{{ "REQUIRED" if analysis.fbar_required else "N/A" }}</div>
    </div>
    <div class="stat">
      <div class="label">Jurisdictions</div>
      <div class="value">{{ analysis.government_views | length }}</div>
    </div>
  </div>

  <strong style="font-size:0.85rem">Priority Actions:</strong>
  <ul class="action-list">
  {% for ob in top_actions %}
    <li>
      <span class="sev-{{ ob.severity.value }}">[{{ ob.severity.value | upper }}]</span>
      {{ ob.jurisdiction }} — {{ ob.name }} ({{ ob.tax_year }}): {{ ob.action }}
    </li>
  {% endfor %}
  </ul>
</div>
{% endif %}

{% for phase in phases %}
<div class="phase">
  <div class="phase-header">
    <span class="phase-title">Phase {{ phase.id }}: {{ phase.title }}</span>
    <span class="badge badge-{{ phase.status }}">{{ phase.status | upper }}</span>
  </div>
  <div class="phase-desc">{{ phase.description }}</div>

  {% set done_count = phase.tasks | selectattr('status', 'equalto', 'done') | list | length %}
  {% set total = phase.tasks | length %}
  {% set pct = (done_count / total * 100) | int if total > 0 else 0 %}
  <div class="progress-bar">
    <div class="progress-fill {% if phase.status == 'done' %}green{% elif phase.status == 'next' %}yellow{% else %}purple{% endif %}"
         style="width:{{ pct }}%"></div>
  </div>
  <div class="progress-label">{{ done_count }}/{{ total }} complete</div>

  <ul class="items">
  {% for item in phase.tasks %}
    <li class="item">
      <span class="check {% if item.status == 'done' %}check-done{% else %}check-planned{% endif %}">
        {% if item.status == 'done' %}&#10003;{% else %}&#9744;{% endif %}
      </span>
      <div>
        <div class="item-name">{{ item.name }}</div>
        <div class="item-detail">{{ item.detail }}</div>
      </div>
    </li>
  {% endfor %}
  </ul>
</div>
{% endfor %}

<div class="footer">
  {% if personal %}Confidential — generated for {{ analysis.name }} on {{ today }}.{% endif %}
  {% if not personal %}legal-tax-ops — <a href="https://github.com/jthorvaldur/legal-tax-ops">github.com/jthorvaldur/legal-tax-ops</a>{% endif %}
</div>

</body>
</html>
""")


def generate_public_roadmap(output_path: Path):
    """Generate the public (no personal data) roadmap HTML."""
    html = ROADMAP_TEMPLATE.render(
        title="Legal & Tax Ops — Roadmap",
        subtitle="Multi-jurisdiction tax compliance toolkit — what's built, what's next",
        phases=PHASES,
        personal=False,
        analysis=None,
        today=date.today().isoformat(),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)


def generate_personal_roadmap(analysis: ProfileAnalysis, output_path: Path):
    """Generate a personalized roadmap with the user's status overlay."""
    severity_order = {
        Severity.CRITICAL: 0, Severity.HIGH: 1,
        Severity.MEDIUM: 2, Severity.LOW: 3, Severity.OK: 4,
    }
    sorted_obs = sorted(
        analysis.obligations,
        key=lambda o: severity_order.get(o.severity, 5),
    )
    top_actions = [o for o in sorted_obs if o.severity in (Severity.CRITICAL, Severity.HIGH)][:8]

    html = ROADMAP_TEMPLATE.render(
        title=f"Tax Ops Roadmap — {analysis.name}",
        subtitle=f"Personal status + project roadmap | {date.today().isoformat()}",
        phases=PHASES,
        personal=True,
        analysis=analysis,
        critical_count=sum(1 for o in analysis.obligations if o.severity == Severity.CRITICAL),
        high_count=sum(1 for o in analysis.obligations if o.severity == Severity.HIGH),
        penalty_exposure=f"{analysis.total_penalty_exposure:,.0f}",
        top_actions=top_actions,
        today=date.today().isoformat(),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
