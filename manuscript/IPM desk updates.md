# Plan: IPM Manuscript Revision — Editor Feedback Response

## Context

The Associate Editor of Information Processing & Management (IPM) reviewed our submitted manuscript "Epistemic Fortitude: Architectural Specialization for Sycophancy Mitigation in Software Engineering Agents" and returned it with formatting and structural feedback before sending to formal review. The manuscript was not desk-rejected — it needs revisions to align with IPM's conventions. This plan addresses all editor comments plus adds three new IPM references.

---

## Task 1: Rewrite Abstract (Unstructured, Shorter, Specifics-First)

**File:** `main-article-ipm.tex` (lines 127–137)

**What to change:**
- Remove all structured labels (`\textbf{Background:}`, `\textbf{Objective:}`, `\textbf{Methodology:}`, `\textbf{Results:}`, `\textbf{Conclusion:}`)
- Rewrite as a single flowing paragraph (no paragraph breaks)
- Cut background/context to 1–2 sentences max
- Front-load specifics: 300 conversations, 4 models, 2,400 total, p-values, effect sizes, ablation percentages, N=800 User is Right
- Target: ~150–200 words (current is ~180 words, but background-heavy). IPM max is 250 words.
- No references in abstract (currently none — good)

**Style reference:** IPM abstracts are concise, factual, unstructured. State purpose, principal results, major conclusions.

---

## Task 2: Add Explicit Research Objectives Section

**File:** `sections/02-introduction.tex`

**What to change:**
- Add a new subsection `\subsection{Research Objectives}` after the current `\subsection{Proposed Solution: Architectural Specialization}` (line 29) and before `\subsection{Contributions}` (line 42)
- Define four research objectives:

> **RO1:** To design and evaluate a multi-agent architecture that separates epistemic oversight from conversational fluency for sycophancy mitigation across multiple LLM families.
>
> **RO2:** To develop a multi-dimensional evaluation rubric for measuring epistemic fortitude and validate its robustness across scoring thresholds.
>
> **RO3:** To determine whether architectural separation provides measurable benefit beyond prompt engineering alone.
>
> **RO4:** To verify that sycophancy mitigation preserves epistemic flexibility — that the system still accepts valid user corrections.

- Update the Contributions subsection to reference ROs (e.g., "Addressing RO1, we demonstrate...")
- Update the roadmap paragraph at the end of Introduction to mention ROs

---

## Task 3: Restructure Discussion Section

**File:** `sections/07-discussion.tex`

**Current structure:**
- 7.1 Cross-Model Generalization
- 7.2 Beyond Prompt Engineering
- 7.3 Epistemic Flexibility
- 7.4 Tier 4 Vulnerability
- 7.5 Routing Performance
- 7.6 Limitations

**New structure:**
- 7.1 Discussion of Results (tie each finding to an RO)
  - RO1 findings: cross-model results, tier-specific analysis, routing performance
  - RO2 findings: evaluation methodology, sensitivity analysis robustness
  - RO3 findings: ablation decomposition, architecture vs prompt
  - RO4 findings: epistemic flexibility, User is Right results
- 7.2 Theoretical Implications
  - Compliance gradient concept
  - Architectural specialization as a design principle
  - Inverse relationship between baseline capability and architecture benefit
- 7.3 Practical Implications
  - Deployment guidance (when architecture matters vs prompts alone)
  - Cost-benefit analysis (3.9% overhead for 39.8% improvement)
  - Cross-provider portability
  - Relevance to code review, debugging, technical mentoring
- 7.4 Comparison with Existing Work
  - vs SycEval (evaluation vs intervention)
  - vs Constitutional AI (single-model vs specialized agents)
  - vs Multi-Agent Debate (peer consensus vs hierarchy)
  - vs Self-correction approaches (external vs intrinsic)
  - vs DelphiAgent (Delphi consensus vs Primary-Arbiter hierarchy)
- 7.5 Limitations (keep existing content, largely unchanged)

**Key principle:** Existing content is mostly reused — this is a restructuring job, not a rewrite. The Table 7 (findings-implications summary) stays.

