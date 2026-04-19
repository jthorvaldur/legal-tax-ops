# Legal Technology Tools — Rated by Tier

A practical guide to legal technology, from free tools to enterprise platforms. Rated by what's accessible to individuals vs. what requires firm-level budgets.

---

## Tier 1 — Free / Under $50/month

Tools accessible to any individual, pro se litigant, or solo practitioner.

### Google NotebookLM
- **Cost:** Free
- **What it does:** Upload case documents (PDFs, docs), ask questions, get sourced answers with citations
- **Best for:** Quick case analysis, finding contradictions across documents, preparing for hearings
- **Limitation:** Not a legal research tool — doesn't search case law
- **Verdict:** Surprisingly effective. Upload your filings + opposing party's filings and ask "what are the contradictions?"

### Docketbird
- **Cost:** Free tier available, premium ~$30/mo
- **What it does:** Federal court docket monitoring, alerts, search
- **Best for:** Tracking case activity, getting notified of new filings
- **Limitation:** Federal courts only (PACER-based). State courts need other tools.

### CourtListener (Free Law Project)
- **Cost:** Free
- **What it does:** Free case law search, PACER document access, oral argument audio
- **Best for:** Legal research on a budget
- **Limitation:** Smaller database than Westlaw/Lexis

### Casetext (Basic)
- **Cost:** ~$65/mo for basic legal research
- **What it does:** Case law search with AI-assisted results (CARA)
- **Best for:** Solo practitioners and pro se litigants doing their own research
- **Note:** Now owned by Thomson Reuters, being integrated into Westlaw

### CaseFleet
- **Cost:** ~$45/mo (solo plan)
- **What it does:** Structured fact-to-source linking with timeline visualization. Link every factual claim to the source document that proves it.
- **Best for:** Building a chronological case narrative from scattered evidence
- **Why it matters:** This is what elite litigation teams do manually with paralegals. CaseFleet automates the structure.
- **Verdict:** Best single tool for a pro se litigant organizing complex litigation

