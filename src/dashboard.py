"""Dashboard generator — Palantir-style interconnected views.

Generates a comprehensive HTML dashboard showing:
- Jurisdiction risk heat map
- Entity → Account → Jurisdiction relationship graph
- Flow of funds timeline
- Obligation priority matrix
- Government intelligence view (what each country sees)
- Account exposure map
"""
from __future__ import annotations

from pathlib import Path
from datetime import date
from collections import defaultdict

from jinja2 import Template

from .models import ProfileAnalysis, Severity
from .analyzer import analyze, load_profile


def generate_dashboard(profile_path: str, output_path: Path):
    """Generate the full dashboard from a profile."""
    profile = load_profile(profile_path)
    analysis = analyze(profile)

    # Build supplementary data structures from raw profile
    entities = profile.get("entities", [])
    accounts = profile.get("accounts", [])
    income = profile.get("income", [])
    filings = profile.get("filings", [])
    distributions = profile.get("distributions", [])
    crypto = profile.get("crypto", {})
    identity = profile.get("identity", {})
    case_payments = profile.get("case_payments", {})

    # ── Jurisdiction summary ─────────────────────────────────
    jurisdictions = _build_jurisdiction_summary(analysis, entities, accounts, income, filings)

    # ── Entity map ───────────────────────────────────────────
    entity_map = _build_entity_map(entities)

    # ── Account map ──────────────────────────────────────────
    account_map = _build_account_map(accounts)

    # ── Income timeline ──────────────────────────────────────
    income_timeline = _build_income_timeline(income)

    # ── Fund flows ───────────────────────────────────────────
    fund_flows = _build_fund_flows(income, distributions, case_payments)

    # ── Open questions ───────────────────────────────────────
    open_questions = profile.get("open_questions", [])

    # ── Render ───────────────────────────────────────────────
    severity_order = {
        Severity.CRITICAL: 0, Severity.HIGH: 1,
        Severity.MEDIUM: 2, Severity.LOW: 3, Severity.OK: 4,
    }
    sorted_obs = sorted(
        analysis.obligations,
        key=lambda o: severity_order.get(o.severity, 5),
    )

    html = DASHBOARD_TEMPLATE.render(
        name=analysis.name,
        today=date.today().isoformat(),
        analysis=analysis,
        obligations=sorted_obs,
        critical_count=sum(1 for o in analysis.obligations if o.severity == Severity.CRITICAL),
        high_count=sum(1 for o in analysis.obligations if o.severity == Severity.HIGH),
        medium_count=sum(1 for o in analysis.obligations if o.severity == Severity.MEDIUM),
        penalty_exposure=f"{analysis.total_penalty_exposure:,.0f}",
        jurisdictions=jurisdictions,
        entity_map=entity_map,
        account_map=account_map,
        income_timeline=income_timeline,
        fund_flows=fund_flows,
        open_questions=open_questions,
        residences=_build_residence_timeline(identity),
        fbar=analysis.fbar_required,
        fatca=analysis.fatca_required,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)


# ── Data builders ────────────────────────────────────────────

def _build_jurisdiction_summary(analysis, entities, accounts, income, filings):
    """Build per-jurisdiction risk summary."""
    jurs = {}
    for gv in analysis.government_views:
        jurs[gv.country] = {
            "country": gv.country,
            "risk": gv.risk_level.value,
            "why": gv.why,
            "gaps": gv.gaps,
            "sources": gv.information_sources,
            "notes": gv.notes,
            "entity_count": sum(1 for e in entities if _entity_country(e) == gv.country),
            "account_count": sum(1 for a in accounts if a.get("country") == gv.country),
            "obligations": [
                o for o in analysis.obligations if _ob_country(o) == gv.country
            ],
        }
    return jurs


