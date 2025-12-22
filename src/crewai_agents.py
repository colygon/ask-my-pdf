"""
CrewAI Agents for Ask my PDF - Enhanced Document Q&A with Multi-Agent Collaboration

This module provides CrewAI agents to enhance the Ask my PDF application with specialized
agents for document analysis, question understanding, and answer generation.
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from typing import Dict, Any, List
import os


class AskPDFCrewAI:
    """CrewAI integration for Ask my PDF with specialized agents"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required for CrewAI")

    def create_document_analyst_agent(self) -> Agent:
        """
        Agent responsible for analyzing PDF documents and understanding their structure
        """
        return Agent(
            role="Document Structure Analyst",
            goal="Analyze PDF documents to understand their structure, content organization, and key topics",
            backstory="""You are an expert document analyst who can quickly understand
            the structure and organization of complex documents. You identify key sections,
            topics, and relationships within documents to help answer user questions effectively.""",
            verbose=True,
            allow_delegation=False,
        )

    def create_question_interpreter_agent(self) -> Agent:
        """
        Agent responsible for interpreting user questions and identifying what information is needed
        """
        return Agent(
            role="Question Interpreter",
            goal="Understand user questions deeply and identify the exact information needed to answer them",
            backstory="""You are an expert at understanding natural language questions
            and breaking them down into specific information requirements. You can identify
            the intent behind questions and determine what context is needed for accurate answers.""",
            verbose=True,
            allow_delegation=False,
        )

    def create_answer_synthesizer_agent(self) -> Agent:
        """
        Agent responsible for synthesizing answers from document context
        """
        return Agent(
            role="Answer Synthesizer",
            goal="Create comprehensive, accurate answers by synthesizing information from document fragments",
            backstory="""You are an expert at reading and comprehending technical documents.
            You can extract relevant information from multiple text fragments and synthesize
            them into clear, accurate, and comprehensive answers. You always cite your sources
            and acknowledge when information is not available in the provided context.""",
            verbose=True,
            allow_delegation=False,
        )

    def create_analysis_tasks(
        self,
        question: str,
        document_summary: str,
        text_fragments: List[str],
        document_analyst: Agent,
        question_interpreter: Agent,
        answer_synthesizer: Agent
    ) -> list[Task]:
        """Create tasks for the CrewAI workflow"""

        # Combine fragments for context
        context = "\n\n---FRAGMENT---\n\n".join(text_fragments[:5])  # Limit to top 5 fragments

        # Task 1: Document Analysis
        doc_analysis_task = Task(
            description=f"""Analyze the following document summary and fragments:

            DOCUMENT SUMMARY:
            {document_summary}

            RELEVANT FRAGMENTS:
            {context}

            Provide:
            1. Main topics covered in these fragments
            2. Document type and purpose
            3. Key information available
            4. Any relationships between fragments
            """,
            agent=document_analyst,
            expected_output="Detailed document analysis with topic identification and structure understanding"
        )

        # Task 2: Question Interpretation
        question_task = Task(
            description=f"""Analyze the user's question and the document analysis:

            USER QUESTION: "{question}"

            Based on the document analysis, determine:
            1. What specific information does the question ask for?
            2. What type of answer is expected (factual, procedural, comparative, etc.)?
            3. What key terms or concepts are relevant?
            4. Are there any implicit assumptions or context needed?
            """,
            agent=question_interpreter,
            expected_output="Detailed question analysis with information requirements",
            context=[doc_analysis_task]
        )

        # Task 3: Answer Synthesis
        answer_task = Task(
            description=f"""Synthesize a comprehensive answer to the user's question:

            USER QUESTION: "{question}"

            DOCUMENT FRAGMENTS:
            {context}

            Requirements:
            1. Provide a clear, direct answer to the question
            2. Use information only from the provided fragments
            3. If the fragments don't contain enough information, clearly state this
            4. Include relevant details and examples from the fragments
            5. Structure the answer logically
            6. Cite specific fragments when making key points (e.g., "According to Fragment 1...")

            Format your answer in a clear, readable way.
            """,
            agent=answer_synthesizer,
            expected_output="Comprehensive answer with citations from document fragments",
            context=[doc_analysis_task, question_task]
        )

        return [doc_analysis_task, question_task, answer_task]

    def answer_question(
        self,
        question: str,
        document_summary: str,
        text_fragments: List[str]
    ) -> Dict[str, Any]:
        """
        Run the complete CrewAI workflow for question answering

        Args:
            question: The user's question
            document_summary: Summary of the PDF document
            text_fragments: List of relevant text fragments from the document

        Returns:
            Dictionary containing analysis results and final answer
        """
        # Create agents
        document_analyst = self.create_document_analyst_agent()
        question_interpreter = self.create_question_interpreter_agent()
        answer_synthesizer = self.create_answer_synthesizer_agent()

        # Create tasks
        tasks = self.create_analysis_tasks(
            question,
            document_summary,
            text_fragments,
            document_analyst,
            question_interpreter,
            answer_synthesizer
        )

        # Create and run crew
        crew = Crew(
            agents=[document_analyst, question_interpreter, answer_synthesizer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        # Execute the crew
        result = crew.kickoff()

        return {
            "answer": str(result),
            "success": True,
            "question": question
        }


class HyDEEnhancedCrew(AskPDFCrewAI):
    """
    Extended CrewAI implementation with HyDE (Hypothetical Document Embeddings) support
    """

    def create_hyde_agent(self) -> Agent:
        """
        Agent responsible for generating hypothetical documents for HyDE
        """
        return Agent(
            role="Hypothetical Document Generator",
            goal="Generate hypothetical document fragments that would answer the user's question",
            backstory="""You are an expert at generating hypothetical document content
            that would contain the answer to a user's question. This helps improve
            semantic search by creating more relevant search queries.""",
            verbose=True,
            allow_delegation=False,
        )

    def create_hyde_task(self, question: str, summary: str, hyde_agent: Agent) -> Task:
        """Create HyDE generation task"""
        return Task(
            description=f"""Generate a hypothetical document fragment that would answer the question:

            QUESTION: "{question}"

            DOCUMENT CONTEXT: {summary}

            Requirements:
            1. Write as if you're extracting text from the actual document
            2. Include specific details and technical terms likely to appear in the real answer
            3. Maintain the style and tone expected from the document type
            4. Keep it concise (2-3 sentences)
            5. Focus on the key information that would answer the question

            Output only the hypothetical document fragment, nothing else.
            """,
            agent=hyde_agent,
            expected_output="Hypothetical document fragment for improved semantic search"
        )

    def generate_hyde_query(self, question: str, summary: str) -> str:
        """
        Generate a HyDE query for improved semantic search

        Args:
            question: User's question
            summary: Document summary

        Returns:
            Hypothetical document fragment
        """
        hyde_agent = self.create_hyde_agent()
        hyde_task = self.create_hyde_task(question, summary, hyde_agent)

        crew = Crew(
            agents=[hyde_agent],
            tasks=[hyde_task],
            process=Process.sequential,
            verbose=False,
        )

        result = crew.kickoff()
        return str(result)


def get_crewai_answer(
    question: str,
    document_summary: str,
    text_fragments: List[str],
    use_hyde: bool = False
) -> str:
    """
    Convenience function to get CrewAI answer for a question

    Args:
        question: User's question
        document_summary: Summary of the document
        text_fragments: Relevant text fragments from the document
        use_hyde: Whether to use HyDE enhancement

    Returns:
        Answer text
    """
    try:
        if use_hyde:
            crew_ai = HyDEEnhancedCrew()
            # Generate HyDE query first (can be used for better fragment retrieval)
            hyde_query = crew_ai.generate_hyde_query(question, document_summary)
            # Use the answer_question method for final answer
            result = crew_ai.answer_question(question, document_summary, text_fragments)
        else:
            crew_ai = AskPDFCrewAI()
            result = crew_ai.answer_question(question, document_summary, text_fragments)

        if result["success"]:
            return result["answer"]
        else:
            return "I encountered an issue answering your question. Please try again."

    except Exception as e:
        return f"Error: {str(e)}\n\nPlease try rephrasing your question."


# Integration helper for existing codebase
def enhance_with_crewai(index: Dict, question: str) -> str:
    """
    Helper function to integrate CrewAI with existing Ask my PDF index structure

    Args:
        index: The index dictionary from model.index_file()
        question: User's question

    Returns:
        Answer text
    """
    summary = index.get('summary', 'No summary available')
    texts = index.get('texts', [])

    # Use top fragments (would normally come from vector search)
    top_fragments = texts[:5] if len(texts) > 5 else texts

    return get_crewai_answer(question, summary, top_fragments, use_hyde=False)
