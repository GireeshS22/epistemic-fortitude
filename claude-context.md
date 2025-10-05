# Claude Context - Epistemic Fortitude

## Project Overview
**Epistemic Fortitude** is a multi-agent AI system built with Google's Agent Development Kit (ADK) that maintains principled confidence in its knowledge instead of being overly agreeable to user contradictions.

## Core Architecture

### The Problem We're Solving
AI agents often provide correct answers but then retract them when users say "that's wrong," switching to incorrect responses. This is the "sycophancy" problem.

### The Solution
A **two-agent system**:

1. **Primary Agent** (✅ Implemented)
   - Fast, user-facing conversational agent
   - Handles normal Q&A flow
   - Model: `gemini-2.5-flash`

2. **Interventional Agent / Arbiter** (📋 Planned)
   - Deep-reasoning fact-checker
   - Activated when user contradicts Primary Agent
   - Reviews context and adjudicates disputes
   - Either defends correct answer OR gracefully corrects

## Current Implementation Status

### ✅ Completed (Session 1)
- Project structure setup on branch `develop/epistemic`
- Poetry-based dependency management
- Google ADK integration
- Primary agent with custom prompts
- ADK web interface working at `http://localhost:8000`
- Environment configuration with `.env` files

### 📁 Project Structure
```
epistemic_fortitude/
├── epistemic_fortitude/          # Agent package
│   ├── __init__.py              # Imports agent module
│   ├── agent.py                 # Primary agent (root_agent)
│   ├── prompts.py               # Agent instructions
│   ├── .env                     # Config (API key, model)
│   └── .env.example             # Template
├── pyproject.toml               # Poetry dependencies
├── test_agent.py                # CLI test script
└── README.md                    # Setup & usage docs
```

### 🔑 Key Technical Details

**ADK Agent Pattern:**
```python
from google.adk import Agent

root_agent = Agent(
    name="primary_agent",
    model="gemini-2.5-flash",
    instruction="..." # singular, not plural
)
```

**Running the Agent:**
- Web UI: `poetry run adk web` → `http://localhost:8000`
- CLI: `python test_agent.py`

**Important Notes:**
- ADK requires `root_agent` variable name in `agent.py`
- `__init__.py` must import agent module: `from . import agent`
- `.env` file must be in the agent folder (not parent)
- Model names: Use `gemini-2.5-flash` (1.5 models retired in 2025)
- `instruction` is singular, no `temperature` parameter in Agent()

### 🐛 Issues Resolved
1. ✅ Fixed Pydantic validation errors (instructions → instruction)
2. ✅ Added missing `deprecated` dependency
3. ✅ Updated deprecated model name (1.5-flash → 2.5-flash)
4. ✅ Fixed package path in pyproject.toml

### 📦 Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.9"
google-adk = "^0.1.0"
python-dotenv = "^1.0.0"
deprecated = "^1.2.14"
```

## Next Steps (Priority Order)

### 1. Implement Interventional Agent (Arbiter)
- Create separate agent with critical reasoning prompt
- Use same ADK Agent pattern but with lower temperature concept
- Store in `epistemic_fortitude/arbiter.py`

### 2. Build Contradiction Detection
- Implement trigger system to detect user contradictions
- Keyword-based or ML-based classifier
- Module: `epistemic_fortitude/triggers.py`

### 3. Orchestration Logic
- Build conversation manager to route between agents
- Decide when to invoke Arbiter vs Primary
- Module: `epistemic_fortitude/orchestrator.py`

### 4. Memory System
- Track agent claims/assertions
- Store conversation history for context
- Enable Arbiter to review full dispute context

### 5. Evaluation Framework
- Create test cases for contradiction scenarios
- Measure: accuracy, consistency, appropriate defenses
- Benchmark against baseline (single agent)

## Environment Variables
```bash
GOOGLE_API_KEY=<your_key>
DEFAULT_MODEL=gemini-2.5-flash
PRIMARY_AGENT_TEMPERATURE=0.7      # Note: not used in Agent() yet
INTERVENTIONAL_AGENT_TEMPERATURE=0.3
```

## Git Branch
- Working branch: `develop/epistemic`
- Main branch: `main`

## Related Research
Part of the **Consistency-Preserving Architectures** PhD research project exploring LLM architectures that maintain logical coherence across multi-turn interactions.

## Session Notes

### Session 1 (2025-10-05)
- Set up basic ADK agent structure
- Got web interface running
- Fixed model compatibility issues
- Created documentation

---

*Last updated: 2025-10-05*
*Update this file at the end of each session with progress and blockers*