def _build_entity_map(entities):
    """Build entity visualization data."""
    result = []
    for e in entities:
        status = e.get("status", "unknown")
        color = {"active": "#3fb950", "delinquent": "#f85149", "inactive": "#8b949e",
                 "dissolved": "#484f58"}.get(status, "#d29922")
        result.append({
            "name": e.get("name", "Unknown"),
            "state": e.get("state", ""),
            "country": e.get("country", "US"),
            "type": e.get("type", "LLC"),
            "status": status,
            "color": color,
            "classification": e.get("tax_classification", ""),
            "formed": e.get("formed", ""),
            "annual_fee": e.get("annual_fee", 0),
            "members": e.get("members", []),
            "last_report": e.get("last_annual_report", ""),
            "last_return": e.get("last_tax_return", ""),
            "notes": e.get("notes", ""),
        })
    return result


def _build_account_map(accounts):
    """Build account visualization data."""
    by_country = defaultdict(list)
    for a in accounts:
        country = a.get("country", "US")
        atype = a.get("type", "unknown")
        color = {
            "checking": "#58a6ff", "current": "#58a6ff", "chequing": "#58a6ff",
            "savings": "#3fb950", "401k": "#d29922", "brokerage": "#bc8cff",
            "crypto": "#f0883e", "credit": "#f85149", "credit_card": "#f85149",
        }.get(atype, "#8b949e")
        by_country[country].append({
            "institution": a.get("institution", ""),
            "type": atype,
            "last4": a.get("last4", ""),
            "max_balance": a.get("max_balance_2024", 0),
            "currency": a.get("currency", "USD"),
            "color": color,
            "joint": a.get("joint_with", ""),
            "notes": a.get("notes", ""),
        })
    return dict(by_country)


def _build_income_timeline(income):
    """Build income timeline for visualization."""
    timeline = []
    for year_block in income:
        year = year_block.get("year", 0)
        for s in year_block.get("sources", []):
            timeline.append({
                "year": year,
                "type": s.get("type", ""),
                "employer": s.get("employer", s.get("client", "")),
                "country": s.get("country", ""),
                "gross": s.get("gross", 0),
                "tax_withheld": s.get("tax_withheld", 0),
                "currency": s.get("currency", "USD"),
                "start": s.get("start", f"{year}-01-01"),
                "end": s.get("end", f"{year}-12-31"),
            })
    return sorted(timeline, key=lambda t: t["start"])


def _build_fund_flows(income, distributions, case_payments):
    """Build flow-of-funds data."""
    flows = []

    # Income flows
    for year_block in income:
        for s in year_block.get("sources", []):
            if s.get("gross", 0) > 0:
                flows.append({
                    "direction": "in",
                    "from": s.get("employer", s.get("client", "Unknown")),
                    "to": "Joel",
                    "amount": s.get("gross", 0),
                    "currency": s.get("currency", "USD"),
                    "year": year_block.get("year"),
                    "type": "income",
                    "label": f"{s.get('type', '')} income",
                })
            if s.get("tax_withheld", 0) > 0:
                country = s.get("country", "")
                gov = {"UK": "HMRC", "US": "IRS", "CA": "CRA"}.get(country, f"{country} Tax")
                flows.append({
                    "direction": "out",
                    "from": "Joel",
                    "to": gov,
                    "amount": s.get("tax_withheld", 0),
                    "currency": s.get("currency", "USD"),
                    "year": year_block.get("year"),
                    "type": "tax",
                    "label": f"{country} tax withheld",
                })

    # Distributions
    for d in distributions:
        flows.append({
            "direction": "in",
            "from": d.get("account", "Retirement"),
            "to": "Joel",
            "amount": d.get("amount", 0),
            "currency": d.get("currency", "USD"),
            "year": d.get("year"),
            "type": "distribution",
            "label": f"{d.get('type', '')} distribution",
        })

    # Case payments
    if case_payments:
        medical = case_payments.get("medical", {})
        if medical.get("total", 0) > 0:
            flows.append({
                "direction": "out",
                "from": "Joel",
                "to": "Medical providers",
                "amount": medical["total"],
                "currency": "USD",
                "year": 2025,
                "type": "medical",
                "label": "Medical expenses",
            })
        transfers = case_payments.get("transfers_to_heather", 0)
        if transfers > 0:
            flows.append({
                "direction": "out",
                "from": "Joel",
                "to": "Heather (undisclosed accounts)",
                "amount": transfers,
                "currency": "USD",
                "year": 2025,
                "type": "transfer",
                "label": "Transfers to undisclosed accounts",
            })

    return sorted(flows, key=lambda f: f.get("year", 0))


