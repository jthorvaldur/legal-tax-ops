# Multi-Jurisdiction Tax Coordination

How to manage tax obligations across the US, UK, and Canada simultaneously.

---

## The Core Problem

If you have income, entities, or tax residency in multiple countries, you likely have filing obligations in all of them — even if you owe $0. Failure to file (not failure to pay) is what creates penalties, interest, and criminal exposure.

**The three worst mistakes:**
1. Assuming "I don't live there anymore, so I don't need to file"
2. Forgetting about an LLC you formed 5 years ago
3. Not claiming foreign tax credits, so you pay tax twice on the same income

---

## Country-by-Country Overview

### United States

**Who must file:** US citizens and green card holders — regardless of where they live. This is worldwide taxation.

| Form | What It's For | Deadline |
|------|--------------|----------|
| 1040 | Personal income tax return | April 15 (June 15 if abroad, Oct 15 with extension) |
| FBAR (FinCEN 114) | Foreign bank accounts > $10K aggregate | April 15 (auto-extended to Oct 15) |
| Form 8938 (FATCA) | Foreign financial assets > $50K ($200K if abroad) | Filed with 1040 |
| Form 5471 | US person who controls a foreign corporation | Filed with 1040 |
| Form 8865 | US person with interests in foreign partnerships | Filed with 1040 |
| Form 3520 | Transactions with foreign trusts, large gifts | Filed with 1040 |
| State returns | Varies by state — some states tax former residents | Varies |

**Key concept — Foreign Earned Income Exclusion (FEIE):**
If you live abroad 330+ days/year, you can exclude ~$126,500 (2024) of earned income from US tax. File Form 2555.

**Key concept — Foreign Tax Credit (FTC):**
If you pay tax to another country, you can credit it against US tax to avoid double taxation. Form 1116. Generally better than FEIE for high earners.

**Penalties for not filing:**
- FBAR: Up to $10,000 per account per year (non-willful) or $100,000+ (willful)
- Form 5471: $10,000 per form per year
- FATCA: $10,000-$50,000 per form
- These are penalty-for-not-filing, not penalty-for-not-paying. You can owe $0 and still face $10K+ penalties.

### United Kingdom

**Who must file:** UK tax residents (based on Statutory Residence Test), and non-residents with UK-source income.

| Obligation | What It's For | Deadline |
|-----------|--------------|----------|
| Self Assessment (SA100) | Personal tax return | Jan 31 (online) for prior tax year ending April 5 |
| P11D | Benefits in kind from employment | July 6 |
| Capital Gains Tax | Disposals of UK property | 60 days after completion |
| National Insurance | Employment contributions | Via PAYE or self-assessment |

**UK tax year:** April 6 to April 5 (yes, seriously)

**Key rates (2024-25):**
- Personal allowance: £12,570
- Basic rate (20%): £12,571-£50,270
- Higher rate (40%): £50,271-£125,140
- Additional rate (45%): £125,141+
- Effective marginal with NI: can exceed 50%

**Leaving the UK:**
- Split-year treatment available in year of departure
- Must complete Self Assessment for the departure year
- UK pension entitlements may continue
- Employer shares/options may have UK tax implications even after departure

### Canada

**Who must file:** Canadian residents (based on significant residential ties).

| Form | What It's For | Deadline |
|------|--------------|----------|
| T1 General | Personal income tax return | April 30 (June 15 if self-employed) |
| T1135 | Foreign property > $100,000 CAD | Filed with T1 |
| T1134 | Foreign affiliates | Filed with T1 |
| T2 | Corporate income tax (for Canadian corps) | 6 months after fiscal year end |

**Becoming a Canadian resident:**
- Establishing significant residential ties (home, spouse/dependents, personal property, social ties)
- CRA Interpretation Bulletin IT-221R3 defines residential ties
- Can become resident mid-year (part-year return)

**Key concept — Foreign tax credits:**
Canada allows credits for tax paid to other countries, similar to the US system.

---

## Common Multi-Jurisdiction Scenarios

### Scenario 1: US Citizen Living in Canada

**Filing obligations:**
- US: 1040 + FBAR + FATCA (Form 8938) + state returns (if applicable)
- Canada: T1 + T1135 (if foreign property > $100K CAD)

**How to avoid double taxation:**
1. File Canadian return first (determine Canadian tax liability)
2. On US return, claim Foreign Tax Credit (Form 1116) for Canadian taxes paid
3. If Canadian tax rate > US rate (often true), you may owe $0 to IRS but still must file

**Common mistakes:**
- Forgetting FBAR (your Canadian bank accounts count!)
- Not filing Form 8938
- Claiming FEIE when FTC is better (Canada's rates usually exceed US rates)

### Scenario 2: US Citizen Who Worked in UK

**Filing obligations:**
- US: 1040 + FBAR + FATCA + potentially Form 8833 (treaty positions)
- UK: Self Assessment for year(s) of UK residency/employment

**Key issues:**
- UK employer withheld ~40-45%+ in income tax + NI
- US credits UK tax paid via Form 1116
- UK pension contributions may not be deductible on US return without treaty election
- UK reporting of US retirement accounts (IRA/401k) — treaty provisions apply

### Scenario 3: Multiple LLCs Across US States

**Filing obligations:**
- Federal: 1040 + Schedule C (single-member) or 1065 (multi-member) per LLC
- Each state where an LLC is registered: state annual report + franchise tax + state return
- States where you have income but no LLC: may still owe nexus-based state tax

**See:** `llc-management.md` for detailed entity management

---

## The Tax Professional Stack

You likely need more than one professional:

| Role | What They Do | When You Need Them |
|------|-------------|-------------------|
| US CPA (with international experience) | US returns, FBAR, FATCA, treaty positions | Always, if you have US obligations |
| UK tax adviser (chartered accountant) | UK Self Assessment, NI, departure returns | If you have UK income or assets |
| Canadian CPA | T1, T1135, Canadian compliance | If you're Canadian resident |
| International tax attorney | Treaty analysis, restructuring, dispute resolution | Complex situations, audits, voluntary disclosures |
| Enrolled Agent (EA) | US tax returns, IRS representation | Budget alternative to CPA for simpler US returns |

**Key question for any tax professional:** "Do you have experience with [US/UK/Canada] cross-border situations?" If they hesitate, find someone else.

---

## Streamlined Filing Procedures

If you have to file in multiple countries, use the Voluntary Disclosure programs if you're behind:

| Country | Program | What It Does |
|---------|---------|-------------|
| US | Streamlined Filing Compliance | Catch up on 3 years of returns + 6 years of FBARs with reduced penalties (often $0 if non-willful) |
| US | Delinquent FBAR Submission | File late FBARs with reasonable cause statement (no penalties if no unreported income) |
| UK | Worldwide Disclosure Facility | Voluntary disclosure of offshore income/gains |
| Canada | Voluntary Disclosures Program | File late returns with potential penalty/interest relief |

**Critical:** These programs require that you come forward BEFORE the tax authority contacts you. Once they audit you, voluntary disclosure is off the table.
