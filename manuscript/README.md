# Epistemic Fortitude Paper

**Title**: Architecting Epistemic Fortitude: A Hierarchical Multi-Agent Framework for Mitigating Sycophancy in Conversational AI

**Target Venue**: ACM TOSEM Special Issue on Agentic AI Software

## Paper Structure

This paper is organized using modular LaTeX sections for easy editing and collaboration:

```
manuscripts/epistemic-fortitude/
├── main-article.tex           # Main LaTeX file (compile this)
├── acmart.cls                 # ACM article class
├── ACM-Reference-Format.bst   # Bibliography style
├── acmart.bib                 # Bibliography database
├── README.md                  # This file
├── sections/                  # Modular paper sections
│   ├── 01-abstract.tex
│   ├── 02-introduction.tex
│   ├── 03-related-work.tex
│   ├── 04-framework.tex
│   ├── 05-experimental-setup.tex
│   ├── 06-results.tex
│   ├── 07-discussion.tex
│   └── 08-conclusion.tex
├── images/                    # Figures and diagrams
└── guidelines/                # Venue guidelines
    └── ACM-TOSEM-CfP-Agentic-AI-Software.pdf
```

## How to Compile

### Using LaTeX (Recommended)

1. Install a LaTeX distribution:
   - **Windows**: MiKTeX or TeX Live
   - **Mac**: MacTeX
   - **Linux**: TeX Live

2. Compile with BibTeX:
   ```bash
   pdflatex main-article.tex
   bibtex main-article
   pdflatex main-article.tex
   pdflatex main-article.tex
   ```

3. Or use latexmk (automated):
   ```bash
   latexmk -pdf main-article.tex
   ```

### Using Overleaf

1. Create new project in Overleaf
2. Upload all files maintaining folder structure
3. Set main document to `main-article.tex`
4. Compile automatically

## Current Status

### Completed ✅
- [x] Main document structure with ACM template
- [x] All 8 section files with comprehensive outlines
- [x] Abstract (200 words, needs results filled in)
- [x] Introduction with 4 subsections
- [x] Related Work with 4 subsections
- [x] Framework with 5 subsections (architecture, agents, routing)
- [x] Experimental Setup with 6 subsections
- [x] Results with 6 subsections (placeholders for actual numbers)
- [x] Discussion with 6 subsections
- [x] Conclusion
- [x] Bibliography with 25+ key citations

### To Do 📋
- [ ] Fill in actual experimental results (marked with `[XX]`, `[XX%]`, `[X.XX]`)
- [ ] Create figures:
  - [ ] `images/architecture-diagram.pdf` - System architecture
  - [ ] `images/score-degradation-baseline.pdf` - Baseline score maintenance
  - [ ] `images/score-comparison.pdf` - Baseline vs Fortitude comparison
  - [ ] `images/routing-distribution.pdf` - Routing mechanism breakdown
- [ ] Update author information in `main-article.tex`
- [ ] Replace placeholder citations (marked with "Placeholder:" in bibliography)
- [ ] Add actual GitHub repository URL (currently `[ANONYMOUS]`)
- [ ] Proofread and polish all sections
- [ ] Ensure consistency in terminology throughout

## Sections Overview

### 1. Introduction (4 subsections)
- **1.1**: The Sycophancy Problem - Defines the failure mode with concrete examples
- **1.2**: Epistemic Fortitude - Introduces the core concept
- **1.3**: Primary-Arbiter Architecture - Presents our solution
- **1.4**: Contributions - Lists 6 key contributions

### 2. Related Work (4 subsections)
- **2.1**: Sycophancy measurement and mitigation literature
- **2.2**: Self-correction limitations (answer wavering)
- **2.3**: Multi-agent systems (consensus vs correctness)
- **2.4**: Constitutional AI and RLAIF

### 3. Framework (5 subsections)
- **3.1**: System architecture overview
- **3.2**: Primary Agent design
- **3.3**: Arbiter Agent with epistemic constitution
- **3.4**: Hybrid routing (Algorithm 1, Tier 1-3)
- **3.5**: LangGraph implementation

### 4. Experimental Setup (6 subsections)
- **4.1**: HealthBench dataset and sampling
- **4.2**: Contradiction injection methodology (16 prompts, 4 tiers)
- **4.3**: A/B testing conditions (baseline vs fortitude)
- **4.4**: Evaluation metrics (sycophancy rate, score maintenance)
- **4.5**: LLM-as-judge scoring protocol
- **4.6**: Statistical analysis methods

### 5. Results (6 subsections)
- **5.1**: Baseline sycophancy quantification
- **5.2**: Main result - sycophancy reduction with Arbiter
- **5.3**: Arbiter intervention analysis with examples
- **5.4**: Routing accuracy by tier
- **5.5**: Computational cost comparison
- **5.6**: Ablation studies (router, instruction variants, ADK vs LangGraph)

### 6. Discussion (6 subsections)
- **6.1**: Rethinking alignment (agreeableness vs truthfulness)
- **6.2**: Solving feedback friction and answer wavering
- **6.3**: Critical role of routing reliability
- **6.4**: Constitutional AI in multi-agent systems
- **6.5**: Conversational quality and user experience
- **6.6**: Limitations and future work

### 7. Conclusion
- Summary of contributions
- Broader implications for architectural alignment
- Future research directions

## Filling in Results

When you have experimental results, search for these patterns and replace:

- `[XX%]` - Percentage values (sycophancy rates, accuracy, etc.)
- `[XX]` - Count values (number of cases, interventions, etc.)
- `[X.XX]` - Decimal values (score maintenance ratios, effect sizes)
- `[XXXX]` - Large numbers (latency in milliseconds, token counts)
- `[BASELINE]` and `[RESULT]` - Specific metric comparisons

## Key Arguments

The paper makes several interconnected arguments:

1. **The Problem**: RLHF creates sycophancy - models prioritize agreeableness over truthfulness
2. **Why Single Agents Fail**: Answer wavering, feedback friction, conflicting objectives
3. **The Solution**: Architectural separation - Primary for conversation, Arbiter for epistemic oversight
4. **Critical Insight**: Pure LLM routing fails (44%), hybrid achieves 2x improvement (87%)
5. **Broader Vision**: Architectural alignment as paradigm - specialize agents for objectives

## Citation Style

Using ACM Reference Format with `\cite{}` commands. Key citation labels:

- Sycophancy: `\cite{perez2022discovering,sharma2023towards}`
- RLHF: `\cite{ouyang2022training}`
- Self-correction: `\cite{madaan2023self,huang2023large}`
- Multi-agent: `\cite{du2023improving,liang2023encouraging}`
- Constitutional AI: `\cite{bai2022constitutional,lee2023rlaif}`
- Frameworks: `\cite{langgraph,adk}`
- Evaluation: `\cite{zheng2023judging,healthbench}`

## Contact

For questions or collaboration, please contact [YOUR EMAIL].

---

**Last Updated**: 2025-10-18
**Status**: Draft - awaiting experimental results
