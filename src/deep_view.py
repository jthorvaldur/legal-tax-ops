"""Deep jurisdiction views — what each government can reconstruct about you.

For each country, builds the view that a tax authority auditor would see:
- All information flows INTO that government
- Cross-referenced income vs. filings
- Account visibility (FATCA/CRS reporting)
- Entity connections
- Estimated tax position
- Risk assessment
"""
from __future__ import annotations

from pathlib import Path
from datetime import date

from jinja2 import Template

from .analyzer import analyze, load_profile


def generate_deep_view(profile_path: str, output_path: Path):
    """Generate per-jurisdiction deep views."""
    profile = load_profile(profile_path)
    analysis = analyze(profile)
    identity = profile.get("identity", {})
    name = identity.get("name", "Unknown")

    countries = {}

    # ── US Deep View ─────────────────────────────────────────
    if "US" in identity.get("citizenships", []):
        countries["US"] = _build_us_deep(profile, analysis)

    # ── UK Deep View ─────────────────────────────────────────
    uk_income = any(
        s.get("country") == "UK"
        for yb in profile.get("income", [])
        for s in yb.get("sources", [])
    )
    if uk_income:
        countries["UK"] = _build_uk_deep(profile, analysis)

    # ── CA Deep View ─────────────────────────────────────────
    if identity.get("current_residence", {}).get("country") == "CA" or "CA" in identity.get("citizenships", []):
        countries["CA"] = _build_ca_deep(profile, analysis)

    html = DEEP_VIEW_TEMPLATE.render(
        name=name,
        today=date.today().isoformat(),
        countries=countries,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)


def _build_us_deep(profile, analysis):
    """Build IRS auditor's view."""
    income = profile.get("income", [])
    accounts = profile.get("accounts", [])
    entities = profile.get("entities", [])
    filings = profile.get("filings", [])
    distributions = profile.get("distributions", [])

    # What the IRS receives automatically
    auto_reports = []
    for yb in income:
        for s in yb.get("sources", []):
            if s.get("country") == "US" and s.get("gross", 0) > 0:
                auto_reports.append({
                    "source": s.get("employer", s.get("client", "")),
                    "form": "W-2" if s.get("type") == "employment" else "1099",
                    "amount": s.get("gross", 0),
                    "year": yb.get("year"),
                    "note": "",
                })

    for d in distributions:
        auto_reports.append({
            "source": d.get("account", ""),
            "form": "1099-R",
            "amount": d.get("amount", 0),
            "year": d.get("year"),
            "note": f"{d.get('type', '')} distribution",
        })

    # FATCA/CRS incoming reports from foreign banks
    fatca_reports = []
    for a in accounts:
        if a.get("country") not in ("US", ""):
            fatca_reports.append({
                "institution": a.get("institution", ""),
                "country": a.get("country", ""),
                "type": a.get("type", ""),
                "max_balance": a.get("max_balance_2024", 0),
                "via": "FATCA" if a.get("country") in ("UK", "CA") else "CRS",
            })

    # Entity awareness
    entity_info = []
    for e in entities:
        if e.get("country") == "US":
            entity_info.append({
                "name": e.get("name", ""),
                "state": e.get("state", ""),
                "ein": e.get("ein", "unknown"),
                "type": e.get("tax_classification", ""),
                "status": e.get("status", ""),
            })

    # Filing gaps
    filed = set()
    gaps = []
    for f in filings:
        if f.get("jurisdiction") == "US" and f.get("status") == "filed":
            filed.add(f"{f.get('form')}_{f.get('year')}")

    today = date.today()
    for year in range(today.year - 3, today.year):
        if f"1040_{year}" not in filed:
            gaps.append(f"Form 1040 for {year}")
        if f"FBAR_{year}" not in filed and fatca_reports:
            gaps.append(f"FBAR for {year}")

    # Estimated position
    total_income_known = sum(r["amount"] for r in auto_reports)
    total_foreign = sum(r["max_balance"] for r in fatca_reports)

    return {
        "full_name": "Internal Revenue Service (IRS)",
        "flag": "&#127482;&#127480;",
        "basis": "Worldwide taxation of US citizens",
        "auto_reports": auto_reports,
        "fatca_reports": fatca_reports,
        "entity_info": entity_info,
        "gaps": gaps,
        "total_income_known": total_income_known,
        "total_foreign_visible": total_foreign,
        "risk_factors": [
            "US citizen abroad — FBAR/FATCA required",
            f"${total_foreign:,.0f} in foreign accounts visible to IRS via FATCA/CRS",
            f"{len(entity_info)} US entities registered (EIN = IRS awareness)",
            f"{len(gaps)} unfiled returns detected" if gaps else "No critical gaps",
        ],
        "what_triggers_audit": [
            "Unfiled FBAR with foreign account balance > $10K",
            "FATCA mismatch — bank reports account, no 8938 filed",
            "1099-R distribution not reported on 1040",
            "Foreign tax credits claimed without supporting documentation",
            "Entity income not flowing to personal return",
        ],
    }