def _build_residence_timeline(identity):
    """Build residence timeline."""
    residences = []
    current = identity.get("current_residence", {})
    if current:
        residences.append({
            "country": current.get("country", ""),
            "location": current.get("city", current.get("province_state", "")),
            "since": current.get("since", ""),
            "until": "present",
            "current": True,
        })
    for r in identity.get("prior_residences", []):
        residences.append({
            "country": r.get("country", ""),
            "location": r.get("city", r.get("state", "")),
            "since": r.get("since", ""),
            "until": r.get("until", ""),
            "current": False,
        })
    return sorted(residences, key=lambda r: r.get("since", ""), reverse=True)


def _entity_country(e):
    return e.get("country", "US")


def _ob_country(o):
    jur = o.jurisdiction
    if jur.startswith("US"):
        return "US"
    return jur


# ── Template ─────────────────────────────────────────────────

DASHBOARD_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tax Dashboard — {{ name }}</title>
<style>
  :root { --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #c9d1d9;
          --heading: #f0f6fc; --accent: #58a6ff; --green: #3fb950; --red: #f85149;
          --yellow: #d29922; --purple: #bc8cff; --orange: #f0883e; --dim: #8b949e; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); line-height: 1.6; }

  .top-bar { background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
             border-bottom: 1px solid var(--border); padding: 1rem 2rem; }
  .top-bar h1 { font-size: 1.4rem; color: var(--heading); display: inline; }
  .top-bar .date { float: right; color: var(--dim); font-size: 0.85rem; margin-top: 0.3rem; }

  .container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }

  /* Stats strip */
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
           gap: 0.6rem; margin-bottom: 1.5rem; }
  .stat { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
          padding: 0.7rem; text-align: center; }
  .stat .label { font-size: 0.6rem; color: var(--dim); text-transform: uppercase;
                 letter-spacing: 0.06em; }
  .stat .value { font-size: 1.3rem; font-weight: 700; margin-top: 0.2rem; }

  /* Section */
  .section { margin-bottom: 2rem; }
  .section-title { font-size: 1.1rem; color: var(--accent); font-weight: 700;
                   margin-bottom: 0.75rem; padding-bottom: 6px;
                   border-bottom: 1px solid var(--border); }

  /* Grid layouts */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
  @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }

  /* Cards */
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
          padding: 1rem; }
  .card:hover { border-color: var(--accent); }
  .card h3 { font-size: 0.95rem; color: var(--heading); margin-bottom: 0.5rem; }
  .card-label { font-size: 0.7rem; color: var(--dim); text-transform: uppercase; letter-spacing: 0.04em; }

  /* Jurisdiction heat map */
  .jur-card { border-left: 4px solid; }
  .jur-card.risk-critical { border-left-color: var(--red); }
  .jur-card.risk-high { border-left-color: var(--orange); }
  .jur-card.risk-medium { border-left-color: var(--yellow); }
  .jur-card.risk-low { border-left-color: var(--accent); }
  .jur-card.risk-ok { border-left-color: var(--green); }
  .jur-header { display: flex; justify-content: space-between; align-items: center; }
  .jur-country { font-size: 1.5rem; font-weight: 800; }
  .jur-badge { padding: 0.1rem 0.5rem; border-radius: 12px; font-size: 0.65rem;
               font-weight: 600; text-transform: uppercase; }
  .badge-critical { background: rgba(248,81,73,0.15); color: var(--red); }
  .badge-high { background: rgba(240,136,62,0.15); color: var(--orange); }
  .badge-medium { background: rgba(210,153,34,0.15); color: var(--yellow); }
  .badge-low { background: rgba(88,166,255,0.1); color: var(--accent); }
  .badge-ok { background: rgba(63,185,80,0.15); color: var(--green); }
  .jur-detail { font-size: 0.8rem; color: var(--dim); margin-top: 0.35rem; }
  .jur-gaps { margin-top: 0.5rem; }
  .jur-gap { color: var(--red); font-size: 0.8rem; }
  .jur-source { font-size: 0.75rem; color: var(--dim); }
  .jur-stat { display: inline-block; margin-right: 1rem; margin-top: 0.3rem; font-size: 0.8rem; }

  /* Entity cards */
  .entity-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%;
                margin-right: 0.4rem; vertical-align: middle; }
  .entity-status { font-size: 0.7rem; text-transform: uppercase; font-weight: 600; }
  .entity-meta { font-size: 0.75rem; color: var(--dim); margin-top: 0.25rem; }

  /* Account map */
  .account-country { font-size: 0.9rem; font-weight: 700; color: var(--heading);
                     margin: 0.75rem 0 0.35rem; }
  .account-item { display: flex; justify-content: space-between; align-items: center;
                  padding: 0.35rem 0.5rem; border-radius: 4px; margin-bottom: 0.25rem;
                  font-size: 0.8rem; background: rgba(255,255,255,0.02); }
  .account-item:hover { background: rgba(88,166,255,0.05); }
  .account-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block;
                 margin-right: 0.4rem; }
  .account-bal { font-weight: 600; }

  /* Flow of funds */
  .flow { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0;
          border-bottom: 1px solid rgba(48,54,61,0.3); font-size: 0.8rem; }
  .flow:last-child { border-bottom: none; }
  .flow-arrow { font-size: 1rem; flex-shrink: 0; }
  .flow-arrow.in { color: var(--green); }
  .flow-arrow.out { color: var(--red); }
  .flow-amount { font-weight: 700; min-width: 90px; text-align: right; }
  .flow-label { color: var(--dim); font-size: 0.75rem; }
  .flow-year { color: var(--dim); font-size: 0.7rem; min-width: 35px; }

  /* Residence timeline */
  .res-item { display: flex; gap: 0.75rem; padding: 0.35rem 0; font-size: 0.8rem;
              border-bottom: 1px solid rgba(48,54,61,0.3); }
  .res-item:last-child { border-bottom: none; }
  .res-flag { font-size: 1.2rem; flex-shrink: 0; }
  .res-current { color: var(--green); font-weight: 600; }

  /* Obligations table */
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 6px 8px; text-align: left; border: 1px solid var(--border); font-size: 0.8rem; }
  th { background: rgba(88,166,255,0.08); color: var(--accent); font-weight: 600;
       font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.03em; }
  .sev-critical { color: var(--red); font-weight: 700; }
  .sev-high { color: var(--orange); }
  .sev-medium { color: var(--yellow); }
  .sev-low { color: var(--accent); }
  .sev-ok { color: var(--green); }

  /* Open questions */
  .question { padding: 0.3rem 0; font-size: 0.8rem; color: var(--yellow);
              border-bottom: 1px solid rgba(48,54,61,0.3); }

  .footer { text-align: center; color: #484f58; font-size: 0.7rem; margin-top: 2rem;
            padding-top: 1rem; border-top: 1px solid var(--border); }
