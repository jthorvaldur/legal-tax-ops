"""Jurisdiction analyzer — determines obligations from a profile."""
from __future__ import annotations

from datetime import date, datetime

import yaml

from .models import (
    GovernmentView,
    Obligation,
    ObligationType,
    ProfileAnalysis,
    Severity,
)


def load_profile(path: str) -> dict:
    """Load a YAML profile."""
    with open(path) as f:
        return yaml.safe_load(f)


def analyze(profile: dict) -> ProfileAnalysis:
    """Analyze a profile and return all obligations."""
    identity = profile.get("identity", {})
    name = identity.get("name", "Unknown")
    today = date.today()

    analysis = ProfileAnalysis(
        name=name,
        analysis_date=today.isoformat(),
    )

    # Run each analyzer
    _analyze_us(profile, analysis, today)
    _analyze_uk(profile, analysis, today)
    _analyze_ca(profile, analysis, today)
    _analyze_entities(profile, analysis, today)
    _analyze_fbar(profile, analysis, today)
    _analyze_fatca(profile, analysis, today)
    _analyze_crypto(profile, analysis, today)

    # Calculate totals
    analysis.total_penalty_exposure = sum(
        o.amount_at_risk for o in analysis.obligations
    )

    # Generate summary
    critical = [o for o in analysis.obligations if o.severity == Severity.CRITICAL]
    high = [o for o in analysis.obligations if o.severity == Severity.HIGH]
    analysis.summary = (
        f"{len(analysis.obligations)} obligations identified. "
        f"{len(critical)} critical, {len(high)} high priority. "
        f"Estimated penalty exposure: ${analysis.total_penalty_exposure:,.0f}."
    )

    return analysis


# ── US Analysis ──────────────────────────────────────────────

def _analyze_us(profile: dict, analysis: ProfileAnalysis, today: date):
    """Analyze US filing obligations."""
    identity = profile.get("identity", {})
    citizenships = identity.get("citizenships", [])
    filings = profile.get("filings", [])

    is_us_citizen = "US" in citizenships
    has_us_income = any(
        s.get("country") == "US"
        for year_block in profile.get("income", [])
        for s in year_block.get("sources", [])
    )
    has_us_entities = any(
        e.get("country") == "US"
        for e in profile.get("entities", [])
    )

    if not (is_us_citizen or has_us_income or has_us_entities):
        return

    # What does the US know?
    info_sources = []
    if is_us_citizen:
        info_sources.append("Citizenship — worldwide taxation")
    if has_us_income:
        info_sources.append("W-2/1099 reporting from US employers/clients")
    if has_us_entities:
        info_sources.append("EIN registrations for US entities")

    # Check for foreign accounts (FATCA/CRS reporting back to IRS)
    foreign_accounts = [
        a for a in profile.get("accounts", [])
        if a.get("country") != "US"
    ]
    if foreign_accounts:
        info_sources.append(
            f"FATCA/CRS: {len(foreign_accounts)} foreign account(s) "
            "reported to IRS by foreign banks"
        )

    # Check each tax year for 1040
    for year in _recent_years(today):
        filed = _find_filing(filings, "US", "1040", str(year))
        status = filed.get("status", "not_filed") if filed else "not_filed"

        if status == "filed":
            severity = Severity.OK
            action = "None — filed"
            penalty = ""
            risk = 0.0
        elif status == "extension":
            ext_deadline = filed.get("extension_deadline", f"{year + 1}-10-15")
            ext_date = date.fromisoformat(ext_deadline)
            if today > ext_date:
                severity = Severity.CRITICAL
                action = f"FILE IMMEDIATELY — extension expired {ext_deadline}"
                penalty = "5% of unpaid tax per month, up to 25%"
                risk = 5000.0
            else:
                severity = Severity.HIGH
                action = f"File before extension deadline {ext_deadline}"
                penalty = "None if filed on time"
                risk = 0.0
        else:
            # Not filed
            regular_deadline = date(year + 1, 4, 15)
            abroad_deadline = date(year + 1, 6, 15)
            lives_abroad = identity.get("current_residence", {}).get("country", "US") != "US"
            deadline = abroad_deadline if lives_abroad else regular_deadline

            if today > deadline:
                severity = Severity.CRITICAL
                action = "FILE IMMEDIATELY — past deadline"
                penalty = "5% of unpaid tax per month (up to 25%). If no tax owed, no penalty but still must file."
                risk = 5000.0
            else:
                severity = Severity.MEDIUM
                action = f"File by {deadline.isoformat()} or request extension"
                penalty = "None if filed on time"
                risk = 0.0

        analysis.obligations.append(Obligation(
            jurisdiction="US",
            name="Form 1040 (Individual Income Tax)",
            obligation_type=ObligationType.TAX_RETURN,
            tax_year=str(year),
            deadline=f"{year + 1}-04-15",
            status=status,
            severity=severity,
            penalty_risk=penalty,
            action=action,
            amount_at_risk=risk,
        ))

    # Government view
    filed_forms = [
        f"{f.get('form')} ({f.get('year')})"
        for f in filings if f.get("jurisdiction") == "US" and f.get("status") == "filed"
    ]
    expected = ["Form 1040 (each year)", "FBAR (if foreign accounts > $10K)"]
    if foreign_accounts:
        expected.append("Form 8938 (FATCA)")
    if has_us_entities:
        expected.append("Schedule C or Form 1065 per entity")

    gaps = []
    for year in _recent_years(today):
        if not _find_filing(filings, "US", "1040", str(year)):
            gaps.append(f"1040 for {year}")

    analysis.government_views.append(GovernmentView(
        country="US",
        knows_about_you=True,
        why="US citizen" if is_us_citizen else "US income/entities",
        information_sources=info_sources,
        what_they_expect=expected,
        what_you_filed=filed_forms,
        gaps=gaps,
        risk_level=Severity.CRITICAL if gaps else Severity.OK,
    ))


