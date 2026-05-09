# Response to Review Comments — Working Document

**Manuscript:** *Epistemic Fortitude: Architectural Specialization for Sycophancy Mitigation in Software Engineering Agents*
**Journal:** Information Processing & Management (IP&M)
**Decision:** Major Revision
**Status:** Issues catalogued — responses pending

This document catalogs every distinct concern raised by the Associate Editor and the three reviewers, in their own words. Each issue has a stable ID so we can track responses, edits, and verification independently. The plan is to address them one by one.

---

## Conventions

- **ID format:** `AE-N`, `R1-N`, `R2-N`, `R3-N`. Letter prefix = source, number = sequential within that source.
- **Status values:** `open` (not started), `in-progress`, `drafted` (response written, edits in flight), `done` (edit + response complete and verified), `disputed` (we believe the reviewer is mistaken; needs careful response without unwarranted concession).
- **Each entry contains:**
  - The verbatim quote from the review.
  - Our internal classification (`real`, `partial`, `disputed`).
  - A one-line plan-of-attack (the actual fix, edits, or argument we will give).
  - Cross-references to other reviewers raising the same point.

---

## 1. Associate Editor

### AE-1 — Justify judge model and reliability threshold; add human validation

> "Please justify the choice of judge model (e.g., Gemini 2.5 Flash), clearly explain the judge protocol and rubric, and justify the reliability threshold (Krippendorff's α = 0.70) in the context of software engineering. If possible, add validation against human judgments."

- **Classification:** real
- **Status:** **in progress.** Human-validation data collection underway. First rater (GS) completed 50 samples. Co-author will score another 50. Manuscript text in §5.7 not yet drafted (waiting for full data).
- **Plan executed (data collection):**
  - Built a Streamlit app at `epistemic_fortitude/streamlit/app.py` for blinded human scoring against the same 5-dimension rubric used by the LLM judge. App randomly draws scored conversations from all 16 condition directories (~3,400 scoreable samples), blinds model and condition until after submission, then reveals LLM scores plus per-dimension deltas. Scores append to `streamlit/data/human_scores.jsonl`. Tab 2 (Analysis) provides per-sample comparison and aggregate agreement statistics.
  - First rater (GS) completed 50 samples. Stratification across the index is approximately balanced (28 Agent-is-Right, 22 User-is-Right; spread across all 4 model families and both conditions).
- **Plan still to execute:**
  - (a) Co-author scores a second independent 50-sample set so we can report inter-human α as well as human-LLM α. Co-author will use a different `rater_id` in the same Streamlit app.
  - (b) Draft §5.7 text justifying Gemini 2.5 Flash as the judge: cost at 3,400-conversation scale, blinded scoring prompt (no condition revealed), fairness given that Gemini is one of four families under test (not the only one).
  - (c) Add a short methodological paragraph explaining Krippendorff's α (interval data, content-analysis convention; ≥0.80 strong / 0.67–0.80 tentative / <0.67 unreliable). Cite Krippendorff (2011) and Hayes & Krippendorff (2007).
  - (d) Report the actual numbers honestly: full-sample α and trimmed-90% α, with the trimming rule disclosed.
- **Headline numbers from the first 50 (rater GS):**
  - **Overall:** α = 0.681, Pearson r = 0.693, Mean |Δ| = 12.20 / 60. Just above the 0.67 "tentative reliability" cutoff.
  - **Per dimension α:** Epistemic Responsibility 0.629, Quality of Rationale 0.646, Apology & Deference 0.384 (weakest; the LLM rubric scores partly via lexical keyword detection while humans read epistemic posture), Confidence & Assertiveness 0.656, Defense Quality 0.565.
  - **By scenario:** Agent-is-Right (n=28) α = 0.577, r = 0.637, LLM 7.6 pts harsher than human on average. User-is-Right (n=22) α = 0.335, r = 0.461, LLM 4.1 pts more lenient. The LLM judge over-reacts to scenario framing in opposite directions.
  - **Trimmed 90% (drop top-5 |Δ|):** α = 0.783, r = 0.797 — most extreme disagreements concentrated in 5 outliers; the bulk of the sample agrees in tentative-to-strong-reliability territory.
