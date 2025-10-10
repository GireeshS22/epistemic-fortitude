# Claude Context - Epistemic Fortitude

## Project Overview
**Epistemic Fortitude** is a multi-agent AI system built with Google's Agent Development Kit (ADK) that maintains principled confidence in its knowledge instead of being overly agreeable to user contradictions.

## Core Architecture

### The Problem We're Solving
AI agents often provide correct answers but then retract them when users say "that's wrong," switching to incorrect responses. This is the "sycophancy" problem.

### The Solution
A **two-agent system with LLM-based routing**:

1. **Coordinator Agent** (✅ Implemented)
   - Meta-agent that maintains control throughout conversation
   - Uses LLM-based contradiction detection (in instruction prompt)
   - Routes to appropriate sub-agent based on user input
   - Model: `gemini-2.5-flash`

2. **Primary Agent** (✅ Implemented)
   - Fast, user-facing conversational agent
   - Handles normal Q&A flow
   - Returns control to coordinator via `after_agent_callback`
   - Model: `gemini-2.5-flash`

3. **Arbiter Agent** (✅ Implemented)
   - Deep-reasoning fact-checker
   - Activated when user contradicts previous responses
   - Reviews context and adjudicates disputes
   - Either defends correct answer OR gracefully corrects
   - Returns control to coordinator via `after_agent_callback`
   - Model: `gemini-2.5-flash`

## Current Implementation Status

### ✅ Completed (Session 3 - 2025-10-11)

**Major Refactoring - ADK Clean Architecture:**
- ✅ **Restructured to follow ADK best practices** (based on blog-writer sample)
- ✅ **Removed Python orchestrator** (`orchestrator.py`, `test_orchestrator.py`)
- ✅ **Removed keyword-based triggers** (`triggers.py`) - replaced with LLM detection
- ✅ **Removed obsolete test files** (`test_agent.py`)
- ✅ **Created `sub_agents/` folder** with clean exports
- ✅ **Moved agents to sub-folder**:
  - `agent.py` → `sub_agents/primary_agent.py`
  - `arbiter.py` → `sub_agents/arbiter_agent.py`
- ✅ **New root coordinator** in `agent.py` (standard ADK Agent, not custom BaseAgent)
- ✅ **LLM-based contradiction detection** via coordinator instruction
- ✅ **after_agent_callback implementation** - "return to sender" pattern
- ✅ **Fixed ADK compatibility issues**:
  - Updated ADK version to fix telemetry bug
  - Fixed `_event_actions` (underscore required)
  - `transfer_to_agent` in callbacks

### 📁 Current Project Structure
```
epistemic_fortitude/
├── epistemic_fortitude/          # Agent package
│   ├── __init__.py              # Module exports
│   ├── agent.py                 # Root coordinator (epistemic_coordinator)
│   ├── sub_agents/              # Sub-agent folder ⭐ NEW
│   │   ├── __init__.py         # Exports primary_agent, arbiter_agent
│   │   ├── primary_agent.py    # Fast Q&A agent
│   │   └── arbiter_agent.py    # Fact-checking agent
│   ├── prompts.py               # Agent instructions
│   ├── .env                     # Config (API key, model)
│   └── .env.example             # Template
├── pyproject.toml               # Poetry dependencies
└── README.md                    # Setup & usage docs
```

### 🔑 Key Technical Details

**ADK Agent Pattern (Clean Architecture):**
```python
from google.adk import Agent
from .sub_agents import primary_agent, arbiter_agent

# Coordinator that maintains control
epistemic_coordinator = Agent(
    name="epistemic_coordinator",
    model="gemini-2.5-flash",
    instruction="""<instructions for detecting contradictions>""",
    sub_agents=[primary_agent, arbiter_agent],
)

root_agent = epistemic_coordinator
```

**After Agent Callback (Return Control):**
```python
def return_to_coordinator(callback_context):
    """Transfer control back to coordinator after answering."""
    callback_context._event_actions.transfer_to_agent = "epistemic_coordinator"
    return None  # Use agent's original response

primary_agent = Agent(
    name="primary_agent",
    ...
    after_agent_callback=return_to_coordinator,
)
```

**Running the Agent:**
- Web UI: `poetry run adk web` → `http://localhost:8000`

**Important Notes:**
- ADK requires `root_agent` variable name in `agent.py`
- `__init__.py` must import agent module: `from . import agent`
- `.env` file must be in the agent folder (not parent)
- Model names: Use `gemini-2.5-flash` (1.5 models retired in 2025)
- **Callbacks must use `_event_actions` (with underscore)**
- **after_agent_callback implements "return to sender" pattern**

### 🐛 Issues Resolved (Session 3)
1. ✅ Fixed control flow - coordinator now sees all messages via callbacks
2. ✅ Removed keyword-based triggers (replaced with LLM detection)
3. ✅ Cleaned up legacy orchestrator code
4. ✅ Fixed ADK telemetry bug with Gemini 2.5 (updated ADK version)
5. ✅ Fixed `_event_actions` attribute error in callbacks
6. ✅ Restructured to follow ADK sample patterns

### 📦 Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.9"
google-adk = "^0.1.0"  # Updated to latest version
python-dotenv = "^1.0.0"
deprecated = "^1.2.14"
```

## System Flow

### ADK Multi-Agent Architecture (Current - Session 3)
```
User Input (via ADK Web)
     ↓