def _build_uk_deep(profile, analysis):
    """Build HMRC auditor's view."""
    income = profile.get("income", [])
    accounts = profile.get("accounts", [])

    paye_reports = []
    for yb in income:
        for s in yb.get("sources", []):
            if s.get("country") == "UK":
                paye_reports.append({
                    "employer": s.get("employer", ""),
                    "gross_gbp": int(s.get("gross", 0) / 1.27),  # rough USD→GBP
                    "tax_gbp": int(s.get("tax_withheld", 0) / 1.27),
                    "ni_gbp": s.get("ni_paid", 0),
                    "year": yb.get("year"),
                    "start": s.get("start", ""),
                    "end": s.get("end", ""),
                })

    uk_accounts = [a for a in accounts if a.get("country") == "UK"]

    crs_outgoing = []
    for a in accounts:
        if a.get("country") == "UK":
            crs_outgoing.append({
                "institution": a.get("institution", ""),
                "reported_to": "IRS (US citizen) and CRA (Canadian resident)",
                "max_balance": a.get("max_balance_2024", 0),
            })

    total_paye = sum(r["tax_gbp"] + r.get("ni_gbp", 0) for r in paye_reports)

    return {
        "full_name": "HM Revenue & Customs (HMRC)",
        "flag": "&#127468;&#127463;",
        "basis": "UK employment income / prior residency",
        "auto_reports": paye_reports,
        "fatca_reports": [],
        "entity_info": [],
        "gaps": [gv.gaps for gv in analysis.government_views if gv.country == "UK" for _ in [None]][0] if any(gv.country == "UK" for gv in analysis.government_views) else [],
        "total_income_known": sum(r["gross_gbp"] for r in paye_reports),
        "total_foreign_visible": 0,
        "uk_accounts": uk_accounts,
        "crs_outgoing": crs_outgoing,
        "total_paye": total_paye,
        "risk_factors": [
            "PAYE records show high-earner (>£100K) — Self Assessment required",
            f"£{total_paye:,} in tax/NI already collected via PAYE",
            "Departure from UK triggers split-year treatment consideration",
            "PILON payment may have UK tax implications",
            "CRS: UK banks report account to IRS and CRA",
        ],
        "what_triggers_audit": [
            "High earner with no Self Assessment registration",
            "Departure from UK without filing departure year SA",
            "PILON/severance not properly reported",
            "Undeclared UK rental income or capital gains",
        ],
    }


