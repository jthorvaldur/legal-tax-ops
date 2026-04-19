"""HTML report generator."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from .models import ProfileAnalysis, Severity


REPORT_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tax Obligations Report — {{ name }}</title>
<style>
  :root { --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #c9d1d9;
          --heading: #f0f6fc; --accent: #58a6ff; --green: #3fb950; --red: #f85149; --yellow: #d29922; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); padding: 2rem 1rem; max-width: 1000px; margin: 0 auto; line-height: 1.6; }
  h1 { color: var(--heading); font-size: 1.5rem; margin-bottom: 0.5rem; }
  h2 { color: var(--accent); font-size: 1.15rem; margin: 2rem 0 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
  .subtitle { color: #8b949e; font-size: 0.9rem; margin-bottom: 1.5rem; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
  .stat { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem; }
  .stat .label { font-size: 0.7rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat .value { font-size: 1.25rem; font-weight: 700; margin-top: 0.25rem; }
  table { width: 100%; border-collapse: collapse; margin: 0.75rem 0; }
  th, td { padding: 8px 10px; text-align: left; border: 1px solid var(--border); font-size: 0.85rem; }
  th { background: rgba(88,166,255,0.08); color: var(--accent); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
  .critical { color: var(--red); font-weight: 700; }
  .high { color: #f97583; }
  .medium { color: var(--yellow); }
  .low { color: var(--accent); }
  .ok { color: var(--green); }
  .gov-card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }
  .gov-card h3 { color: var(--heading); font-size: 1rem; margin-bottom: 0.5rem; }
  .gov-card ul { padding-left: 1.25rem; margin: 0.35rem 0; }
  .gov-card li { font-size: 0.85rem; margin-bottom: 0.2rem; }
  .gap { color: var(--red); }
  .footer { text-align: center; color: #484f58; font-size: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border); }
</style>
</head>
<body>

<h1>Tax Obligations Report</h1>
<div class="subtitle">{{ name }} | Generated {{ date }}</div>

<div class="stats">
  <div class="stat">
    <div class="label">Total Obligations</div>
    <div class="value">{{ obligations | length }}</div>
  </div>
  <div class="stat">
    <div class="label">Critical</div>
    <div class="value critical">{{ critical_count }}</div>
  </div>
  <div class="stat">
    <div class="label">High Priority</div>
    <div class="value high">{{ high_count }}</div>
  </div>
  <div class="stat">
    <div class="label">Penalty Exposure</div>
    <div class="value critical">${{ penalty_exposure }}</div>
  </div>
  <div class="stat">
    <div class="label">FBAR Required</div>
    <div class="value {% if fbar %}critical{% else %}ok{% endif %}">{{ "YES" if fbar else "No" }}</div>
  </div>
  <div class="stat">
    <div class="label">FATCA Required</div>
    <div class="value {% if fatca %}critical{% else %}ok{% endif %}">{{ "YES" if fatca else "No" }}</div>
  </div>
</div>

<h2>How Governments See You</h2>
{% for gv in government_views %}
<div class="gov-card">
  <h3 class="{{ gv.risk_level.value }}">{{ gv.country }} — {{ gv.why }}</h3>
  <strong>Information sources:</strong>
  <ul>{% for s in gv.information_sources %}<li>{{ s }}</li>{% endfor %}</ul>
  {% if gv.gaps %}
  <strong class="gap">Missing filings:</strong>
  <ul>{% for g in gv.gaps %}<li class="gap">{{ g }}</li>{% endfor %}</ul>
  {% endif %}
  {% if gv.notes %}<p style="color:#8b949e;font-size:0.8rem;margin-top:0.5rem">{{ gv.notes }}</p>{% endif %}
</div>
{% endfor %}

<h2>Filing Obligations</h2>
<table>
  <thead>
    <tr><th>Priority</th><th>Jurisdiction</th><th>Obligation</th><th>Year</th><th>Status</th><th>Action</th><th>Risk</th></tr>
  </thead>
  <tbody>
  {% for ob in obligations %}
    <tr>
      <td class="{{ ob.severity.value }}">{{ ob.severity.value | upper }}</td>
      <td>{{ ob.jurisdiction }}</td>
      <td>{{ ob.name }}</td>
      <td>{{ ob.tax_year }}</td>
      <td class="{{ ob.severity.value }}">{{ ob.status }}</td>
      <td>{{ ob.action }}</td>
      <td class="{% if ob.amount_at_risk > 0 %}critical{% endif %}">${{ "%.0f" | format(ob.amount_at_risk) if ob.amount_at_risk > 0 else "—" }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>

{% if entity_issues %}
<h2>Entity Issues</h2>
<ul>
{% for issue in entity_issues %}
  <li class="high">{{ issue }}</li>
{% endfor %}
</ul>
{% endif %}

<div class="footer">
  Generated by legal-tax-ops. This is not tax advice — consult a licensed professional.
</div>

</body>
</html>
""")


def generate_html_report(analysis: ProfileAnalysis, output_path: Path):
    """Generate an HTML report from analysis results."""
    severity_order = {
        Severity.CRITICAL: 0, Severity.HIGH: 1,
        Severity.MEDIUM: 2, Severity.LOW: 3, Severity.OK: 4,
    }
    sorted_obligations = sorted(
        analysis.obligations,
        key=lambda o: severity_order.get(o.severity, 5),
    )

    html = REPORT_TEMPLATE.render(
        name=analysis.name,
        date=analysis.analysis_date,
        obligations=sorted_obligations,
        government_views=analysis.government_views,
        entity_issues=analysis.entity_issues,
        critical_count=sum(1 for o in analysis.obligations if o.severity == Severity.CRITICAL),
        high_count=sum(1 for o in analysis.obligations if o.severity == Severity.HIGH),
        penalty_exposure=f"{analysis.total_penalty_exposure:,.0f}",
        fbar=analysis.fbar_required,
        fatca=analysis.fatca_required,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
