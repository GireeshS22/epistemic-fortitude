# Epistemic Fortitude: Architectural Specialization for Sycophancy Mitigation

**Published in Information Processing and Management (Elsevier)**

---

## Abstract

Large language models (LLMs) aligned through Reinforcement Learning from Human Feedback (RLHF) suffer from *sycophancy* — the tendency to abandon factually correct answers when users provide incorrect contradictions. In software engineering, where technical correctness is both verifiable and consequential, this failure mode can propagate bugs, mislead developers, and erode trust in AI-assisted workflows.

We introduce **Epistemic Fortitude**, a multi-agent architecture designed to maintain adherence to verified technical knowledge under user contradiction, while preserving the flexibility to accept valid corrections. Our framework separates epistemic responsibility across a Primary Agent for conversational fluency and an Arbiter Agent that intervenes when contradictions are detected, defending correct positions through evidence-based reasoning.

We evaluate on 300 software engineering conversations derived from SWE-bench Lite, with systematic adversarial contradiction injection, across four model families: Gemini 2.5 Flash, GPT-5.1, Claude Sonnet 4.5, and Llama 3.3 70B (2,400 total conversations). The arbiter architecture produces statistically significant improvements across all four models (p < 0.001), with effect sizes ranging from d = 0.40 (Llama) to d = 1.79 (GPT-5.1). An ablation study shows that architectural separation accounts for 49–77% of the improvement beyond what prompt content alone provides.

---

## Citation

```bibtex
@article{epistemic-fortitude-2026,
  title   = {Epistemic Fortitude: Architectural Specialization for Sycophancy Mitigation},
  journal = {Information Processing and Management},
  year    = {2026},
  publisher = {Elsevier}
}
```

---

## Repository Structure

```
epistemic-fortitude/
├── epistemic_fortitude/       # Core agent package
│   ├── langgraph_agent.py     # Main entry point
│   ├── langgraph/             # LangGraph multi-agent implementation
│   │   ├── state.py           # EpistemicState schema
│   │   ├── nodes.py           # Primary and Arbiter agent nodes
│   │   ├── routing.py         # Hybrid contradiction router
│   │   └── graph.py           # StateGraph construction
│   └── prompts.py             # Agent system prompts
├── manuscript/                # Paper source (LaTeX) and figures
│   ├── main-article-ipm.tex   # Main manuscript
│   ├── main-article-ipm.pdf   # Compiled PDF
│   ├── sections/              # Individual section files
│   └── images/                # All figures
├── data/                      # Experiment datasets
│   └── swebench/              # SWE-bench Lite evaluation data
├── scripts/                   # Experiment runners and analysis
├── streamlit/                 # Human evaluation annotation app
├── logs/                      # Experiment logs and outputs
└── pyproject.toml             # Python dependencies (Poetry)
```

---

## Setup

### Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/)
- API key for at least one supported model provider (Google, OpenAI, Anthropic)

### Installation

```bash
git clone https://github.com/GireeshS22/epistemic-fortitude.git
cd epistemic-fortitude
poetry install
```

### Configuration

```bash
cp epistemic_fortitude/.env.example epistemic_fortitude/.env
# Add your API keys to .env
```

---

## Running Experiments

```bash
# Run with Arbiter enabled (Epistemic Fortitude)
ENABLE_ARBITER=true poetry run python scripts/run_swebench_langgraph.py --num-examples 100

# Run baseline (no Arbiter)
ENABLE_ARBITER=false poetry run python scripts/run_swebench_langgraph.py --num-examples 100

# Analyze routing decisions
poetry run python scripts/analyze_contradiction_routing.py
```

---

## Architecture

```
User Message
    ↓
[Hybrid Router]
    ├─ Tier 1: Strong keyword detection  (deterministic)
    ├─ Tier 2: Soft keyword detection    (deterministic)
    └─ Tier 3: LLM fallback             (flexible)
    ↓
[Primary Agent]     — conversational fluency
[Arbiter Agent]     — fact verification and position defense
    ↓
Response + Routing Metadata
```

The key insight is that **architectural separation** — not prompt engineering alone — is responsible for the majority of sycophancy mitigation. The Arbiter operates with full context of the conversation and adjudicates disputes through evidence-based reasoning, either defending the correct answer or issuing a well-reasoned correction when the user is right.

---

## Human Evaluation App

An annotation interface for collecting human rater judgments is available in `streamlit/`:

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

---

## License

This code is released for research reproducibility. Please cite the paper if you use this work.
