"""Data models for tax profile and obligations."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"   # penalties accruing NOW, criminal exposure
    HIGH = "high"           # deadline approaching or recently passed
    MEDIUM = "medium"       # needs attention this quarter
    LOW = "low"             # informational, plan ahead
    OK = "ok"               # no action needed


class ObligationType(str, Enum):
    TAX_RETURN = "tax_return"
    INFO_RETURN = "info_return"        # FBAR, FATCA, 5471, etc.
    ENTITY_COMPLIANCE = "entity"       # annual reports, franchise tax
    PAYMENT = "payment"                # estimated tax, entity fees
    DISCLOSURE = "disclosure"          # foreign asset reporting


@dataclass
class Obligation:
    """A single filing or compliance obligation."""
    jurisdiction: str               # US, UK, CA, US-WY, US-CA, etc.
    name: str                       # "Form 1040", "FBAR", "WY Annual Report"
    obligation_type: ObligationType
    tax_year: str                   # "2024" or "2024-25" for UK
    deadline: str                   # ISO date
    status: str                     # filed | extension | not_filed | overdue | n/a
    severity: Severity
    penalty_risk: str               # description of penalty
    action: str                     # what to do
    notes: str = ""
    amount_at_risk: float = 0.0     # estimated penalty exposure


@dataclass
class GovernmentView:
    """What a specific government knows/sees about you."""
    country: str
    knows_about_you: bool
    why: str                        # citizenship, residency, income, accounts, entities
    information_sources: list[str]  # FATCA, CRS, employer reporting, etc.
    what_they_expect: list[str]     # forms/returns they expect from you
    what_you_filed: list[str]       # what you've actually filed
    gaps: list[str]                 # what's missing
    risk_level: Severity
    notes: str = ""


@dataclass
class ProfileAnalysis:
    """Complete analysis of a tax profile."""
    name: str
    analysis_date: str
    obligations: list[Obligation] = field(default_factory=list)
    government_views: list[GovernmentView] = field(default_factory=list)
    entity_issues: list[str] = field(default_factory=list)
    fbar_required: bool = False
    fatca_required: bool = False
    total_penalty_exposure: float = 0.0
    summary: str = ""