def _build_ca_deep(profile, analysis):
    """Build CRA auditor's view."""
    identity = profile.get("identity", {})
    accounts = profile.get("accounts", [])
    income = profile.get("income", [])

    ca_accounts = [a for a in accounts if a.get("country") == "CA"]
    foreign_accounts = [a for a in accounts if a.get("country") not in ("CA", "")]
    total_foreign = sum(a.get("max_balance_2024", 0) for a in foreign_accounts)

    residency_since = identity.get("current_residence", {}).get("since", "")

    # CRS incoming from US and UK
    crs_incoming = []
    for a in foreign_accounts:
        crs_incoming.append({
            "institution": a.get("institution", ""),
            "country": a.get("country", ""),
            "max_balance": a.get("max_balance_2024", 0),
            "via": "CRS",
        })

    return {
        "full_name": "Canada Revenue Agency (CRA)",
        "flag": "&#127464;&#127462;",
        "basis": f"Canadian citizen, resident since {residency_since}",
        "auto_reports": [],
        "fatca_reports": crs_incoming,
        "entity_info": [],
        "gaps": [],
        "total_income_known": 0,
        "total_foreign_visible": total_foreign,
        "risk_factors": [
            f"Became resident {residency_since} — part-year T1 required",
            f"Foreign property > $100K CAD — T1135 required" if total_foreign > 100000 else "Foreign property may be under T1135 threshold",
            f"{len(crs_incoming)} foreign accounts visible to CRA via CRS",
            "US and UK income must be reported on Canadian return with FTC",
            "Canadian citizen = SIN on file with CRA",
        ],
        "what_triggers_audit": [
            "New resident with no T1 filed",
            "T1135 not filed when foreign property > $100K",
            "Large deposits in Canadian bank from foreign sources",
            "CRS mismatch — foreign bank reports account not on T1135",
        ],
    }


DEEP_VIEW_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deep Jurisdiction View — {{ name }}</title>
<style>
  :root { --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #c9d1d9;
          --heading: #f0f6fc; --accent: #58a6ff; --green: #3fb950; --red: #f85149;
          --yellow: #d29922; --purple: #bc8cff; --orange: #f0883e; --dim: #8b949e; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); padding: 2rem 1rem;
         max-width: 1000px; margin: 0 auto; line-height: 1.6; }
  h1 { color: var(--heading); font-size: 1.5rem; margin-bottom: 0.25rem; }
  .subtitle { color: var(--dim); font-size: 0.9rem; margin-bottom: 2rem; }
  .country-section { margin-bottom: 3rem; }
  .country-header { display: flex; align-items: center; gap: 0.75rem;
                    padding: 1rem; background: var(--card); border: 1px solid var(--border);
                    border-radius: 10px; margin-bottom: 1rem; }
  .country-flag { font-size: 2.5rem; }
  .country-name { font-size: 1.2rem; font-weight: 700; color: var(--heading); }
  .country-basis { color: var(--dim); font-size: 0.85rem; }

  h3 { font-size: 0.95rem; color: var(--accent); margin: 1.25rem 0 0.5rem;
       padding-bottom: 4px; border-bottom: 1px solid var(--border); }

  .intel-card { background: var(--card); border: 1px solid var(--border);
                border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem; }
  .intel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  @media (max-width: 600px) { .intel-grid { grid-template-columns: 1fr; } }

  .report-item { display: flex; justify-content: space-between; padding: 0.35rem 0;
                 border-bottom: 1px solid rgba(48,54,61,0.3); font-size: 0.8rem; }
  .report-item:last-child { border-bottom: none; }
  .report-source { color: var(--heading); font-weight: 600; }
  .report-amount { color: var(--green); font-weight: 600; }
  .report-form { color: var(--dim); font-size: 0.7rem; }

  .risk-item { padding: 0.3rem 0; font-size: 0.8rem; border-bottom: 1px solid rgba(48,54,61,0.3); }
  .risk-item:last-child { border-bottom: none; }
  .risk-bullet { color: var(--yellow); margin-right: 0.3rem; }
  .trigger-item { padding: 0.3rem 0; font-size: 0.8rem; color: var(--red);
                  border-bottom: 1px solid rgba(48,54,61,0.3); }
  .trigger-item:last-child { border-bottom: none; }

  .gap-item { color: var(--red); font-size: 0.85rem; font-weight: 600; padding: 0.3rem 0; }

  .summary-stat { display: inline-block; background: var(--bg); border: 1px solid var(--border);
                  border-radius: 6px; padding: 0.4rem 0.75rem; margin: 0.25rem; font-size: 0.8rem; }
  .summary-stat .val { font-weight: 700; color: var(--heading); }

  .footer { text-align: center; color: #484f58; font-size: 0.7rem; margin-top: 2rem;
            padding-top: 1rem; border-top: 1px solid var(--border); }
</style>
</head>
<body>

<h1>Deep Jurisdiction View</h1>
<div class="subtitle">{{ name }} | {{ today }} — What each tax authority can reconstruct about you</div>