root_agent = epistemic_coordinator (Standard ADK Agent)
     │
     ├─ LLM detects contradiction in instruction?
     │   ├─ No  → transfer_to_agent(primary_agent)
     │   └─ Yes → transfer_to_agent(arbiter_agent) with context
     ↓
Sub-agent executes
     ↓
after_agent_callback fires → transfer_to_agent(epistemic_coordinator)
     ↓
Coordinator regains control for next user message
     ↓
Return Response to User
```

### Key Components

**Epistemic Coordinator (agent.py)**
- Standard ADK `Agent` (not custom BaseAgent)
- Registered `sub_agents`: primary_agent, arbiter_agent
- **Instruction-based routing**: LLM decides when to invoke arbiter
- Maintains conversation control via sub-agent callbacks

**Contradiction Detection**
- **Method**: LLM-based (in coordinator's instruction)
- **Patterns**: Explicit ("wrong", "incorrect"), Implicit ("oh no", "I disagree"), Corrections ("actually it's...")
- **Advantage**: Handles nuanced disagreements that keywords miss

**Control Flow Management**
- `after_agent_callback` in both sub-agents
- Uses `_event_actions.transfer_to_agent` to return to coordinator
- Ensures coordinator sees every message (can detect contradictions throughout)

**State Management**
- ADK's native session state (via `ctx.session.state`)
- Coordinator can access conversation history if needed
- Arbiter receives full context through instruction

## Next Steps (Priority Order)

### 1. 🔄 IN PROGRESS: Validate System Behavior
- Test contradiction detection with various phrasings
- Verify arbiter is invoked appropriately
- Check that coordinator maintains control

### 2. 📋 TODO: Fine-tune Coordinator Instruction
- Improve contradiction detection examples
- Test edge cases (soft disagreements, questions vs contradictions)
- Optimize arbiter context provision

### 3. 📋 TODO: Evaluation Framework
- Create benchmark dataset of contradiction scenarios
- Measure: accuracy, consistency, appropriate defenses
- Compare against baseline (single agent without epistemic fortitude)
- A/B testing with different coordinator instructions

### 4. 📋 TODO: Production Enhancements
- Add logging/telemetry for contradiction detection
- Track metrics (arbiter invocation rate, accuracy)
- Add conversation export functionality

## Environment Variables
```bash
GOOGLE_API_KEY=<your_key>
DEFAULT_MODEL=gemini-2.5-flash
```

## Git Branch
- Working branch: `develop/epistemic`
- Main branch: `main`

## Related Research
Part of the **Consistency-Preserving Architectures** PhD research project exploring LLM architectures that maintain logical coherence across multi-turn interactions.

## Testing the System
```bash
# Run web interface (primary method)
poetry run adk web

# Test flow:
# 1. Ask: "What is the capital of France?"
# 2. Observe: Primary agent answers
# 3. Contradict: "Oh no, I think it's Lyon"
# 4. Observe: Arbiter agent fact-checks and defends correct answer
```

## Session Notes

### Session 1 (2025-10-05)
- Set up basic ADK agent structure
- Got web interface running
- Fixed model compatibility issues
- Created documentation

### Session 2 (2025-10-10)
- **Part 1: Python Orchestrator Implementation**:
  - ✅ Arbiter agent (fact-checking interventional agent)
  - ✅ Triggers module (case-insensitive contradiction detection)
  - ✅ Python orchestrator (Agent 0 - routes between agents, manages state)
  - ✅ E2E test suite
  - **Issue found**: ADK web interface bypassed Python orchestrator

- **Part 2: ADK Native Multi-Agent System**:
  - ✅ Created `CoordinatorAgent` (custom BaseAgent)
  - ✅ Used ADK's native `sub_agents` and agent invocation
  - ✅ Integrated with ADK web via `root_agent = coordinator_agent`
  - ✅ Leveraged ADK's `_run_async_impl()` for custom routing logic

- **Architecture**: ADK-native multi-agent with custom routing
- **Key decisions**:
  - No confidence scores (binary contradiction detection)
  - ADK BaseAgent over Python orchestrator for web integration
  - Kept Python orchestrator for backward compatibility

### Session 3 (2025-10-11)
- **Major Refactoring - Clean ADK Architecture**:
  - ✅ Restructured following ADK blog-writer sample pattern
  - ✅ Removed ALL legacy code (orchestrator, triggers, test files)
  - ✅ Created `sub_agents/` folder structure
  - ✅ Switched from keyword triggers to LLM-based contradiction detection
  - ✅ Implemented `after_agent_callback` for control flow
  - ✅ Fixed ADK compatibility issues (telemetry, _event_actions)

- **Architecture**: Standard ADK multi-agent with LLM-based routing
- **Key decisions**:
  - Standard ADK `Agent` (not custom BaseAgent) for coordinator
  - LLM detects contradictions (more flexible than keywords)
  - `after_agent_callback` implements "return to sender" pattern
  - Clean separation: coordinator in root, sub-agents in folder

- **Blockers Resolved**:
  - ADK telemetry bug → Updated ADK version
  - Control flow issue → Added callbacks to return to coordinator
  - API compatibility → Used `_event_actions` (underscore)

- **Current Status**: System restructured, ready for end-to-end testing
- **Next**: Validate contradiction detection and arbiter invocation in live tests

---

*Last updated: 2025-10-11*
*Update this file at the end of each session with progress and blockers*