</style>
</head>
<body>

<div class="top-bar">
  <h1>{{ name }} — Tax & Compliance Dashboard</h1>
  <span class="date">{{ today }}</span>
</div>

<div class="container">

<!-- STATS STRIP -->
<div class="stats">
  <div class="stat">
    <div class="label">Obligations</div>
    <div class="value">{{ obligations | length }}</div>
  </div>
  <div class="stat">
    <div class="label">Critical</div>
    <div class="value" style="color:var(--red)">{{ critical_count }}</div>
  </div>
  <div class="stat">
    <div class="label">High</div>
    <div class="value" style="color:var(--orange)">{{ high_count }}</div>
  </div>
  <div class="stat">
    <div class="label">Medium</div>
    <div class="value" style="color:var(--yellow)">{{ medium_count }}</div>
  </div>
  <div class="stat">
    <div class="label">Penalty Exposure</div>
    <div class="value" style="color:var(--red)">${{ penalty_exposure }}</div>
  </div>
  <div class="stat">
    <div class="label">Jurisdictions</div>
    <div class="value">{{ jurisdictions | length }}</div>
  </div>
  <div class="stat">
    <div class="label">FBAR</div>
    <div class="value" style="color:{% if fbar %}var(--red){% else %}var(--green){% endif %}">{{ "REQ" if fbar else "N/A" }}</div>
  </div>
  <div class="stat">
    <div class="label">FATCA</div>
    <div class="value" style="color:{% if fatca %}var(--red){% else %}var(--green){% endif %}">{{ "REQ" if fatca else "N/A" }}</div>
  </div>