# ── UK Analysis ──────────────────────────────────────────────

def _analyze_uk(profile: dict, analysis: ProfileAnalysis, today: date):
    """Analyze UK filing obligations."""
    identity = profile.get("identity", {})
    filings = profile.get("filings", [])

    # Check for UK residency or income
    uk_residences = [
        r for r in identity.get("prior_residences", [])
        if r.get("country") == "UK"
    ]
    current_uk = identity.get("current_residence", {}).get("country") == "UK"
    has_uk_income = any(
        s.get("country") == "UK"
        for year_block in profile.get("income", [])
        for s in year_block.get("sources", [])
    )
    has_uk_accounts = any(
        a.get("country") == "UK"
        for a in profile.get("accounts", [])
    )

    if not (current_uk or uk_residences or has_uk_income):
        return

    info_sources = []
    if current_uk or uk_residences:
        info_sources.append("HMRC has residency records via PAYE/NI")
    if has_uk_income:
        info_sources.append("Employer reported income via RTI/PAYE")
    if has_uk_accounts:
        info_sources.append("UK banks report via CRS to other countries")

    # UK tax years: April 6 to April 5
    # If you had UK income, you may need Self Assessment even if PAYE covered it
    uk_income_years = set()
    for year_block in profile.get("income", []):
        for s in year_block.get("sources", []):
            if s.get("country") == "UK":
                uk_income_years.add(year_block.get("year"))

    for cal_year in sorted(uk_income_years):
        # UK tax year "2024-25" covers April 6 2024 to April 5 2025
        uk_year = f"{cal_year}-{str(cal_year + 1)[-2:]}"
        sa_deadline = date(cal_year + 2, 1, 31)  # Jan 31 of year+2

        filed = _find_filing(filings, "UK", "Self Assessment", uk_year)
        status = filed.get("status", "not_filed") if filed else "not_filed"

        if status == "filed":
            severity = Severity.OK
            action = "None — filed"
            penalty = ""
            risk = 0.0
        elif today > sa_deadline:
            severity = Severity.HIGH
            action = f"File UK Self Assessment for {uk_year} — past deadline {sa_deadline}"
            penalty = "£100 flat + £10/day after 3 months + 5% of tax after 6 months"
            risk = 500.0  # approximate
        else:
            severity = Severity.MEDIUM
            action = f"File UK Self Assessment for {uk_year} by {sa_deadline}"
            penalty = "None if filed on time"
            risk = 0.0

        notes = ""
        # Check if taxes were withheld
        for year_block in profile.get("income", []):
            if year_block.get("year") == cal_year:
                for s in year_block.get("sources", []):
                    if s.get("country") == "UK" and s.get("tax_withheld", 0) > 0:
                        notes = (
                            f"£{s['tax_withheld']:,} already withheld via PAYE. "
                            "SA may result in refund or small balance."
                        )

        analysis.obligations.append(Obligation(
            jurisdiction="UK",
            name="Self Assessment",
            obligation_type=ObligationType.TAX_RETURN,
            tax_year=uk_year,
            deadline=sa_deadline.isoformat(),
            status=status,
            severity=severity,
            penalty_risk=penalty,
            action=action,
            notes=notes,
            amount_at_risk=risk,
        ))

    # Government view
    gaps = []
    for cal_year in sorted(uk_income_years):
        uk_year = f"{cal_year}-{str(cal_year + 1)[-2:]}"
        filed = _find_filing(filings, "UK", "Self Assessment", uk_year)
        if not filed or filed.get("status") != "filed":
            gaps.append(f"Self Assessment {uk_year}")

    analysis.government_views.append(GovernmentView(
        country="UK",
        knows_about_you=True,
        why="UK employment income / prior residency",
        information_sources=info_sources,
        what_they_expect=["Self Assessment for each tax year with UK income"],
        what_you_filed=[],
        gaps=gaps,
        risk_level=Severity.HIGH if gaps else Severity.OK,
        notes="HMRC knows your income via PAYE. Even if all tax was withheld, "
              "Self Assessment may be required for high earners (>£100K).",
    ))