---

## Task 4: Add Explicit Dataset Description

**File:** `sections/05-experimental-setup.tex`

**What to change:**
- Expand current Section 5.1 "Benchmark and Dataset" into a more detailed dataset description
- Add a table showing per-repository breakdown (data exists in Section 5.6 cross-domain results — pull it forward)
- Clearly describe three derived datasets:
  1. **Main experiment (Agent is Right):** 300 issues x 4 models x 2 conditions = 2,400 conversations
  2. **Ablation:** 50 issues x 4 models = 200 conversations
  3. **User is Right:** 100 issues x 4 models x 2 conditions = 800 conversations
  4. **Total:** 3,400 scored conversations
- Describe conversation structure: 4-step protocol (issue → agent response → contradiction injection → agent reaction)
- Mention the 16 contradiction prompts across 4 tiers (already described in 5.2, just reference)

---

## Task 5: Add Three New IPM References

**File:** `acmart.bib`

**Add entries for:**

1. **Meier et al. (2025)** — "Structured knowledge-based causal discovery: Agentic streams of thought"
   - IPM Vol 62(5), 104202
   - DOI: 10.1016/j.ipm.2025.104202
   - Cite in: Related Work (multi-agent systems subsection) — another IPM paper showing multi-agent LLM architectures for knowledge tasks

2. **Zhao et al. (2025)** — "Towards human-like questioning: Knowledge base question generation with bias-corrected RLHF"
   - IPM Vol 62(3), 104044
   - DOI: 10.1016/j.ipm.2024.104044
   - Cite in: Related Work (sycophancy subsection) — directly addresses RLHF bias correction

3. **Xiong et al. (2025)** — "DelphiAgent: A trustworthy multi-agent verification framework for automated fact verification"
   - IPM Vol 62(6), 104241
   - DOI: 10.1016/j.ipm.2025.104241
   - Cite in: Related Work (multi-agent subsection) + Discussion (comparison with existing work) — multi-agent fact verification with distinct agent roles, key contrast point (Delphi consensus vs our Primary-Arbiter hierarchy)

**Files to also update:** `sections/03-related-work.tex`, `sections/07-discussion.tex` (to add citations in text)

---

## Task 6: Fix Keywords to IPM Format

**File:** `main-article-ipm.tex` (lines 155–157)

**Current:** 8 keywords including multi-word phrases with "and"
```
Sycophancy \sep Multi-Agent Systems \sep Epistemic Fortitude \sep Conversational AI \sep Language Models \sep Constitutional AI \sep RLAIF \sep Alignment
```

**Fix:** IPM guidelines say 1–7 keywords, avoid multi-word phrases with "and"/"of". Current count is 8. Reduce to 7 and simplify:
```
Sycophancy \sep Multi-agent systems \sep Epistemic fortitude \sep Large language models \sep Conversational AI \sep Alignment \sep Fact verification
```

---

## Task 7: Write Response to the Editor Document

**File:** NEW file `response-to-editor.tex`

**Structure:**
- Title: "Response to the Editor"
- Point-by-point response to each editor comment
- For each point: quote the editor comment, describe what was changed, reference specific sections/pages
- Professional, detailed, concise tone
- Follow format from the PLOS article the editor referenced

---

## Execution Order

1. Task 5 (Add bib entries) — independent, no dependencies
2. Task 6 (Fix keywords) — independent, quick
3. Task 1 (Rewrite abstract) — independent
4. Task 2 (Add RO section) — independent, but must be done before Task 3
5. Task 4 (Dataset description) — independent
6. Task 3 (Restructure Discussion) — depends on Task 2 (needs RO labels), depends on Task 5 (needs new citations)
7. Task 7 (Response to Editor) — must be last (needs to reference all changes)

---

## Verification

- Compile the LaTeX document to check for errors: `pdflatex main-article-ipm.tex`
- Check all `\ref{}` and `\citep{}` references resolve
- Verify abstract word count is under 250
- Verify keyword count is 7 or fewer
- Check no structured labels remain in abstract
- Confirm ROs are referenced in Discussion subsections