</div>

<!-- JURISDICTION RISK MAP -->
<div class="section">
  <div class="section-title">Jurisdiction Risk Map — What Each Government Sees</div>
  <div class="grid-3">
  {% for code, j in jurisdictions.items() %}
    <div class="card jur-card risk-{{ j.risk }}">
      <div class="jur-header">
        <span class="jur-country">{{ code }}</span>
        <span class="jur-badge badge-{{ j.risk }}">{{ j.risk | upper }}</span>
      </div>
      <div class="jur-detail">{{ j.why }}</div>
      <div>
        <span class="jur-stat">{{ j.entity_count }} entities</span>
        <span class="jur-stat">{{ j.account_count }} accounts</span>
        <span class="jur-stat">{{ j.obligations | length }} obligations</span>
      </div>
      {% if j.gaps %}
      <div class="jur-gaps">
        {% for g in j.gaps %}<div class="jur-gap">&#9888; {{ g }}</div>{% endfor %}
      </div>
      {% endif %}
      {% for s in j.sources %}
        <div class="jur-source">&#8226; {{ s }}</div>
      {% endfor %}
      {% if j.notes %}<div class="jur-detail" style="margin-top:0.5rem;font-style:italic">{{ j.notes }}</div>{% endif %}
    </div>
  {% endfor %}
  </div>
</div>

<!-- ENTITIES + ACCOUNTS -->
<div class="section">
  <div class="grid-2">
    <!-- Entities -->
    <div>
      <div class="section-title">Entity Map</div>
      {% for e in entity_map %}
      <div class="card" style="margin-bottom:0.5rem; border-left: 3px solid {{ e.color }}">
        <h3><span class="entity-dot" style="background:{{ e.color }}"></span>{{ e.name }}</h3>
        <span class="entity-status" style="color:{{ e.color }}">{{ e.status }}</span>
        &mdash; {{ e.type }} ({{ e.state }}, {{ e.country }})
        <div class="entity-meta">
          {% if e.classification %}Tax: {{ e.classification }}{% endif %}
          {% if e.formed %} | Formed: {{ e.formed }}{% endif %}
          {% if e.annual_fee %} | Fee: ${{ e.annual_fee }}/yr{% endif %}
        </div>
        {% if e.members %}
        <div class="entity-meta">
          {% if e.members is string %}Members: {{ e.members }}{% else %}Members: {{ e.members | join(', ') if e.members[0] is string else e.members | map(attribute='name') | join(', ') }}{% endif %}
        </div>
        {% endif %}
        {% if e.notes %}<div class="entity-meta" style="color:var(--yellow)">{{ e.notes[:120] }}{% if e.notes|length > 120 %}...{% endif %}</div>{% endif %}
      </div>
      {% endfor %}
    </div>

    <!-- Accounts by country -->
    <div>
      <div class="section-title">Account Map</div>
      <div class="card">
      {% for country, accts in account_map.items() %}
        <div class="account-country">{{ country }}</div>
        {% for a in accts %}
        <div class="account-item">
          <span>
            <span class="account-dot" style="background:{{ a.color }}"></span>
            {{ a.institution }} {% if a.last4 %}({{ a.last4 }}){% endif %}
            <span style="color:var(--dim);font-size:0.7rem">{{ a.type }}</span>
            {% if a.joint %}<span style="color:var(--yellow);font-size:0.65rem"> JOINT</span>{% endif %}
          </span>
          <span class="account-bal" style="color:{{ a.color }}">
            {% if a.max_balance > 0 %}{{ a.currency }} {{ "{:,.0f}".format(a.max_balance) }}{% else %}—{% endif %}
          </span>
        </div>
        {% endfor %}
      {% endfor %}
      </div>
    </div>
  </div>