# ── Canada Analysis ──────────────────────────────────────────

def _analyze_ca(profile: dict, analysis: ProfileAnalysis, today: date):
    """Analyze Canadian filing obligations."""
    identity = profile.get("identity", {})
    filings = profile.get("filings", [])

    citizenships = identity.get("citizenships", [])
    current_ca = identity.get("current_residence", {}).get("country") == "CA"
    ca_residences = [
        r for r in identity.get("prior_residences", [])
        if r.get("country") == "CA"
    ]

    if not ("CA" in citizenships or current_ca or ca_residences):
        return

    # Canada taxes based on residency, not citizenship
    # If you established residential ties, you're a tax resident
    if current_ca:
        resident_since = identity.get("current_residence", {}).get("since", "")
        if resident_since:
            resident_year = int(resident_since[:4])
        else:
            resident_year = today.year

        for year in range(resident_year, today.year + 1):
            filed = _find_filing(filings, "CA", "T1", str(year))
            status = filed.get("status", "not_filed") if filed else "not_filed"
            deadline = date(year + 1, 4, 30)

            if status == "filed":
                severity = Severity.OK
                action = "None — filed"
                penalty = ""
                risk = 0.0
            elif today > deadline:
                severity = Severity.HIGH
                action = f"File T1 for {year} — past deadline"
                penalty = "5% of balance + 1%/month up to 12 months"
                risk = 1000.0
            else:
                severity = Severity.MEDIUM
                action = f"File T1 for {year} by {deadline}"
                penalty = "None if filed on time"
                risk = 0.0

            analysis.obligations.append(Obligation(
                jurisdiction="CA",
                name="T1 General (Income Tax)",
                obligation_type=ObligationType.TAX_RETURN,
                tax_year=str(year),
                deadline=deadline.isoformat(),
                status=status,
                severity=severity,
                penalty_risk=penalty,
                action=action,
                amount_at_risk=risk,
                notes="Part-year return if residency established mid-year"
                if year == resident_year else "",
            ))

        # T1135 — Foreign Income Verification
        foreign_assets = sum(
            a.get("max_balance_2024", 0)
            for a in profile.get("accounts", [])
            if a.get("country") != "CA"
        )
        if foreign_assets > 100000:
            analysis.obligations.append(Obligation(
                jurisdiction="CA",
                name="T1135 (Foreign Income Verification)",
                obligation_type=ObligationType.INFO_RETURN,
                tax_year=str(today.year - 1),
                deadline=date(today.year, 4, 30).isoformat(),
                status="not_filed",
                severity=Severity.HIGH,
                penalty_risk="$25/day late, up to $2,500. $500-$12,000 for knowing failure.",
                action="File T1135 with T1 — report all foreign property > $100K CAD",
                amount_at_risk=2500.0,
            ))

    # Government view
    info_sources = []
    if "CA" in citizenships:
        info_sources.append("Canadian citizen (CRA has SIN records)")
    if current_ca:
        info_sources.append("Current resident — CRA aware via banking/address")

    analysis.government_views.append(GovernmentView(
        country="CA",
        knows_about_you="CA" in citizenships or current_ca,
        why="Canadian citizen/resident",
        information_sources=info_sources,
        what_they_expect=["T1 for each year of residency"],
        what_you_filed=[],
        gaps=[],
        risk_level=Severity.MEDIUM if current_ca else Severity.LOW,
        notes="Canada taxes by residency, not citizenship. "
              "Establishing residential ties triggers filing obligation.",
    ))