{% for code, c in countries.items() %}
<div class="country-section">
  <div class="country-header">
    <span class="country-flag">{{ c.flag }}</span>
    <div>
      <div class="country-name">{{ c.full_name }}</div>
      <div class="country-basis">{{ c.basis }}</div>
    </div>
  </div>

  <div>
    <span class="summary-stat">Income visible: <span class="val">${{ "{:,.0f}".format(c.total_income_known) }}</span></span>
    <span class="summary-stat">Foreign accounts visible: <span class="val">${{ "{:,.0f}".format(c.total_foreign_visible) }}</span></span>
    {% if c.get('total_paye') %}<span class="summary-stat">Tax collected (PAYE): <span class="val">£{{ "{:,.0f}".format(c.total_paye) }}</span></span>{% endif %}
  </div>

  {% if c.gaps %}
  <h3 style="color:var(--red)">Filing Gaps Detected</h3>
  <div class="intel-card" style="border-left:3px solid var(--red)">
    {% for g in c.gaps %}<div class="gap-item">&#9888; {{ g }}</div>{% endfor %}
  </div>
  {% endif %}

  <div class="intel-grid">
    <div>
      <h3>Automatic Information Reports</h3>
      <div class="intel-card">
        {% if c.auto_reports %}
          {% for r in c.auto_reports %}
          <div class="report-item">
            <span>
              <span class="report-source">{{ r.get('source', r.get('employer', '')) }}</span>
              <span class="report-form">{{ r.get('form', 'PAYE') }} ({{ r.get('year', '') }})</span>
            </span>
            <span class="report-amount">
              {% if r.get('amount') %}${{ "{:,.0f}".format(r.amount) }}{% endif %}
              {% if r.get('gross_gbp') %}£{{ "{:,.0f}".format(r.gross_gbp) }} gross | £{{ "{:,.0f}".format(r.tax_gbp) }} tax{% endif %}
            </span>
          </div>
          {% endfor %}
        {% else %}
          <div style="color:var(--dim);font-size:0.8rem">No automatic domestic reports</div>
        {% endif %}
      </div>
    </div>

    <div>
      <h3>Foreign Account Visibility (FATCA/CRS)</h3>
      <div class="intel-card">
        {% if c.fatca_reports %}
          {% for r in c.fatca_reports %}
          <div class="report-item">
            <span>
              <span class="report-source">{{ r.institution }}</span>
              <span class="report-form">{{ r.get('country', '') }} via {{ r.via }}</span>
            </span>
            <span class="report-amount">
              {% if r.max_balance > 0 %}${{ "{:,.0f}".format(r.max_balance) }}{% else %}balance unknown{% endif %}
            </span>
          </div>
          {% endfor %}
        {% else %}
          <div style="color:var(--dim);font-size:0.8rem">No foreign account reports to this jurisdiction</div>
        {% endif %}
      </div>
    </div>
  </div>

  {% if c.entity_info %}
  <h3>Entity Registrations</h3>
  <div class="intel-card">
    {% for e in c.entity_info %}
    <div class="report-item">
      <span class="report-source">{{ e.name }} ({{ e.state }})</span>
      <span><span class="report-form">{{ e.type }} | EIN: {{ e.ein }} | {{ e.status }}</span></span>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <div class="intel-grid">
    <div>
      <h3>Risk Factors</h3>
      <div class="intel-card">
        {% for r in c.risk_factors %}
        <div class="risk-item"><span class="risk-bullet">&#9679;</span> {{ r }}</div>
        {% endfor %}
      </div>
    </div>

    <div>
      <h3>What Triggers an Audit</h3>
      <div class="intel-card" style="border-left:3px solid var(--red)">
        {% for t in c.what_triggers_audit %}
        <div class="trigger-item">&#9888; {{ t }}</div>
        {% endfor %}
      </div>
    </div>
  </div>
</div>
{% endfor %}

<div class="footer">
  Confidential — generated for {{ name }} on {{ today }}.<br>
  This shows what tax authorities can reconstruct. Not tax advice.
</div>

</body>
</html>
""")
