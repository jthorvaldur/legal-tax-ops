"""Data source classification and labeling.

Every data point in the system has a provenance:
- LOCAL: provided by the user directly (manual entry, uploaded CSV, bank export)
- COMPUTED: derived from other data points by our analyzers
- INTERNET: pulled from an external API or website (SOS lookup, IRS, exchange rates)
- IMPORTED: imported from another system (div_legal, Qdrant, email sync)
- UNVERIFIED: present in profile but not yet confirmed against source documents

This module provides utilities for labeling, tracking, and displaying data provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DataSource(str, Enum):
    LOCAL = "local"           # User-provided (manual entry, CSV upload, bank export)
    COMPUTED = "computed"     # Derived by our analyzers from other data
    INTERNET = "internet"    # Fetched from external API/website
    IMPORTED = "imported"    # Imported from another system (div_legal, Qdrant)
    UNVERIFIED = "unverified"  # In profile but not confirmed


# Display properties for each source type
SOURCE_DISPLAY = {
    DataSource.LOCAL: {
        "label": "LOCAL",
        "color": "#3fb950",
        "icon": "&#128193;",   # folder
        "description": "Provided by user (bank export, manual entry, uploaded document)",
    },
    DataSource.COMPUTED: {
        "label": "COMPUTED",
        "color": "#58a6ff",
        "icon": "&#9881;",     # gear
        "description": "Calculated by the system from other data points",
    },
    DataSource.INTERNET: {
        "label": "INTERNET",
        "color": "#bc8cff",
        "icon": "&#127760;",   # globe
        "description": "Fetched from external source (SOS website, exchange rates, IRS)",
    },
    DataSource.IMPORTED: {
        "label": "IMPORTED",
        "color": "#d29922",
        "icon": "&#128279;",   # link
        "description": "Imported from companion system (div_legal, Qdrant, email)",
    },
    DataSource.UNVERIFIED: {
        "label": "UNVERIFIED",
        "color": "#f85149",
        "icon": "&#10067;",    # question mark
        "description": "Present in profile but not yet verified against source document",
    },
}


@dataclass
class LabeledValue:
    """A data point with its source provenance."""
    value: object
    source: DataSource
    source_detail: str = ""   # e.g., "Chase CSV export 2024-12", "legal_facts.py line 142"
    verified: bool = False
    verified_against: str = ""  # e.g., "W-2 form", "bank statement", "1099-R"
    last_updated: str = ""


def classify_profile_sources(profile: dict) -> dict[str, list[dict]]:
    """Analyze a profile and classify each section's data sources.

    Returns a dict mapping section names to lists of data point classifications.
    """
    classifications = {}

    # Identity — almost always local
    identity = profile.get("identity", {})
    id_items = []
    if identity.get("name"):
        id_items.append({"field": "name", "value": identity["name"], "source": "local", "detail": "User-provided"})
    for cit in identity.get("citizenships", []):
        id_items.append({"field": "citizenship", "value": cit, "source": "local", "detail": "User-provided — verify with passport"})
    res = identity.get("current_residence", {})
    if res:
        id_items.append({"field": "current_residence", "value": f"{res.get('country')} since {res.get('since')}", "source": "local", "detail": "User-provided"})
    classifications["identity"] = id_items

    # Income — mixed sources
    inc_items = []
    for yb in profile.get("income", []):
        for s in yb.get("sources", []):
            source_type = "local"
            detail = "User-provided"
            verify = ""
            if s.get("tax_withheld", 0) > 0:
                verify = "W-2 or P60/P45 (UK)"
            if "notes" in s and "legal_facts" in str(s.get("notes", "")):
                source_type = "imported"
                detail = "Imported from div_legal/legal_facts.py"

            inc_items.append({
                "field": f"{yb.get('year')} {s.get('employer', s.get('client', ''))}",
                "value": f"{s.get('currency', 'USD')} {s.get('gross', 0):,}",
                "source": source_type,
                "detail": detail,
                "verify_against": verify,
            })
    classifications["income"] = inc_items

    # Entities — local or internet-verifiable
    ent_items = []
    for e in profile.get("entities", []):
        ent_items.append({
            "field": e.get("name", ""),
            "value": f"{e.get('type')} in {e.get('state', e.get('country', ''))} — {e.get('status', '')}",
            "source": "local" if e.get("status") == "active" else "unverified",
            "detail": "User-provided — verify on Secretary of State website",
            "verify_against": f"{e.get('state', '')} Secretary of State",
            "can_auto_verify": True,
        })
    classifications["entities"] = ent_items

    # Accounts — local
    acct_items = []
    for a in profile.get("accounts", []):
        acct_items.append({
            "field": f"{a.get('institution', '')} ({a.get('type', '')})",
            "value": f"{a.get('currency', 'USD')} {a.get('max_balance_2024', 0):,}",
            "source": "local" if a.get("max_balance_2024", 0) > 0 else "unverified",
            "detail": "User-provided — verify with bank statement or year-end summary",
            "verify_against": "Bank statement / year-end summary",
        })
    classifications["accounts"] = acct_items

    # Filings — local
    filing_items = []
    for f in profile.get("filings", []):
        filing_items.append({
            "field": f"{f.get('jurisdiction')} {f.get('form')} ({f.get('year')})",
            "value": f.get("status", "unknown"),
            "source": "local",
            "detail": "User-provided — verify with IRS transcript / HMRC record / CRA My Account",
        })
    classifications["filings"] = filing_items

    # Obligations — computed
    # (these come from the analyzer, not the profile directly)

    return classifications


def generate_source_legend_html() -> str:
    """Generate HTML legend for data source labels."""
    items = []
    for source, props in SOURCE_DISPLAY.items():
        items.append(
            f'<span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px;font-size:0.75rem;">'
            f'<span style="background:{props["color"]};color:#0d1117;padding:1px 6px;border-radius:3px;'
            f'font-weight:600;font-size:0.65rem">{props["label"]}</span>'
            f'{props["description"]}</span>'
        )
    return '<div style="display:flex;flex-wrap:wrap;gap:4px;margin:8px 0">' + "".join(items) + "</div>"


def source_badge_html(source: str) -> str:
    """Generate a small HTML badge for a data source type."""
    try:
        ds = DataSource(source)
    except ValueError:
        ds = DataSource.UNVERIFIED
    props = SOURCE_DISPLAY[ds]
    return (
        f'<span style="background:{props["color"]};color:#0d1117;padding:1px 5px;'
        f'border-radius:3px;font-size:0.6rem;font-weight:600;margin-left:4px">'
        f'{props["label"]}</span>'
    )
