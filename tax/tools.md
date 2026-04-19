# Tax Software and Services — Rated

Tools for managing taxes across jurisdictions, entities, and family members.

---

## Tax Preparation Software

### TurboTax (Intuit)
- **Cost:** $0 (simple) to $130+ (self-employed/business)
- **Best for:** Straightforward US individual returns
- **International:** Limited. Can handle FEIE/FTC but struggles with complex multi-jurisdiction
- **LLC support:** Single-member (Schedule C). Multi-member needs TurboTax Business ($200+)
- **Verdict:** Fine for simple returns, outgrown quickly by multi-jurisdiction filers

### H&R Block
- **Cost:** Similar to TurboTax
- **Best for:** US individual returns with in-person support option
- **Advantage:** In-person offices if you need face-to-face help
- **International:** Similar limitations to TurboTax

### TaxAct
- **Cost:** $25-65 (cheaper than TurboTax/H&R Block)
- **Best for:** Budget-conscious filers with moderately complex returns
- **Verdict:** Good value if you know what you're doing

### FreeTaxUSA
- **Cost:** Free federal, $15 state
- **Best for:** Budget filing of US returns
- **Limitation:** No hand-holding. You need to know what forms you need.

---

## Multi-Jurisdiction / International

### Greenback Expat Tax Services
- **Cost:** ~$450-800 per return
- **What it does:** Full-service US expat tax preparation (FEIE, FTC, FBAR, FATCA)
- **Best for:** US citizens living abroad who need professional help
- **Advantage:** Specializes in expat situations — they've seen your scenario before

### Bright!Tax
- **Cost:** ~$400-1,200 per return
- **What it does:** US expat tax preparation with advisory
- **Best for:** Complex international situations (multiple countries, investments, foreign corps)

### TaxesForExpats
- **Cost:** ~$350-800
- **What it does:** US expat returns, FBAR, treaty positions
- **Best for:** Budget-friendly expat tax prep

### CrossBorder Financial (Canada-US specialists)
- **Cost:** Varies (advisory fees)
- **What it does:** Canada-US cross-border tax planning and compliance
- **Best for:** People with ties to both countries

---

## Bookkeeping & Accounting

### QuickBooks Online
- **Cost:** $15-90/month
- **What it does:** Full bookkeeping, invoicing, expense tracking, bank feeds
- **Best for:** LLCs with real revenue and expenses
- **Multi-entity:** Create separate companies in QBO (separate subscription each)
- **Tax prep:** Exports easily to CPA's tax software
- **Verdict:** Industry standard for small business accounting

### Wave
- **Cost:** Free
- **What it does:** Basic bookkeeping, invoicing, receipt scanning
- **Best for:** Very small or dormant LLCs that still need records
- **Limitation:** Limited reporting, no payroll (unless you pay for add-on)

### Xero
- **Cost:** $15-78/month
- **What it does:** Similar to QuickBooks. Popular outside the US (strong in UK, Canada, Australia)
- **Best for:** Multi-country operations. Better international currency handling than QBO.
- **Verdict:** If you have UK + US operations, Xero handles both more naturally

### FreshBooks
- **Cost:** $19-60/month
- **What it does:** Invoicing-focused bookkeeping
- **Best for:** Freelancers and consultants
- **Limitation:** Less powerful than QBO/Xero for complex entities

---

## FBAR / FATCA Compliance

### FBAR Filing (FinCEN 114)
- **Where to file:** [BSA E-Filing System](https://bsaefiling.fincen.treas.gov/)
- **Cost:** Free to file directly
- **Professional help:** Most CPAs include FBAR in their engagement ($50-200 add-on)

### FATCA (Form 8938)
- **Where to file:** Attached to your 1040
- **Cost:** Included in tax prep
- **Key difference from FBAR:** FBAR goes to FinCEN (Treasury), FATCA goes to IRS. Different thresholds. You may need to file both.

---

## Document Management for Taxes

### What to Keep (and for How Long)

| Document | Retention |
|----------|-----------|
| Tax returns (all jurisdictions) | Permanent |
| W-2s, 1099s, K-1s | 7 years |
| Bank and brokerage statements | 7 years |
| Business receipts and expenses | 7 years |
| Entity formation documents | Permanent (until entity dissolved + 7 years) |
| Real estate records | Duration of ownership + 7 years |
| FBAR records | 6 years |

### Organization System

```
taxes/
├── 2024/
│   ├── personal/
│   │   ├── us/          # 1040, state returns
│   │   ├── uk/          # Self Assessment
│   │   └── canada/      # T1
│   ├── entities/
│   │   ├── llc_coherence_labs/
│   │   ├── llc_global_trading/
│   │   └── ...
│   ├── source_docs/     # W-2, 1099, K-1, T4, P60
│   ├── fbar/            # FinCEN 114
│   └── correspondence/  # Letters to/from IRS, HMRC, CRA
├── 2025/
│   └── (same structure)
└── entities/
    ├── registry.md      # Master list of all entities
    └── [entity_name]/   # Formation docs, EIN letter, annual reports
```

---

## Automation Opportunities

| Task | Tool | How |
|------|------|-----|
| Bank feed categorization | QuickBooks/Xero | Auto-categorize transactions with rules |
| Receipt capture | QuickBooks mobile / Dext | Photograph receipts, auto-extract data |
| Deadline tracking | Google Calendar + reminders | Recurring events for all filing deadlines |
| FBAR account tracking | Spreadsheet | Update quarterly with max balances |
| Entity status monitoring | Calendar reminders | Annual check of Secretary of State websites |
| Foreign exchange rates | IRS yearly average rates page | Use consistent rates across all filings |

---

## Choosing a Tax Professional

### For Simple US Returns
- **Enrolled Agent (EA):** $150-400 per return. Licensed by IRS to represent taxpayers. Often cheaper than CPAs.
- **CPA:** $250-600+ per return. Broader training than EAs. Required for audits and complex situations.

### For International/Multi-Jurisdiction
- **International CPA firm:** $800-3,000+ per return. Worth it if you have 3+ jurisdictions.
- **Big 4 (Deloitte, PwC, EY, KPMG):** $2,000-10,000+ per return. Overkill for most individuals, but necessary for very complex structures.
- **Mid-tier international (BDO, Grant Thornton, RSM):** $1,000-5,000. Good balance of expertise and cost.

### Key Question
"How many US citizens living in [your country] do you prepare returns for annually?"

If the answer is less than 20, they don't have enough volume to stay current on the rules. Find someone else.
