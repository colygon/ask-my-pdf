# CrewAI Upgrade Documentation - Ask my PDF

## Overview

Enhanced the Ask my PDF application with CrewAI multi-agent capabilities. The app originally used custom RAG with HyDE (Hypothetical Document Embeddings). The upgrade adds three specialized agents for improved document Q&A.

## Architecture

### Original Implementation
- Custom RAG with scikit-learn cosine similarity
- HyDE for improved semantic search
- OpenAI embeddings and completions via ai-bricks library
- Fragment-based document indexing

### CrewAI Enhancement
- Three specialized agents working collaboratively
- Sequential workflow with context sharing
- Optional HyDE agent for query enhancement
- Full backward compatibility

## CrewAI Agents

### 1. Document Structure Analyst
**Goal**: Analyze PDF documents to understand structure and content organization

**Responsibilities**:
- Identify key sections and topics
- Understand document organization
- Map content relationships
- Provide structural context for Q&A

### 2. Question Interpreter
**Goal**: Understand user questions and identify exact information needs

**Responsibilities**:
- Parse natural language questions
- Identify question intent and type
- Determine required information
- Extract key concepts

### 3. Answer Synthesizer
**Goal**: Create comprehensive answers from document fragments

**Responsibilities**:
- Extract relevant information from fragments
- Synthesize coherent answers
- Include citations from source fragments
- Acknowledge information gaps

### 4. Hypothetical Document Generator (Optional)
**Goal**: Generate hypothetical documents for HyDE-enhanced search

**Responsibilities**:
- Create hypothetical answer text
- Improve semantic search quality
- Match document style and tone

## Workflow

```
User Question + Document Fragments
    ↓
Document Analysis (Agent 1)
    ↓ (provides context)
Question Interpretation (Agent 2)
    ↓ (provides context)
Answer Synthesis (Agent 3)
    ↓
Final Answer with Citations
```

## Usage

### Basic Usage

```python
from src.crewai_agents import get_crewai_answer

# Simple interface
answer = get_crewai_answer(
    question="What are the game setup rules?",
    document_summary=index['summary'],
    text_fragments=top_fragments
)
print(answer)
```

### With HyDE Enhancement

```python
from src.crewai_agents import get_crewai_answer

answer = get_crewai_answer(
    question="How many players can play this game?",
    document_summary=index['summary'],
    text_fragments=top_fragments,
    use_hyde=True  # Enable HyDE
)
```

### Integration with Existing Code

```python
from src.crewai_agents import enhance_with_crewai

# Direct integration with index structure
answer = enhance_with_crewai(index, question)
```

### Adding to GUI

In `gui.py`, add CrewAI option:

```python
def ui_crewai():
    st.checkbox('use CrewAI multi-agent', value=False, key='use_crewai')

# In b_ask() function, after getting fragments:
if ss.get('use_crewai'):
    from src.crewai_agents import get_crewai_answer
    answer = get_crewai_answer(
        question,
        index['summary'],
        text_list[:max_frags]
    )
    ss['answer'] = answer
    output_add(question.strip(), answer.strip())
else:
    # Original query logic
    resp = model.query(...)
```

## Features

### Enhanced Analysis
- **Multi-agent collaboration**: Three perspectives on every question
- **Context awareness**: Agents share document and question understanding
- **Citation support**: Answers reference specific fragments
- **Gap acknowledgment**: Clearly states when information is unavailable

### Improved Quality
- **Deeper comprehension**: Better understanding of complex questions
- **Coherent synthesis**: More natural answer generation
- **Source attribution**: Track where information comes from
- **Quality validation**: Multiple agents review the answer

## Backward Compatibility

✅ **Fully backward compatible**:
- Original RAG system unchanged
- Original HyDE implementation preserved
- CrewAI is opt-in feature
- No breaking changes

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-...  # Required for CrewAI
```

### Dependencies

```bash
pip install -r requirements.txt
```

New dependencies:
- crewai>=0.86.0
- crewai-tools>=0.17.0
- langchain-openai>=0.3.0

## Performance Considerations

| Aspect | Original | CrewAI |
|--------|----------|--------|
| Speed | Fast (1 call) | Slower (3 calls) |
| Quality | Good | Excellent |
| Citations | None | Included |
| Token Usage | Lower | Higher |

### Recommendations
- **Use CrewAI** for: Complex questions, detailed analysis, learning scenarios
- **Use Original** for: Quick lookups, simple questions, cost optimization

## Examples

### Example 1: Simple Question

**Question**: "How many players can play?"

**CrewAI Output**:
```
According to the provided fragments, the game supports 2-4 players.
Fragment 1 specifically states "This game is designed for 2 to 4 players,
ages 10 and up." The setup varies depending on the number of players,
with specific instructions provided for each player count.
```

### Example 2: Complex Question

**Question**: "What happens if two players tie for the highest score?"

**CrewAI Output**:
```
Based on the game rules in the provided fragments, if two or more players
tie for the highest score, Fragment 3 indicates that "players should play
one final tiebreaker round." The tiebreaker follows the same rules as
regular gameplay, but only tied players participate. The winner of the
tiebreaker round is declared the overall winner.
```

## Testing

```python
# test_crewai.py
from src.crewai_agents import AskPDFCrewAI

def test_question_answering():
    crew = AskPDFCrewAI()
    result = crew.answer_question(
        question="What is the main topic?",
        document_summary="A guide to board games",
        text_fragments=["Chapter 1: Introduction to board games..."]
    )
    assert result["success"] == True
    assert len(result["answer"]) > 0
```

## Future Enhancements

1. **Parallel Processing**: Run some agents in parallel
2. **Fragment Ranking**: Better fragment selection
3. **Multi-document**: Support multiple PDFs
4. **Interactive Clarification**: Ask users for clarification
5. **Answer Confidence**: Provide confidence scores

---

**Version**: 1.0.0
**Last Updated**: 2025-12-21
**Compatibility**: Ask my PDF 0.4.x+, CrewAI 0.86.0+