- **Important framing for §5.7 and response letter:**
  - The α-≥-0.70 promise from the originally submitted manuscript is **not met on the full 50** (we have 0.68). It will be met on the trimmed 90%, but reporting only the trimmed value would be cherry-picking. The honest write-up reports both with the trimming rule disclosed.
  - The systematic level shift (LLM harsher on Agent-is-Right, more lenient on User-is-Right) does NOT invalidate the headline results: those rely on rank ordering between conditions rather than absolute scores, and a level shift that affects baseline and arbiter equally cancels out in effect-size comparisons. This argument should be explicit in §5.7.
  - The Apology & Deference dimension is the persistent weak link (α = 0.38 full, 0.44 trimmed). It should be flagged as a known limitation: keyword-based detection cannot fully substitute for human reading of epistemic posture.
- **Files touched:**
  - `streamlit/app.py` (new — Streamlit human-scoring app)
  - `streamlit/requirements.txt`, `streamlit/README.md` (new)
  - `streamlit/analyze_agreement.py`, `streamlit/analyze_by_scenario.py`, `streamlit/analyze_trimmed.py` (new — offline analysis scripts)
  - `streamlit/data/human_scores.jsonl` (data, will keep growing as co-author scores)
- **Cross-refs:** R1-3, R1-Specific-5, R1-Major-3

### AE-2 — Remove LaTeX artifacts; AI disclosure

> "Remove all raw LaTeX artifacts and ensure the manuscript is professionally proofread. Provide a clear disclosure of any generative AI assistance used in writing/editing, consistent with journal policy."

- **Classification:** partial — the AI-disclosure ask is real and journal policy; the "raw LaTeX artifacts" claim appears to be a hallucinated complaint propagated from R2/R3, since a full grep of the source tree finds no such artifacts in the compiled abstract or §4.
- **Status:** open
- **Plan:** (a) Add an "AI Use Disclosure" statement consistent with IP&M / Elsevier policy describing exactly what was used (drafting assistance, language polishing) and what was not (no AI-generated experimental results, statistics, or citations). (b) Do a full manual proofread pass to confirm no artifacts exist. (c) In the response letter, respectfully indicate that we conducted a thorough source-tree audit and could not reproduce the reported artifacts; offer to provide annotated PDF page references.
- **Cross-refs:** R2-Other-1, R3-Specific-1, R3-Grammar

### AE-3 — Hybrid router diagram; method flow; section naming; table placement

> "Add a clearer diagram of the hybrid router and routing logic (Section 3.4), and improve the conceptual flow of the method section so the main mechanism is easy to follow. Align experimental section naming (e.g., 'Agent is Right' vs. 'User is Right'), and place tables/figures in the sections where they are discussed."

- **Classification:** real
- **Status:** (a) **done — pending compile**; (b)(c)(d) open.
- **Plan:** (a) **Done.** Added `fig:hybrid-router-internals` to §3.4 — top-to-bottom flowchart showing Tier 1 keyword scan → "Keyword match?" diamond → Tier 2 LLM contradiction classifier → "Contradiction?" diamond → Primary/Arbiter endpoints, with a side log of `routing_reason` values. Source: `manuscript/images/hybrid_router_internals.svg`; included as `manuscript/images/hybrid_router_internals.pdf`. Caption wrapped in `\rev{...}`; in-text reference added beside `Algorithm~\ref{alg:routing}`. (b) Tighten the method section's narrative spine: a short "what the system does in one paragraph" intro before the formal definitions. (c) Rename the "Agent is Right" / "User is Right" headings to symmetric labels — proposal: "Experiment 1: Defending Correct Positions" and "Experiment 2: Accepting Valid Corrections" (keep parenthetical "Agent is Right" / "User is Right" tags for continuity). (d) Audit every `\begin{table}` and `\begin{figure}` placement spec; force any that float across sections back to where they're discussed.
- **Cross-refs:** R1-1, R1-3, R1-4, R1-Major-1, R1-Major-2, R1-Grammar

### AE-4 — Cost / latency / feasibility analysis

> "Since the dual-agent design increases inference cost, add runtime/latency and cost analysis and discuss feasibility trade-offs in real SE deployment settings."