</div>

<!-- FLOW OF FUNDS + RESIDENCE -->
<div class="section">
  <div class="grid-2">
    <div>
      <div class="section-title">Flow of Funds</div>
      <div class="card">
      {% for f in fund_flows %}
        <div class="flow">
          <span class="flow-year">{{ f.year }}</span>
          <span class="flow-arrow {{ f.direction }}">{% if f.direction == 'in' %}&#x2B06;{% else %}&#x2B07;{% endif %}</span>
          <span class="flow-amount" style="color:{% if f.direction == 'in' %}var(--green){% else %}var(--red){% endif %}">
            {{ f.currency }} {{ "{:,.0f}".format(f.amount) }}
          </span>
          <span>
            {{ f['from'] }} &rarr; {{ f.to }}
            <div class="flow-label">{{ f.label }}</div>
          </span>
        </div>
      {% endfor %}
      </div>
    </div>

    <div>
      <div class="section-title">Residence Timeline</div>
      <div class="card">
      {% for r in residences %}
        <div class="res-item">
          <span class="res-flag">{{ {"US":"&#127482;&#127480;","UK":"&#127468;&#127463;","CA":"&#127464;&#127462;"}.get(r.country, "&#127988;") }}</span>
          <div>
            <div {% if r.current %}class="res-current"{% endif %}>
              {{ r.country }} — {{ r.location }}
              {% if r.current %} (current){% endif %}
            </div>
            <div style="font-size:0.75rem;color:var(--dim)">{{ r.since }} &rarr; {{ r.until }}</div>
          </div>
        </div>
      {% endfor %}
      </div>

      <div class="section-title" style="margin-top:1.5rem">Income Timeline</div>
      <div class="card">
      {% for t in income_timeline %}
        {% if t.gross > 0 %}
        <div class="flow">
          <span class="flow-year">{{ t.year }}</span>
          <span style="min-width:20px">{{ {"US":"&#127482;&#127480;","UK":"&#127468;&#127463;","CA":"&#127464;&#127462;"}.get(t.country, "") }}</span>
          <span class="flow-amount" style="color:var(--green)">{{ t.currency }} {{ "{:,.0f}".format(t.gross) }}</span>
          <span>
            {{ t.employer }}
            <div class="flow-label">{{ t.type }} | tax withheld: {{ t.currency }} {{ "{:,.0f}".format(t.tax_withheld) }}</div>
          </span>
        </div>
        {% endif %}
      {% endfor %}
      </div>
    </div>
  </div>
</div>

<!-- OBLIGATION MATRIX -->
<div class="section">
  <div class="section-title">Obligation Priority Matrix</div>
  <table>
    <thead>
      <tr><th>Sev</th><th>Jur</th><th>Obligation</th><th>Year</th><th>Status</th><th>Action</th><th>Risk</th></tr>
    </thead>
    <tbody>
    {% for ob in obligations %}
      <tr>
        <td class="sev-{{ ob.severity.value }}">{{ ob.severity.value | upper }}</td>
        <td>{{ ob.jurisdiction }}</td>
        <td>{{ ob.name }}</td>
        <td>{{ ob.tax_year }}</td>
        <td class="sev-{{ ob.severity.value }}">{{ ob.status }}</td>
        <td>{{ ob.action }}</td>
        <td class="{% if ob.amount_at_risk > 0 %}sev-critical{% endif %}">
          {% if ob.amount_at_risk > 0 %}${{ "{:,.0f}".format(ob.amount_at_risk) }}{% else %}&mdash;{% endif %}
        </td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
</div>

{% if open_questions %}
<!-- OPEN QUESTIONS -->
<div class="section">
  <div class="section-title">Open Questions — Verify Before Filing</div>
  <div class="card">
  {% for q in open_questions %}
    <div class="question">&#x2753; {{ q }}</div>
  {% endfor %}
  </div>
</div>
{% endif %}

<div class="footer">
  Confidential — generated for {{ name }} on {{ today }}.<br>
  legal-tax-ops dashboard. Not tax advice.
</div>

</div>
</body>
</html>
""")