# ── Entity Analysis ──────────────────────────────────────────

def _analyze_entities(profile: dict, analysis: ProfileAnalysis, today: date):
    """Analyze entity compliance."""
    for entity in profile.get("entities", []):
        name = entity.get("name", "Unknown")
        state = entity.get("state", "")
        status = entity.get("status", "unknown")
        last_report = entity.get("last_annual_report", "")
        last_return = entity.get("last_tax_return", "")
        annual_fee = entity.get("annual_fee", 0)

        issues = []

        # Check annual report
        if last_report:
            try:
                report_date = date.fromisoformat(last_report)
                days_since = (today - report_date).days
                if days_since > 400:
                    years_missed = days_since // 365
                    back_fees = annual_fee * years_missed
                    issues.append(
                        f"Annual report {years_missed} year(s) overdue. "
                        f"Estimated back fees: ${back_fees:,.0f}"
                    )
                    analysis.obligations.append(Obligation(
                        jurisdiction=f"US-{state}",
                        name=f"{name} — Annual Report",
                        obligation_type=ObligationType.ENTITY_COMPLIANCE,
                        tax_year=str(today.year),
                        deadline="OVERDUE",
                        status="overdue",
                        severity=Severity.HIGH,
                        penalty_risk=f"${annual_fee}/year + late fees. Entity may be admin dissolved.",
                        action=f"File annual report with {state} Secretary of State or dissolve entity",
                        amount_at_risk=back_fees,
                    ))
            except ValueError:
                pass

        # Check tax returns
        if last_return:
            try:
                return_year = int(last_return)
                years_missing = today.year - 1 - return_year
                if years_missing > 0:
                    tax_class = entity.get("tax_classification", "disregarded")
                    form = {
                        "disregarded": "Schedule C",
                        "partnership": "Form 1065",
                        "s-corp": "Form 1120-S",
                        "c-corp": "Form 1120",
                    }.get(tax_class, "unknown")

                    members = len(entity.get("members", [1]))
                    # Partnership/S-Corp penalties: $220/member/month
                    if tax_class in ("partnership", "s-corp"):
                        penalty_per_year = 220 * members * 12
                        risk = penalty_per_year * years_missing
                    else:
                        risk = 0.0

                    analysis.obligations.append(Obligation(
                        jurisdiction="US",
                        name=f"{name} — {form}",
                        obligation_type=ObligationType.TAX_RETURN,
                        tax_year=f"{return_year + 1}-{today.year - 1}",
                        deadline="OVERDUE",
                        status="overdue",
                        severity=Severity.CRITICAL if risk > 0 else Severity.HIGH,
                        penalty_risk=f"${risk:,.0f} potential penalties ({years_missing} years missed)" if risk > 0 else "File zero returns to close out",
                        action=f"File {form} for {years_missing} missing year(s)",
                        amount_at_risk=risk,
                    ))
            except ValueError:
                pass

        # Check status
        if status == "delinquent":
            analysis.entity_issues.append(
                f"{name} ({state}) is DELINQUENT — resolve or dissolve"
            )


# ── FBAR Analysis ────────────────────────────────────────────