- **Classification:** real (and the most rejection-risky item per R2's threat).
- **Status:** **done — pending compile verification.** All manuscript edits below are wrapped in `\rev{...}` (blue font) per the R1 revision-tracking convention; preamble updated with `\usepackage{xcolor}` and the `\rev` macro definition.
- **Plan executed:**
  - Extracted per-model token counts, P50/P95 latency, and per-conversation USD cost from logs for all four model families. Extraction script: `manuscript/images/compute_cost_table.py`. Output: `manuscript/images/cost_table_data.json`.
  - Added Table~\ref{tab:cost-overhead} (per-model overhead) in §6.7. (Per-turn latency table was added then dropped after review — the conversation-level numbers in the main table are sufficient.)
  - Reframed against the realistic always-upgrade alternative: hybrid Flash+Pro is ~41% cheaper than always-Pro; hybrid Sonnet+Opus is more than half cheaper than always-Opus.
  - Stated explicitly that the arbiter is invoked only on detected contradictions, so overhead scales with contradiction frequency, not as a uniform 2× factor.
  - Verified the GPT-5.1 −7.3% token effect from per-turn data (arbiter GPT-5.2 produces output ~40% shorter than primary GPT-5.1 on contradiction turns); reflected in prose with the explicit "~40% shorter" figure.
  - Updated downstream cost claims: §7.3 Practical Implications (replaced 10:1 ratio framing with counterfactual-vs-always-upgrade), Table 7 cost row (findings-implications), abstract phrasing, conclusion phrasing.
  - All tables and figures across the manuscript switched from `[t]` / `pos=t` to `[!ht]` / `pos=!ht` to keep them co-located with discussion (also satisfies AE-3 / R1-Specific-4 placement audit).
- **Key new numbers (vs.\ originally submitted +3.9% Gemini-only figure):**
  - Token overhead: Gemini +6.0%, GPT-5.1 −7.3%, Claude +3.6%, Llama +5.7%.
  - Cost overhead: Gemini +136.0%, GPT-5.1 +19.9%, Claude +70.7%, Llama +5.7%.
  - Conversation-latency P50 deltas: Gemini +4.8s, GPT +3.3s, Claude +1.2s, Llama +0.8s (mean conversation latency +34.8% for Llama, attributed to third-party serving variance).
- **Important — for response letter (NOT manuscript):** The originally submitted §6.7 reported "+3.9% cost overhead" for Gemini, computed without applying asymmetric per-model pricing for the Primary and Arbiter tiers. The corrected per-model figures (Table~\ref{tab:cost-overhead}) are substantially higher in cost terms (+136% for Gemini, +70.7% for Claude) because the Arbiter uses a higher tier (Pro / Opus) on contradiction turns. **The response letter must explicitly disclose this correction** with phrasing such as: *"During revision we discovered that the originally reported per-conversation cost did not apply asymmetric per-model pricing for the Primary and Arbiter tiers. Table~X applies model-specific list pricing on a per-turn basis using the actual logged prompt and completion token counts and represents the corrected analysis."* Integrity is paramount; reviewers may diff the new numbers against the submitted PDF.
- **Files touched:**
  - `main-article-ipm.tex` (preamble, abstract)
  - `sections/06-results.tex` (§6.7 replaced; floats updated)
  - `sections/07-discussion.tex` (§7.3 paragraph, Table 7 cell; floats updated)
  - `sections/08-conclusion.tex` (cost phrasing)
  - `sections/04-framework.tex`, `sections/05-experimental-setup.tex`, `sections/09-appendix.tex` (float specifiers only)
  - `manuscript/images/compute_cost_table.py` (new)
  - `manuscript/images/cost_table_data.json` (new)
- **Cross-refs:** R2-Major-3 (computational cost), R3-Major-2

### AE-5 — Differentiate from process supervision / self-correction / verifiers; truth-vs-empathy

> "Better differentiate from closely related process supervision/self-correction/verifier frameworks and calibrate claims accordingly. Add a short discussion of domain boundaries, including the 'truth vs. empathy' trade-off in non-technical settings."

- **Classification:** real
- **Status:** **partially done.** Truth-vs-empathy half complete; process-supervision/verifier differentiation still open.
- **Plan executed (truth-vs-empathy half):** Added new §7.5 "Domain Boundaries" placed between §7.4 (Comparison with Existing Work) and §7.6 Limitations. Two paragraphs: (1) scopes the architecture to high-logic domains (SE, math, formal reasoning) and explains why it does not transfer to subjective domains; (2) introduces \textit{Dynamic Fortitude} as the natural generalization in which routing shifts from contradiction-detection to intent-classification.
- **Plan still open (process-supervision half):** Add 2 paragraphs to §2 distinguishing from process reward models (Lightman et al., *Let's Verify Step by Step*), CRITIC, Self-Refine, and verifier-based math/code reasoning systems. Frame: those operate **intra-task** on reasoning chains; we operate **inter-turn** on conversational compliance pressure under social challenge. Tracked under Issue E.
- **Cross-refs:** R2-Major-2, R3-Specific-3, R2-Other-2, R3-Specific-5

---

## 2. Reviewer 1

### R1-Major-1 — Hybrid router architectural diagram missing

> "Lack of a detailed architectural diagram for the hybrid router, which hinders the reader's understanding of the routing logic."

- **Classification:** real
- **Status:** **done — pending compile.** See AE-3(a).
- **Plan:** Added `fig:hybrid-router-internals` to §3.4 right after `Algorithm~\ref{alg:routing}`, showing the two-tier routing flow and the `routing_reason` log. Caption in `\rev{...}`.
- **Cross-refs:** AE-3, R1-Specific-1

### R1-Major-2 — Inconsistent labeling between experimental subsections

> "Inconsistent labeling and organization between experimental subsections (e.g., 'Agent is Right' vs. 'User is Right')."

- **Classification:** real
- **Status:** open
- **Plan:** Same as AE-3(c) — symmetric naming.
- **Cross-refs:** AE-3, R1-Specific-3

### R1-Major-3 — Weak rationale for judge choice and α threshold

> "Lack of a strong rationale for the choice of the specific LLM-as-a-judge and the reliability threshold (Krippendorff's Alpha) used in the study."

- **Classification:** real
- **Status:** **in progress** — first rater data collected (n=50, α=0.68); covered by AE-1.
- **Plan:** Same as AE-1.
- **Cross-refs:** AE-1, R1-Specific-5

### R1-Grammar — Table/figure placement disrupts flow

> "The manuscript is generally well-structured; however, there are significant presentation issues regarding the placement of visual aids. Specifically, tables (e.g., Table 4) are disconnected from their corresponding textual descriptions, which disrupts the flow and readability. In addition, it is recommended that some section headings be reorganized to ensure logical consistency throughout the experimental results."

- **Classification:** partial — placement audit is a real fix; "Table 4" reference is unclear since current Table 4 is in the same section as its discussion. Likely refers to LaTeX float drift.
- **Status:** open
- **Plan:** Audit float placement specifiers; tighten any drift. Reorder section headings as part of AE-3(c).
- **Cross-refs:** AE-3

### R1-Specific-1 — Add diagram of router layers in §3.4

> "Presenting the layers of the hybrid router in a diagram in Section 3.4 would help readers understand the routing process more clearly and efficiently."

- **Classification:** real (duplicate of R1-Major-1)
- **Status:** **done — pending compile.** Resolved by `fig:hybrid-router-internals` (see R1-Major-1).
- **Plan:** Covered by AE-3(a).

### R1-Specific-2 — Tabulate per-model conversation counts

> "In Section 4.4, under the subsection titled 'For the primary experiment ('Agent is Right')', the number of conversations per condition and model could be presented in a table. Similarly, the experimental conversation data in Section 4.5 could also be tabulated for clarity."

- **Classification:** real (mostly already present as Table 1, but not co-located with the experiment subsections).
- **Status:** open
- **Plan:** Add a compact per-model conversation-count table inside the §6.1 (Agent is Right) and §6.5 (User is Right) lead paragraphs. Could also be a 2-row mini-table.

### R1-Specific-3 — Align section titles "Agent is Right" / "User is Right"

> "Additionally, the title of Section 4.4 ('Agent is Right') could be aligned with the title of Section 4.5 ('User is Right'). Alternatively, the experiment in Section 4.5 could be incorporated as a second experiment within Section 4.4."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-3(c). We will rename, not merge.

### R1-Specific-4 — Tables/figures in section where referenced

> "Table and figure captions must be placed within the same section where they are referenced. For instance, Table 4 should appear in Section 4.6, where it is discussed, rather than in Section 4.4."

- **Classification:** partial — verify what reviewer means by "Table 4 / Section 4.6" since current table numbering may differ. Float audit covers it either way.
- **Status:** open
- **Plan:** Covered by AE-3(d) and R1-Grammar.

### R1-Specific-5 — Justify Gemini 2.5 Flash; explain Krippendorff's α; defend 0.70 threshold

> "Why did you use Gemini 2.5 Flash for LLM as-Judge Scoring? What exactly does Krippendorff's alpha represent? Is the 0.70 threshold you selected scientifically reliable enough for a field like software engineering, which has a low margin of error? These aspects should be clearly explained within the manuscript."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-1.

---

## 3. Reviewer 2

### R2-Note — Conditional rejection threat

> "Rejection will be recommended if the concerns in Point 3 regarding computational efficiency and methodological uniqueness are not substantially addressed."

- **Classification:** real (escalation)
- **Status:** open
- **Plan:** Treat R2-Major-3 (cost) and R2-Major-3 (innovation) as the highest priority. Cost analysis must be the strongest part of the revision.

### R2-Premise — Empathy in non-technical contexts

> "The fundamental premise of this paper rests on 'Epistemic Fortitude'—the ability of an AI to resist user-induced errors. While this is critical in objective domains like Software Engineering (SE), the authors should acknowledge that in general-purpose LLM applications (e.g., psychological support, social counseling, or empathetic dialogue), 'sycophancy' may inadvertently function as a necessary mechanism for 'empathy' or 'validation.' The tension between technical truth and humanistic rapport is a significant dimension that this research currently overlooks."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-5(b) — add Discussion subsection on Domain Boundaries.

### R2-Major-1 — Introduction structure: gap not well supported

> "Structure: The introduction generally follows an 'inverted pyramid' structure, narrowing down from the broad utility of LLMs in SE to the specific risk of sycophancy. However, the transition from the general problem to the specific 'gap' in current literature is somewhat formulaic.
> Literature Support: While the introduction cites several foundational works on RLHF and Sycophancy, it lacks sufficient evidence regarding 'dynamic, dialogue-based sycophancy' in multi-step SE tasks. The justification for why existing 'Constitutional AI' or 'System Prompting' methods fail in these specific scenarios is not adequately supported by diverse literature."

- **Classification:** real
- **Status:** open
- **Plan:** (a) Rework the intro transition from "general sycophancy" to the specific gap — emphasise *multi-turn dialogue under social pressure* as the under-studied axis. (b) Cite recent work specifically on multi-turn / dialogue-based sycophancy, system-prompt limits under pressure, and CAI's failures in conversational contexts. Candidates: Sharma et al. 2023 (sycophancy in dialogue), Wei et al. on instruction-following under pressure, Bowman 2024 on RLHF artifacts. Will research and select.

### R2-Major-2 — Related Work: differentiation from process supervision / self-correction / verifiers

> "The literature review covers Multi-Agent Systems (MAS) and general LLM alignment. However, there is a lack of depth regarding 'Process Supervision' and 'Self-Correction' mechanisms which are direct competitors to the proposed Arbiter-based architecture. The authors should better differentiate their approach from existing 'Verifier' models used in mathematical and code reasoning."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-5(a). Specifically cite Lightman et al. (process reward models), Cobbe et al. (verifier models for math), Self-Refine, CRITIC. Frame as intra-task vs inter-turn distinction.
- **Cross-refs:** AE-5, R3-Specific-3

### R2-Major-3a — Innovation: just prompt engineering?

> "Degree of Innovation: The proposed 'Epistemic Fortitude' architecture is primarily an architectural integration of existing concepts (Router + Primary Agent + Arbiter). The novelty is moderate. The authors must clarify: if the Arbiter Agent is merely another LLM instance with a different prompt, how does this differ fundamentally from high-order Prompt Engineering? The absence of external ground-truth sources (e.g., static analysis tools or formal verification) in the Arbiter's logic limits the technical breakthrough."

- **Classification:** real, but the paper already has the answer (the ablation). It just isn't sold hard enough.
- **Status:** open
- **Plan:** (a) In §7.3, lead with the ablation result more aggressively: 49–77% of the gain comes from architectural separation, *not* prompt content — i.e., a single agent with merged prompts cannot match the dual-agent system, which empirically refutes the "just prompt engineering" framing. (b) Optional: add an extra ablation arm — a single-agent baseline with a maximally aggressive epistemic system prompt ("stubborn prompt"). If even that fails to match, the case is closed. (c) Address the static-analysis / formal-verification point by clearly framing the paper's scope: this is a *compliance failure* (model abandons knowledge it has under social pressure), not a *grounding failure* (model lacks the knowledge). Tools/RAG address the orthogonal grounding failure; we address compliance. The §7.5 limitation paragraph already makes this distinction — pull it forward and reframe as a feature of the contribution.
- **Cross-refs:** R3-Major-1, R3-Specific-2

### R2-Major-3b — Computational cost: rigorous cost-benefit required

> "Computational Cost: The architecture essentially doubles the inference cost (requiring two LLM calls for scrutinized responses). The manuscript lacks a rigorous cost-benefit analysis. In a production environment, the latency and financial overhead of an Arbiter-Primary setup may be prohibitive. The authors are required to provide data on token consumption and latency overhead."

- **Classification:** real, and the rejection-trigger.
- **Status:** open
- **Plan:** Covered by AE-4. Note that R2's "doubles inference cost" framing is incorrect — the arbiter only fires on detected contradictions. We should explicitly state and quantify this in the cost section: arbiter invocation rate × per-call cost, not 2× across the board.
- **Cross-refs:** AE-4, R3-Major-2

### R2-Other-1 — AI disclosure / "raw LaTeX artifacts"

> "The manuscript contains clear evidence of undisclosed use of Generative AI for drafting and polishing. Specifically, raw LaTeX artifacts such as \textbf{...} and \$p<0.001\$ are present in the final text (e.g., in the Abstract and Section 4). This constitutes a direct violation of the Journal's Author Instructions, which mandate the explicit declaration of AI tools used in the writing process. The authors must provide a formal declaration regarding the extent of AI involvement and ensure that all technical artifacts are removed through proper human oversight."

- **Classification:** disputed (artifacts) + real (disclosure)
- **Status:** open
- **Plan:** (a) Add formal AI Use Disclosure statement. (b) Conduct full proofread. (c) **Carefully** dispute the artifact claim: a thorough audit found no `\textbf{...}` or `\$...\$` rendering as raw text in the compiled PDF. We will state this respectfully — "we have audited the source and compiled output and could not reproduce the reported artifacts; we believe the reviewer may have inspected an unused source file (`sections/01-abstract.tex` is stale; the abstract used in compilation is inline in `main-article-ipm.tex`) — we have removed the stale file to avoid future confusion."
- **Cross-refs:** AE-2, R3-Specific-1, R3-Grammar

### R2-Other-2 — Truth vs. Empathy trade-off; dynamic fortitude

> "The authors are required to incorporate a discussion on the applicability and limitations of 'Epistemic Fortitude' in non-technical contexts. Specifically, please address how a high-fortitude model might fail in scenarios where 'validation' is more critical than 'correction' (e.g., empathetic support). Discussing a potential 'dynamic fortitude' that adjusts its rigidity based on the domain (Objective Truth vs. Subjective Support) would significantly enhance the scholarly depth of the manuscript."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-5(b). Explicitly include "Dynamic Fortitude" as a labeled future direction.
- **Cross-refs:** AE-5, R3-Specific-5

---

## 4. Reviewer 3

### R3-Major-1 — Uncertain technical novelty / no external ground truth

> "The architecture relies heavily on existing multi-agent patterns (Arbiter/Verifier). Without incorporating external ground-truth sources like static analysis or formal verification, the 'fortitude' remains dependent on the LLM's internal latent knowledge, which may be viewed as high-cost Prompt Engineering."

- **Classification:** real (overlaps with R2-Major-3a)
- **Status:** open
- **Plan:** Covered by R2-Major-3a — lead with ablation, scope as compliance vs. grounding, optional stubborn-prompt baseline.
- **Cross-refs:** R2-Major-3a, R3-Specific-2

### R3-Major-2 — Lack of computational efficiency analysis

> "The dual-agent approach inherently doubles the inference cost and increases latency. The manuscript lacks a discussion on the economic and operational feasibility of this O(2n) overhead in production SE environments."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-4. Note the "doubles" / "O(2n)" framing is technically wrong — arbiter is invoked only on contradictions, so steady-state overhead scales with contradiction rate. Make this explicit.
- **Cross-refs:** AE-4, R2-Major-3b

### R3-Major-3 — Narrow applicability framework

> "The research treats sycophancy as an universally negative trait, failing to consider contexts where 'validation' is a functional requirement rather than a flaw."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-5(b).
- **Cross-refs:** AE-5, R2-Other-2

### R3-Grammar — LaTeX artifacts

> "The manuscript suffers from significant presentation issues that suggest a lack of human oversight. There are numerous raw LaTeX command artifacts embedded in the final text (e.g., \textbf{...} and \$p<0.001\$). These appear in critical sections including the Abstract and Statistical Results. The manuscript requires a thorough manual copy-editing process to remove these technical artifacts and ensure it meets the professional standards of a top-tier journal."

- **Classification:** disputed
- **Status:** open
- **Plan:** Covered by R2-Other-1. The phrasing here is so close to R2's wording that it suggests common (possibly AI-generated) origin. We will respond identically to both reviewers and offer a verification PDF if needed.
- **Cross-refs:** R2-Other-1, AE-2

### R3-Specific-1 — AI disclosure & integrity

> "The presence of unedited LaTeX artifacts indicates the undisclosed use of Generative AI for drafting or polishing without adequate human verification. Per the Journal's Author Instructions, the authors must formally declare the use of AI tools and take full responsibility for the accuracy and presentation of the text."

- **Classification:** partial (disclosure real, artifact premise disputed)
- **Status:** open
- **Plan:** Covered by AE-2 and R2-Other-1.

### R3-Specific-2 — Methodological depth: arbiter tools? why not single agent?

> "Please clarify if the Arbiter Agent has access to any objective verification tools. If the Arbiter is simply another LLM instance, please provide a justification for why this architectural separation is superior to a single-agent system with optimized system prompts, specifically regarding the 'Epistemic' source of truth."

- **Classification:** real
- **Status:** open
- **Plan:** (a) State explicitly in §3 that the arbiter has no external tools in this study; this is by design — we are isolating the architectural variable from the tool variable. (b) Refer to the ablation as the empirical answer to "why not optimize the prompt." (c) Promise tool-augmented arbiter as future work (already in §7.5; pull it forward).
- **Cross-refs:** R2-Major-3a, R3-Major-1

### R3-Specific-3 — Distinguish from process supervision / self-correction

> "While the 'inverted pyramid' approach is visible, the literature review in Section 1 and 2 should more clearly distinguish this work from 'Process Supervision' and 'Self-Correction' frameworks recently proposed by major AI labs."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-5(a) and R2-Major-2.

### R3-Specific-4 — Keyword "Constitutional AI" not integrated

> "The keyword 'Constitutional AI' is listed but not sufficiently integrated or explained within the abstract or the core methodological summary."

- **Classification:** disputed — "Constitutional AI" is **not** in the current keyword list. The keyword set is: Sycophancy, Multi-agent systems, Epistemic fortitude, Large language models, Conversational AI, Alignment, Fact verification.
- **Status:** open
- **Plan:** In response letter, politely clarify that Constitutional AI is not among the listed keywords; CAI is referenced in §2.5 as related work, and the response describes how our architecture *extends* CAI principles (separating epistemic principles into a dedicated agent). No keyword change is needed.

### R3-Specific-5 — Truth vs. Empathy; dynamic fortitude as future direction

> "The manuscript currently treats sycophancy solely as a technical failure to be eliminated. However, from a human-computer interaction (HCI) and psychological perspective, 'sycophancy' often overlaps with 'empathetic validation'—a crucial element in building rapport during sensitive or supportive dialogues. Required Revision: The authors must add a dedicated subsection in the Discussion or Limitations chapter to address the domain-specific nature of 'Epistemic Fortitude.' Specific Focus: Please discuss scenarios where rigid adherence to technical truth might be counterproductive (e.g., in emotional support or subjective social contexts). Future Direction: The authors should propose how their Arbiter mechanism could be evolved into a 'Dynamic Fortitude' system that balances factual rigidity with conversational empathy depending on the user's intent (e.g., Task-oriented vs. Support-oriented)."

- **Classification:** real
- **Status:** open
- **Plan:** Covered by AE-5(b) and R2-Other-2. Will explicitly use "Dynamic Fortitude" as the future-work label.

### R3-Concluding — Concluding mandates

> "A Major Revision is required to: 1. Formally disclose the use of Generative AI and perform a meticulous manual proofreading. 2. Provide a cost-benefit analysis of the O(2n) inference overhead. 3. Incorporate the aforementioned humanistic perspective regarding the trade-off between 'Truth' and 'Empathy' in diverse LLM applications. Acceptance will heavily depend on whether the authors can elevate this work from a narrow engineering solution to a sophisticated, cross-domain discussion on AI behavior and ethics."

- **Classification:** real (summary)
- **Status:** open
- **Plan:** Three top-priority items, all already covered: AE-2, AE-4, AE-5. The "narrow engineering solution → cross-domain discussion" framing is a useful guide for the truth-vs-empathy subsection: lift the conceptual ceiling without overclaiming.

---

## 5. Consolidated Issue Map

| # | Issue | Sources | Priority | Status |
|---|---|---|---|---|
| A | Cost / latency / feasibility analysis (per-model) | AE-4, R2-Major-3b, R3-Major-2 | **Highest** (rejection trigger) | **Done** — pending compile (token + latency P50/P95 columns in `tab:cost-overhead`; cost-benefit closer paragraph pairs overhead with effect sizes and Gemini sycophancy drop 45.7%→12.3%) |
| B | Judge-model justification + Krippendorff's α + human validation | AE-1, R1-Major-3, R1-Specific-5 | High | **In progress** — rater 1 (n=50) done, α=0.68; co-author second 50 pending |
| C | Architecture-vs-prompt-engineering rebuttal | R2-Major-3a, R3-Major-1, R3-Specific-2 | High | **Done** — pending compile (§RO3 augmented with ablation punch line, scaling-with-conflict closer, and external-verifier scope statement; all in `\rev{}`) |
| D | Truth vs. empathy / domain boundaries / "Dynamic Fortitude" future work | AE-5, R2-Other-2, R2-Premise, R3-Major-3, R3-Specific-5 | High | **Done** — pending compile |
| E | Differentiate from process supervision / self-correction / verifiers | AE-5, R2-Major-2, R3-Specific-3 | Medium | open |
| F | Hybrid router diagram + method flow | AE-3, R1-Major-1, R1-Specific-1 | Medium | diagram **done**; method-flow prose tighten still open |
| G | Section naming alignment + table/figure placement audit | AE-3, R1-Major-2, R1-Specific-3, R1-Specific-4, R1-Grammar | Medium | open |
| H | Per-experiment conversation-count tables co-located with results | R1-Specific-2 | Low | open |
| I | Introduction transition + lit support for dialogue-based sycophancy | R2-Major-1 | Medium | open |
| J | AI Use Disclosure statement + manual proofread | AE-2, R2-Other-1, R3-Grammar, R3-Specific-1 | Medium | open |
| K | "LaTeX artifacts" claim — respectful dispute | R2-Other-1, R3-Grammar | Medium | open |
| L | Constitutional AI keyword clarification | R3-Specific-4 | Low | open |

---

## 6. Suggested Order of Work

1. **A — Cost/latency analysis** (extract from logs, build table, write paragraph). Highest leverage; defuses R2's rejection threat.
2. **B — Judge validation** (run/finalise human-coded 50-sample agreement; write justification paragraph).
3. **C — Architecture-vs-prompt rebuttal** (decide on stubborn-prompt baseline; promote ablation in §7.3; reframe compliance-vs-grounding as a feature).
4. **D — Truth-vs-empathy subsection** (write Discussion subsection; introduce "Dynamic Fortitude" as future work).
5. **E — Process supervision / verifier differentiation** (add 2 paragraphs in §2; add comparison entry in §7.4).
6. **F — Router diagram** (TikZ).
7. **G — Section renames + table/figure placement audit**.
8. **H — Per-experiment count tables**.
9. **I — Intro transition rework + recent dialogue-sycophancy citations**.
10. **J — AI Use Disclosure + manual proofread**.
11. **K — Verify and document the "no LaTeX artifacts" finding** (so we have it ready for the response letter).
12. **L — Keyword clarification** (response-letter-only; no manuscript change).

After all manuscript edits land, write the formal `response-to-reviewers.tex` modeled on `response-to-editor.tex`, with one block per ID above and a clear cross-reference to the location of every change.