### Google Scholar (Legal)
- **Cost:** Free
- **What it does:** Search case law, statutes, and legal journals
- **Best for:** Quick citation checks, finding relevant precedent
- **Limitation:** No Shepardizing (can't check if a case was overruled)

---

## Tier 2 — $50-500/month

Tools that provide significant advantages. Worth the investment for active litigation or ongoing legal needs.

### CoCounsel (Thomson Reuters / Westlaw)
- **Cost:** ~$100-400/mo depending on plan
- **What it does:** GPT-4-powered legal AI. Document review, deposition prep, contract analysis, timeline generation, brief drafting
- **Best for:** Force multiplier for anyone doing their own legal work
- **Key features:**
  - Upload a brief → get counterarguments
  - Upload a contract → get risk analysis
  - Ask a legal question → get sourced answer with citations
  - Timeline builder from documents
- **Who uses it:** Solo practitioners, mid-size firms, increasingly larger firms
- **Verdict:** If you can afford one paid tool, this is it

### Trellis
- **Cost:** ~$99/mo
- **What it does:** State court analytics — judge ruling patterns, success rates on motion types, tendencies
- **Best for:** Knowing your judge before you file. How does Judge X rule on contempt? On modification motions? On discovery disputes?
- **Why it matters:** The #1 advantage experienced lawyers have is knowing the judge. Trellis gives you that data.
- **Coverage:** California, Texas, Florida, New York, and growing. Check availability for your state.
- **Verdict:** Highest ROI tool for litigation strategy

### Lexis+ AI
- **Cost:** ~$120-300/mo
- **What it does:** Legal research with AI, hallucination-checked citations
- **Best for:** Reliable legal research when you need to cite case law
- **Advantage over free tools:** Citations are verified (won't give you fake cases)
- **Verdict:** More reliable than CoCounsel for pure research, less versatile overall

### Clio
- **Cost:** ~$39-89/mo
- **What it does:** Practice management — calendaring, deadlines, document storage, time tracking, billing
- **Best for:** Solo practitioners managing multiple matters
- **Family use:** Good for tracking deadlines across multiple family members' legal/tax matters

### Smokeball
- **Cost:** ~$49-99/mo
- **What it does:** Auto-generates documents, tracks time, family-law-specific templates and workflows
- **Best for:** Family law practitioners specifically
- **Key feature:** Pre-built family law document templates for many states

### vLex Vincent AI
- **Cost:** ~$50-100/mo
- **What it does:** AI-powered case law research, more affordable than Westlaw/Lexis
- **Best for:** International legal research (strong coverage outside US)
- **Verdict:** Good Westlaw alternative at 1/3 the price

---

## Tier 3 — Enterprise / Firm-Level ($500+/month)

These require firm-level budgets or enterprise contracts. Listed for awareness — if you're working with a firm, ask if they use these.

### Relativity / RelativityOne
- **Cost:** Enterprise pricing (typically $18-25/GB/month + licensing)
- **What it does:** Industry-standard e-discovery and document review platform
- **Who uses it:** Quinn Emanuel, Kirkland & Ellis, most AmLaw 100 firms, government agencies
- **What to know:** If your case involves significant document production (thousands of documents), this is what the other side's lawyers use. Understanding its capabilities helps you know what they can find.

### Everlaw
- **Cost:** Enterprise pricing
- **What it does:** Cloud-native e-discovery with AI-assisted review (Everlaw AI Assistant)
- **Who uses it:** Mid-size to large litigation firms, DOJ, state AGs
- **Advantage over Relativity:** Better UI, cloud-native, strong AI integration
- **What to know:** If opposing counsel uses Everlaw, they can rapidly review thousands of documents with AI clustering and predictive coding

### Harvey AI
- **Cost:** Enterprise only (not available to individuals)
- **What it does:** Custom AI for legal work — research, drafting, analysis
- **Who uses it:** Allen & Overy (now A&O Shearman), PwC, elite firms
- **What to know:** Not accessible to individuals. If opposing counsel's firm uses Harvey, they have AI-assisted brief generation.

### Reveal (Brainspace)
- **Cost:** Enterprise pricing
- **What it does:** AI-driven e-discovery with continuous active learning
- **Who uses it:** Complex commercial litigation, antitrust cases
- **What to know:** Used for cases with millions of documents

---

## Courtroom Presentation

### TrialPad (iPad)
- **Cost:** ~$130 one-time
- **What it does:** Present exhibits in court from an iPad. Highlight, annotate, zoom.
- **Best for:** Making a professional impression at hearings
- **Verdict:** Small investment, big impact. Judges notice when you present clearly.

### ExhibitManager
- **Cost:** ~$50-100/mo
- **What it does:** Organize and present trial exhibits
- **Best for:** Cases with many exhibits

---

## Family Law Specific

### OurFamilyWizard (OFW)
- **Cost:** ~$100/year per parent
- **What it does:** Court-approved co-parent communication platform
- **What to know:** Often court-ordered. All messages are logged and admissible. Use it professionally — assume the judge reads everything.

### SupportPay
- **Cost:** Free basic, ~$10/mo premium
- **What it does:** Track child support and shared expenses
- **Best for:** Documenting payment compliance

---

## DIY Legal Tech Stack

If you're building your own system (as a developer or technical user), here's what replicates enterprise tools at near-zero cost:

| Enterprise Tool | DIY Equivalent | Cost |
|----------------|----------------|------|
| Relativity (doc review) | Qdrant + local embeddings + Python pipeline | Free (your time) |
| Everlaw (AI review) | Claude API + structured prompts | ~$20-50/mo API usage |
| CaseFleet (fact linking) | Markdown + YAML + static HTML generator | Free |
| Clio (case management) | GitHub Issues + calendar integration | Free |
| Document generation | WeasyPrint + Markdown + Jinja2 templates | Free |

**What you gain:** Full control, no vendor lock-in, your data stays local
**What you lose:** Polished UI, collaboration features, legal-specific integrations, Shepardizing

---

## Recommendation Matrix

| Situation | Top Pick | Runner-Up |
|-----------|----------|-----------|
| Active pro se litigation | CoCounsel | CaseFleet + Google Scholar |
| Need to know your judge | Trellis | Ask a local attorney |
| Organizing thousands of documents | CaseFleet | DIY with embeddings |
| Family law specifically | Smokeball | Clio |
| On a strict budget | Google NotebookLM + CourtListener | Google Scholar + CaseFleet |
| Building a case timeline | CaseFleet | DIY with structured markdown |
| Presenting in court | TrialPad | PDF on laptop screen |
| Multi-matter management | Clio | Notion + calendar |
