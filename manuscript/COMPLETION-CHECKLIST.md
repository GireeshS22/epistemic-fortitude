# Paper Completion Checklist

## Phase 1: Fill in Experimental Results ⏳

### Abstract (01-abstract.tex)
- [ ] Line 19: Replace `[BASELINE]%` with actual baseline sycophancy rate
- [ ] Line 19: Replace `[RESULT]%` with fortitude sycophancy rate

### Results Section (06-results.tex)

#### Table 1: Baseline Sycophancy (Line 12-25)
- [ ] Fill in `[XX]` counts for each tier (T1-T4)
- [ ] Calculate sycophancy percentages
- [ ] Add overall totals

#### Figure 1: Score Degradation (Line 29)
- [ ] Calculate median score maintenance ratio
- [ ] Create scatter plot visualization
- [ ] Export as PDF to `images/score-degradation-baseline.pdf`

#### Table 3: Fortitude Comparison (Line 48-59)
- [ ] Baseline sycophancy rate
- [ ] Fortitude sycophancy rate
- [ ] Calculate absolute and relative reductions
- [ ] Baseline and Fortitude score maintenance ratios

#### Statistical Tests (Line 67-69)
- [ ] Run paired t-test, fill in t-statistic, df, p-value
- [ ] Calculate Cohen's d effect size
- [ ] Run chi-square test, fill in χ² and p-value

#### Figure 2: Score Comparison (Line 73)
- [ ] Create side-by-side distribution plot
- [ ] Export as PDF to `images/score-comparison.pdf`

#### Table 4: Arbiter Interventions (Line 82-92)
- [ ] Count: Defended correct answers
- [ ] Count: Acknowledged valid corrections
- [ ] Count: Partially defended with caveats
- [ ] Count: Routing misses

#### Table 6: Routing Accuracy (Line 136-149)
- [ ] Fill in accuracy for each tier (1-4)
- [ ] Calculate overall hybrid accuracy
- [ ] Verify 2x improvement over 44% baseline

#### Figure 3: Routing Distribution (Line 153)
- [ ] Create pie/bar chart of routing mechanisms
- [ ] Show keyword vs LLM fallback distribution
- [ ] Export as PDF to `images/routing-distribution.pdf`

#### Table 7: Computational Cost (Line 165-178)
- [ ] Mean tokens/turn (baseline vs fortitude)
- [ ] Mean latency in ms (baseline vs fortitude)
- [ ] Total API cost in $ (baseline vs fortitude)
- [ ] Calculate overhead percentage

#### Table 8: Router Ablation (Line 188-197)
- [ ] Pure LLM (ADK): Confirmed 44% accuracy
- [ ] Hybrid (LangGraph): Fill in accuracy
- [ ] Calculate improvement

#### Table 9: Keyword-Only Ablation (Line 203-212)
- [ ] Tier 1-2 accuracy (keyword only)
- [ ] Tier 3-4 accuracy (keyword only)
- [ ] Overall accuracy

#### Table 10: Instruction Ablation (Line 224-234)
- [ ] Minimal instruction results
- [ ] Constitutional instruction results (ours)
- [ ] Adversarial instruction results
- [ ] Tone scores for each

#### Table 11: Framework Comparison (Line 242-253)
- [ ] Confirm ADK: 44% router accuracy
- [ ] Fill in LangGraph metrics across all columns
- [ ] Calculate improvements

### Throughout All Sections
Search and replace ALL instances of:
- [ ] `[XX%]` with actual percentages
- [ ] `[XX]` with actual counts
- [ ] `[X.XX]` with actual decimal values
- [ ] `[XXXX]` with actual large numbers (latency, tokens)

## Phase 2: Create Figures 📊

### Figure 1: Architecture Diagram
- [ ] Design system architecture showing:
  - Primary Agent
  - Arbiter Agent
  - Hybrid Router (3 tiers)
  - State flow
- [ ] Create in draw.io, PowerPoint, or LaTeX TikZ
- [ ] Export as PDF: `images/architecture-diagram.pdf`
- [ ] Update caption if needed in `04-framework.tex` line 14

### Figure 2: Score Degradation (Baseline)
- [ ] Scatter plot: Turn 1 score vs Turn 3 score
- [ ] Add diagonal line (y=x) for reference
- [ ] Highlight median ratio
- [ ] Export as: `images/score-degradation-baseline.pdf`

### Figure 3: Score Comparison
- [ ] Side-by-side violin/box plots
- [ ] Baseline vs Fortitude score maintenance distributions
- [ ] Show medians, quartiles
- [ ] Export as: `images/score-comparison.pdf`

### Figure 4: Routing Distribution
- [ ] Pie chart or stacked bar chart
- [ ] Show: keyword_strong, keyword_soft, llm_detection, normal_qa
- [ ] Percentages labeled
- [ ] Export as: `images/routing-distribution.pdf`

