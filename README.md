# Epistemic Fortitude

**A Multi-Agent AI System with Principled Knowledge Confidence**

## Core Concept

Epistemic Fortitude is a conversational AI system designed to maintain confidence and consistency in its knowledge, rather than being overly agreeable or easily swayed by user contradictions.

### The Problem

Current AI agents often exhibit a failure mode where they:
1. Provide a correct answer
2. Immediately retract or change it when a user says "No, that's wrong"
3. Switch to an incorrect or incoherent response

This is analogous to a child who, despite doing something right, becomes confused and changes behavior due to negative feedback alone.

### The Solution

Epistemic Fortitude implements a **multi-agent architecture** with specialized roles:

#### 1. Primary Agent
- **Role**: Fast, user-facing conversationalist
- **Function**: Handles normal conversation flow
- **Optimization**: Speed and helpfulness

#### 2. Interventional Agent (The Arbiter)
- **Role**: Deep-reasoning expert and fact-checker
- **Function**: Activated when user contradicts the Primary Agent
- **Process**:
  - Reviews full context (question, answer, contradiction)
  - Adjudicates the dispute through fact verification
  - Either defends the correct answer with reasoning OR issues a well-reasoned correction

### Key Capabilities

The system can:
1. **Recognize** when a user is contradicting it
2. **Critically evaluate** whether its original answer or the user's contradiction is correct
3. **Politely defend** its correct answer with supporting evidence
4. **Gracefully accept** corrections when genuinely wrong

---

## Project Structure

```
epistemic_fortitude/
├── epistemic_fortitude/          # Agent package
│   ├── __init__.py
│   ├── agent.py                  # Primary agent definition
│   ├── prompts.py                # Agent instructions/prompts
│   ├── .env                      # Your configuration (not in git)
│   └── .env.example              # Configuration template
├── pyproject.toml                # Poetry dependencies
└── README.md                     # This file
```

## Setup

### Prerequisites
- Python 3.9+
- Poetry (package manager)
- Google AI Studio API key

### Installation

1. **Clone the repository** (if not already done)

2. **Install dependencies:**
   ```bash
   cd epistemic_fortitude
   poetry install
   ```

3. **Configure environment:**
   ```bash
   cd epistemic_fortitude
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

4. **Get API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create an API key
   - Add it to `.env` file

## Running the Agent

### Web Interface (Recommended)

```bash
poetry run adk web
```

Then open `http://localhost:8000` in your browser.

### Python Script

```bash
python test_agent.py
```

## Configuration

Edit `epistemic_fortitude/.env`:

```bash
# Model selection
DEFAULT_MODEL=gemini-2.5-flash

# Available models:
# - gemini-2.5-flash (recommended)
# - gemini-2.0-flash
# - gemini-2.5-flash-lite
```

## Current Status

### ✅ Implemented
- Basic project structure with Google ADK
- Primary agent with configurable prompts
- Web interface support via ADK
- Environment-based configuration

### 🚧 In Progress
- Interventional agent (Arbiter)
- Contradiction detection system
- Multi-agent orchestration

### 📋 Planned
- Trigger detection for user contradictions
- Fact verification integration
- Memory system for tracking agent claims
- Evaluation framework

---

*Part of the Consistency-Preserving Architectures research project*
