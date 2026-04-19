# Managing Multiple LLCs Across States

How to track, maintain, and (if necessary) dissolve entities you've created — including ones you forgot about.

---

## The Forgotten Entity Problem

If you formed an LLC and stopped using it, it doesn't go away. Most states:
- Continue charging annual fees/franchise taxes
- Impose late penalties
- Eventually "administratively dissolve" the entity — but this doesn't end your obligations
- May refer unpaid fees to collections
- Report to the state's Secretary of State, which is public record

**First step:** Audit every entity you've ever created.

---

## Entity Audit Checklist

For each entity you have (or think you might have), document:

| Field | Example |
|-------|---------|
| Entity name | Coherence Labs IP LLC |
| State of formation | Wyoming |
| Date formed | 2023-06-15 |
| Entity type | LLC (single-member) |
| EIN (if obtained) | 87-XXXXXXX |
| Registered agent | Northwest Registered Agent |
| Annual report due | First day of anniversary month |
| Franchise tax | $60/year (Wyoming) |
| Status | Active / Delinquent / Admin dissolved |
| Bank account? | Yes — Chase business checking |
| Revenue? | Yes / No |
| Tax returns filed? | 2023: Yes, 2024: No |
| State tax nexus | Wyoming (no income tax) |

Use the template at `templates/entity-registry.md` to track all your entities.

---

## State-by-State Entity Costs

### Low-Cost States (Popular for Formation)

| State | Formation | Annual Fee | Income Tax | Notes |
|-------|-----------|-----------|------------|-------|
| Wyoming | $100 | $60 | None | Privacy-friendly, low cost, no state income tax |
| Delaware | $90 | $300 | 8.7% on DE-sourced income | Popular for corporations, less useful for LLCs without DE operations |
| Nevada | $75 | $150 + $200 business license | None | Higher fees than Wyoming for same benefits |
| New Mexico | $50 | $0 | 4.8-5.9% | No annual report, cheapest to maintain |
| Texas | $300 | $0 (if under threshold) | No income tax, franchise tax if revenue > $2.47M | Good for businesses with TX operations |

### States That Will Surprise You

| State | Annual Fee | Income Tax | Watch Out For |
|-------|-----------|------------|---------------|
| California | $800/year minimum franchise tax | 8.84% corporate / 1.5% LLC fee | $800 due even if LLC earns $0. Many people form CA LLCs, forget, and owe thousands. |
| New York | $25 filing, but **publication requirement** | 6.5-10.9% | Must publish formation notice in 2 newspapers ($1,500-2,000 in NYC counties). Non-compliance = suspended. |
| Illinois | $75 | 9.5% corporate (4.95% personal) | Annual report $75/year. Failure = involuntary dissolution. |
| Massachusetts | $520 | 8% corporate / 5% personal | High formation and annual costs |

---

## How to Find Forgotten Entities

1. **Search your email** for: "articles of organization," "EIN," "registered agent," "annual report due," "franchise tax"
2. **Search Secretary of State websites** in every state you've lived in or done business:
   - [Wyoming](https://wyobiz.wyo.gov/Business/FilingSearch.aspx)
   - [Delaware](https://icis.corp.delaware.gov/ecorp/entitysearch/namesearch.aspx)
   - [California](https://bizfileonline.sos.ca.gov/search/business)
   - Most states have free online entity search
3. **Search the IRS** — if you got an EIN, the IRS has a record. Call (800) 829-4933.
4. **Check your tax returns** — any Schedule C, Schedule E, or K-1 references an entity
5. **Ask your registered agent** — if you used Northwest, LegalZoom, etc., they have records of all entities they service for you

---

## Annual Maintenance Calendar

| Month | Task |
|-------|------|
| January | Review all entity statuses. Pay any annual fees due in Q1. |
| February-March | Gather tax documents for all entities |
| April | File federal returns (or extensions) for all entities |
| Entity anniversary month | File annual report for each entity (check your state) |
| Quarterly | Review registered agent invoices — if you're paying for an agent for an entity you don't use, dissolve it |
| December | Year-end review: should any entities be dissolved? Created? |

---

## Multi-Member LLC Considerations

If your LLC has more than one member:

- **Operating agreement is mandatory** (even if your state doesn't require it — you need one)
- **Tax classification:** Multi-member LLC defaults to partnership (Form 1065 + K-1s to each member)
- **Each member reports their share** on their personal return
- **Self-employment tax** applies to active members (15.3% on first ~$160K, 2.9% above)
- **Distribution provisions** should be documented (who gets what, when, how)
- **Buyout provisions** should be documented (what happens if a member leaves/dies/divorces)

---

## When to Dissolve an Entity

Dissolve if:
- The entity has no revenue, no assets, and no purpose
- You're paying annual fees for something you don't use
- The entity is in a high-fee state (California's $800/year minimum adds up)
- The entity creates filing obligations you're not meeting

### How to Dissolve

1. **Check state requirements** — most need Articles of Dissolution filed with Secretary of State
2. **File final tax returns** — federal and state. Mark them as "final"
3. **Close the EIN** — send a letter to the IRS (you can't close an EIN online)
4. **Close bank accounts** associated with the entity
5. **Cancel registered agent** — notify your agent once dissolution is filed
6. **Keep records** — retain formation docs, tax returns, and dissolution docs for 7+ years

### What If You're Delinquent?

If you haven't filed annual reports or paid fees:

1. **Check if the entity is still active** on the state's website
2. **If administratively dissolved:** You may need to reinstate before you can formally dissolve, or just let it stay dissolved (varies by state)
3. **Pay outstanding fees** — most states require this before dissolution
4. **File any missing tax returns** — delinquent entities can trigger IRS penalties
5. **Consider the Streamlined Filing program** if federal returns are missing

---

## Entity Structure Patterns

### Solo Founder — One Business
```
Personal (1040)
  └── Operating LLC (single-member, Schedule C)
```

### Solo Founder — IP + Operations Separation
```
Personal (1040)
  ├── IP Holdings LLC (Wyoming — holds IP, licenses it)
  └── Operating LLC (state of operations — pays license fee to IP LLC)
```

### Multiple Founders — Joint Venture
```
Founder A (1040)          Founder B (1040)
  └── JV LLC (1065) ←──── K-1 to each
```

### International — US Person Working Abroad
```
Personal (1040 + FBAR + FATCA)
  ├── US LLC (domestic operations)
  └── Foreign employer (W-2 equivalent + Form 1116 FTC)
```

### Family Coordination
```
Parent A (1040)
  ├── Business LLC
  └── Joint tax coordination with:
        Parent B (1040)
          └── Business LLC
        Child (1040 — if filing)
          └── UTMA/529 accounts
```