## Phase 3: Complete Metadata 📝

### Main Article (main-article.tex)
- [ ] Line 31-38: Fill in author name, email, institution
- [ ] Line 76-79: Update acknowledgments (funding, collaborators)
- [ ] Line 82: Verify bibliography file name matches `acmart.bib`

### Bibliography (acmart.bib)
- [ ] Replace placeholder citations (lines 262-285):
  - `medical-sycophancy-cite`
  - `educational-sycophancy-cite`
  - `prompt-eng-cite`
  - `robust-ft-cite`
  - `reward-mod-cite`
- [ ] Search for relevant papers on Google Scholar
- [ ] Add proper BibTeX entries

### Throughout Paper
- [ ] Search for `[ANONYMOUS]` - replace with actual GitHub username
- [ ] Search for `TODO` comments - address all
- [ ] Verify all `\cite{}` commands have matching entries in .bib

## Phase 4: Proofread & Polish ✍️

### Language and Style
- [ ] Read through abstract - ensure 150-250 words, no jargon
- [ ] Introduction: Check flow from problem → solution → contributions
- [ ] Related work: Verify all claims are cited
- [ ] Framework: Ensure technical details are clear
- [ ] Experiments: Check that methodology is reproducible
- [ ] Results: Verify tables/figures referenced correctly
- [ ] Discussion: Ensure claims are supported by results
- [ ] Conclusion: Strong closing statement

### Consistency Checks
- [ ] Terminology: "Primary Agent" vs "primary_agent" (consistent capitalization)
- [ ] "Epistemic Fortitude" capitalized throughout
- [ ] Model names: "gemini-2.5-flash" in code, "Gemini 2.5 Flash" in prose
- [ ] Citations: [Author et al. YEAR] format consistent
- [ ] Section references: Use `\ref{sec:X}` not hardcoded numbers

### LaTeX Compilation
- [ ] Compile with `pdflatex main-article.tex`
- [ ] Run `bibtex main-article`
- [ ] Compile twice more with `pdflatex`
- [ ] Check for warnings/errors in .log file
- [ ] Verify all citations appear in bibliography
- [ ] Check that all figures render correctly

## Phase 5: Final Review 🔍

### ACM Formatting
- [ ] Verify paper follows ACM format guidelines
- [ ] Check CCS concepts are appropriate
- [ ] Keywords list (7-8 keywords)
- [ ] Copyright notice correct
- [ ] Double-check author info formatting

### Content Quality
- [ ] Abstract: Compelling summary that sells the paper
- [ ] Introduction: Clear problem statement and motivation
- [ ] Contributions: Specific, measurable, and supported by results
- [ ] Related work: Comprehensive coverage, clear positioning
- [ ] Methodology: Reproducible, well-justified choices
- [ ] Results: Clear presentation, appropriate statistics
- [ ] Discussion: Insightful interpretation, honest limitations
- [ ] Conclusion: Strong impact statement

### Technical Accuracy
- [ ] All algorithms formatted correctly
- [ ] All tables have proper captions
- [ ] All figures have descriptive captions
- [ ] All equations numbered and referenced
- [ ] Code snippets readable and correct
- [ ] Statistical tests appropriate for data

### Pre-Submission
- [ ] Run spell check
- [ ] Check for orphan lines (single lines at top of page)
- [ ] Verify page count meets venue requirements
- [ ] Create supplementary materials (code, data) if needed
- [ ] Write cover letter for submission
- [ ] Get co-author approval
- [ ] Upload to submission system

## Quick Commands

### Compile Paper
```bash
cd manuscripts/epistemic-fortitude
pdflatex main-article.tex && bibtex main-article && pdflatex main-article.tex && pdflatex main-article.tex
```

### Count Words (approximate)
```bash
texcount main-article.tex
```

### Find All Placeholders
```bash
grep -r "\[XX" sections/
grep -r "\[BASELINE\]" sections/
grep -r "TODO" sections/
```

### Check Citations
```bash
grep -o "\\cite{[^}]*}" sections/*.tex | sort | uniq
```

---

**Pro Tip**: Work through this checklist in order. Phase 1 (results) is critical - complete it before moving to figures. Phase 2 (figures) takes time - start early. Phases 3-5 are iterative - multiple passes recommended.

**Estimated Time**:
- Phase 1: 4-6 hours (data analysis + filling tables)
- Phase 2: 6-8 hours (figure creation)
- Phase 3: 2-3 hours (metadata completion)
- Phase 4: 4-6 hours (proofreading)
- Phase 5: 2-4 hours (final polish)

**Total**: ~20-30 hours of focused work

Good luck! 🚀
