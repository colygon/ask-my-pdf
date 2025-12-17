# Quick Start Guide - Agent 58 CrewAI Upgrade

## Installation (30 seconds)

```bash
cd /Users/colinlowenberg/crew/askmypdf-agent58
pip install -r requirements.txt
```

## Set API Key (10 seconds)

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Run Application (5 seconds)

```bash
cd src
streamlit run gui.py
```

## Enable CrewAI (3 clicks)

1. Open "advanced" section in sidebar
2. Check "use CrewAI agents" checkbox
3. Ask your question!

## The Three Agents

1. **PDF Analyzer** - Understands document structure
2. **Context Researcher** - Finds relevant information
3. **Answer Synthesizer** - Creates comprehensive answer

## Branch Ready to Push

```bash
# Current branch: crewai-upgrade
# Status: All changes committed
# Ready to push to your fork

git push -u origin crewai-upgrade
```

## Files Changed

- ✅ `src/crew_agents.py` (NEW) - Agent implementations
- ✅ `src/model.py` (MODIFIED) - Integration logic
- ✅ `src/gui.py` (MODIFIED) - UI controls
- ✅ `requirements.txt` (MODIFIED) - Dependencies
- ✅ `CREWAI_UPGRADE.md` (NEW) - Full documentation

## Test It Out

1. Upload a PDF (or use existing)
2. Enable CrewAI checkbox
3. Ask: "What is this document about?"
4. Watch three agents collaborate!

## Need Help?

See `CREWAI_UPGRADE.md` for detailed documentation.

---

**Agent 58** - Multi-Agent PDF Intelligence