def _analyze_fbar(profile: dict, analysis: ProfileAnalysis, today: date):
    """Check FBAR requirement."""
    citizenships = profile.get("identity", {}).get("citizenships", [])
    if "US" not in citizenships:
        return

    foreign_accounts = [
        a for a in profile.get("accounts", [])
        if a.get("country") != "US"
    ]

    if not foreign_accounts:
        return

    total_max = sum(a.get("max_balance_2024", 0) for a in foreign_accounts)

    if total_max > 10000:
        analysis.fbar_required = True
        filings = profile.get("filings", [])

        for year in _recent_years(today):
            filed = _find_filing(filings, "US", "FBAR", str(year))
            status = filed.get("status", "not_filed") if filed else "not_filed"

            if status == "filed":
                continue

            analysis.obligations.append(Obligation(
                jurisdiction="US",
                name="FBAR (FinCEN 114)",
                obligation_type=ObligationType.INFO_RETURN,
                tax_year=str(year),
                deadline=f"{year + 1}-10-15",
                status=status,
                severity=Severity.CRITICAL,
                penalty_risk="$10,000 per account per year (non-willful). Up to $100K or 50% of balance (willful).",
                action=f"File FBAR for {year} at bsaefiling.fincen.treas.gov — {len(foreign_accounts)} foreign accounts",
                amount_at_risk=10000.0 * len(foreign_accounts),
                notes=f"Aggregate max balance: ${total_max:,.0f}",
            ))


# ── FATCA Analysis ───────────────────────────────────────────

def _analyze_fatca(profile: dict, analysis: ProfileAnalysis, today: date):
    """Check FATCA (Form 8938) requirement."""
    citizenships = profile.get("identity", {}).get("citizenships", [])
    if "US" not in citizenships:
        return

    current_country = profile.get("identity", {}).get("current_residence", {}).get("country", "US")
    lives_abroad = current_country != "US"

    foreign_accounts = [
        a for a in profile.get("accounts", [])
        if a.get("country") != "US"
    ]
    total_max = sum(a.get("max_balance_2024", 0) for a in foreign_accounts)

    threshold = 200000 if lives_abroad else 50000

    if total_max > threshold:
        analysis.fatca_required = True
        filings = profile.get("filings", [])

        for year in _recent_years(today):
            filed = _find_filing(filings, "US", "8938", str(year))
            if filed and filed.get("status") == "filed":
                continue

            analysis.obligations.append(Obligation(
                jurisdiction="US",
                name="Form 8938 (FATCA)",
                obligation_type=ObligationType.INFO_RETURN,
                tax_year=str(year),
                deadline=f"{year + 1}-04-15",
                status="not_filed",
                severity=Severity.HIGH,
                penalty_risk="$10,000 + $10,000/month after 90 days, up to $50,000",
                action=f"File Form 8938 with 1040 — foreign assets ${total_max:,.0f}",
                amount_at_risk=10000.0,
            ))


# ── Crypto Analysis ──────────────────────────────────────────

def _analyze_crypto(profile: dict, analysis: ProfileAnalysis, today: date):
    """Check crypto reporting obligations."""
    crypto = profile.get("crypto", {})
    if not crypto:
        return

    exchanges = crypto.get("exchanges", [])
    gains = crypto.get("realized_gains_2024", 0)

    if gains > 0 or exchanges:
        analysis.obligations.append(Obligation(
            jurisdiction="US",
            name="Schedule D / Form 8949 (Crypto)",
            obligation_type=ObligationType.TAX_RETURN,
            tax_year=str(today.year - 1),
            deadline=f"{today.year}-04-15",
            status="review_needed",
            severity=Severity.MEDIUM,
            penalty_risk="Crypto disposals are taxable events. Unreported = underreported income.",
            action="Pull transaction history from all exchanges. Calculate cost basis. Report on Schedule D.",
            notes=f"{len(exchanges)} exchange(s). Pull 1099s and transaction CSVs.",
        ))


# ── Helpers ──────────────────────────────────────────────────

def _recent_years(today: date, lookback: int = 3) -> list[int]:
    """Return recent tax years to check."""
    return list(range(today.year - lookback, today.year))


def _find_filing(filings: list[dict], jurisdiction: str, form: str, year: str) -> dict | None:
    """Find a specific filing entry."""
    for f in filings:
        if (f.get("jurisdiction") == jurisdiction
                and f.get("form") == form
                and str(f.get("year")) == year):
            return f
    return None
