# AI Tools for Legal Research and Drafting

The legal profession is being transformed by AI. Here's what works, what doesn't, and how to use it responsibly.

---

## The Big Three Legal AI Platforms

### CoCounsel (Thomson Reuters)
- **Built on:** GPT-4 with legal fine-tuning
- **Access:** Via Westlaw subscription
- **Key capabilities:**
  - **Document review** — upload contracts, briefs, discovery; get summaries and risk flags
  - **Legal research** — ask questions, get cited answers
  - **Deposition prep** — upload transcripts, generate question lists
  - **Timeline builder** — upload documents, auto-generate chronology
  - **Brief drafting** — generate first drafts with citations
- **Reliability:** Citations are verified against Westlaw database
- **Best for:** Solo practitioners who need a research associate

### Harvey AI
- **Built on:** Custom GPT-4 implementation
- **Access:** Enterprise only (firm-level contracts)
- **Key capabilities:** Similar to CoCounsel but custom-tuned for each firm's practice areas
- **Who uses it:** Allen & Overy (A&O Shearman), PwC Legal, Macfarlanes
- **Availability:** Not accessible to individuals

### Lexis+ AI
- **Built on:** LexisNexis data + GPT integration
- **Access:** Via Lexis subscription
- **Key capabilities:**
  - Conversational legal research
  - Hallucination-checked citations (linked to Lexis database)
  - Document drafting assistance
- **Advantage:** Strong citation verification — less likely to hallucinate cases
- **Best for:** Pure legal research (less versatile than CoCounsel overall)

---

## Using General AI for Legal Work

### Claude, GPT-4, Gemini for Legal Tasks

**What they're good at:**
- Explaining legal concepts in plain language
- Identifying arguments and counterarguments
- Drafting first-draft motions and briefs
- Analyzing contracts for common issues
- Organizing facts into timelines
- Summarizing long documents

**What they're bad at (critical):**
- **Case law citations** — general AI models frequently hallucinate case names, citations, and holdings. NEVER cite a case from AI without verifying it exists.
- **Jurisdiction-specific rules** — may give you California procedure when you need Illinois
- **Current law** — training data has a cutoff. Recent statute changes may not be reflected.
- **Strategic judgment** — can analyze but can't weigh the political/practical dynamics of your specific judge and court

### Safe Workflow for Using AI in Legal Work

1. **Use AI for structure, not authority** — Let it organize your arguments, draft outlines, identify issues. Don't let it be your sole source for case citations.
2. **Verify every citation** — Look up every case AI cites on Google Scholar, CourtListener, or Westlaw/Lexis. Confirm the case exists, the citation is correct, and the holding matches what AI claims.
3. **Use AI to find arguments, then research them yourself** — If AI suggests "argue laches," go research laches in your jurisdiction to see if it actually applies.
4. **Never file AI output directly** — Always rewrite in your voice, verify facts, and add your case-specific details.
5. **Disclose if required** — Some courts now require disclosure of AI use in filings. Check your jurisdiction's rules.

---

## Building Your Own Legal AI Pipeline

For technically inclined users, here's what a DIY legal AI system looks like:

### Components
| Component | Tool | Purpose |
|-----------|------|---------|
| Document storage | Local filesystem (markdown) | All documents in structured format |
| Vector database | Qdrant (local Docker) | Semantic search across all documents |
| Embeddings | nomic-embed-text via Ollama | Convert text to searchable vectors |
| Local LLM | Llama 3.1 8B via Ollama | Summarization, fact extraction, classification |
| Advanced analysis | Claude API / GPT-4 API | Complex legal reasoning, cross-document analysis |
| Document generation | WeasyPrint + Jinja2 | Court-ready PDF output |
| Search interface | Python CLI | Query your entire document corpus semantically |

### What This Gives You
- **Semantic search across all case documents** — "find everything about financial disclosure" returns relevant paragraphs from emails, filings, and notes
- **Automatic summarization** — generate summaries of long documents
- **Fact extraction** — identify dates, amounts, claims across thousands of documents
- **Contradiction detection** — find where opposing party's statements conflict with evidence
- **Timeline generation** — auto-build chronology from document dates

### What It Costs
- Hardware: M-series Mac (you probably already have one)
- Software: All open source (Ollama, Qdrant, Python)
- API costs: ~$20-50/month for Claude/GPT-4 API calls (optional — local LLM handles most tasks)
- Your time: Initial setup ~8-16 hours, ongoing maintenance ~1 hour/week

---

## Court Rules on AI

As of 2025-2026, various courts have adopted rules on AI:

- **Federal courts:** Several districts require disclosure of AI use. Check local rules.
- **State courts:** Varies widely. Some require disclosure, some are silent.
- **Best practice:** Disclose voluntarily. Judges respect transparency and punish concealment.
- **The Mata v. Avianca disaster:** In 2023, a lawyer used ChatGPT and cited fake cases. Sanctioned. This case is now the cautionary tale every judge knows. Don't be that lawyer.

### Bottom Line
AI is a power tool. Like any power tool, it amplifies your capability and your mistakes equally. Verify everything. Disclose usage. Use it for speed, not as a substitute for understanding.
