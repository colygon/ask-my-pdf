"""
CrewAI Agents for Ask my PDF
Agent 58 Implementation

This module defines three specialized agents for PDF question answering:
1. PDF Analyzer Agent - Extracts and analyzes PDF content
2. Context Researcher Agent - Finds relevant context from PDF fragments
3. Answer Synthesizer Agent - Generates comprehensive answers
"""

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from arxiv_tools import get_all_pdf_tools
import os


class PDFCrewAgents:
    """Factory class for creating specialized PDF Q&A agents"""

    def __init__(self, api_key=None, model="gpt-3.5-turbo", temperature=0.0, use_arxiv=False):
        """
        Initialize PDF Crew Agents

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: LLM model to use
            temperature: Temperature for LLM responses
            use_arxiv: Enable ArxivPaperTool for academic paper search
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.temperature = temperature
        self.use_arxiv = use_arxiv

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=self.api_key
        )

        # Initialize tools
        self.tools = get_all_pdf_tools() if use_arxiv else []

    def create_pdf_analyzer_agent(self):
        """
        Create PDF Analyzer Agent

        Role: Extract and analyze PDF document structure and content
        """
        return Agent(
            role='PDF Content Analyzer',
            goal='Extract, structure, and analyze PDF document content to understand its organization and key information',
            backstory="""You are an expert in document analysis with years of experience
            in processing and understanding PDF documents. You excel at identifying document
            structure, key sections, and important information. You can quickly parse through
            pages and fragments to understand the overall context and organization of documents.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_context_researcher_agent(self):
        """
        Create Context Researcher Agent

        Role: Find and rank relevant context from PDF fragments
        Tools: ArxivPaperTool (if enabled) for searching academic papers
        """
        backstory = """You are a research specialist with exceptional skills in information
            retrieval and semantic search. You understand how to match questions with relevant
            context, even when the connection is not immediately obvious. You excel at ranking
            information by relevance and identifying the most useful fragments from large documents.
            You use advanced techniques like HyDE (Hypothetical Document Embeddings) to improve
            search accuracy."""

        if self.use_arxiv:
            backstory += """ Additionally, you have access to Arxiv academic paper search to find
            relevant research papers that can provide supplementary context and theoretical foundations
            for answering complex questions."""

        return Agent(
            role='Context Research Specialist',
            goal='Find the most relevant document fragments and context that best answer user questions',
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )

    def create_answer_synthesizer_agent(self):
        """
        Create Answer Synthesizer Agent

        Role: Generate comprehensive answers from context
        """
        return Agent(
            role='Answer Synthesis Expert',
            goal='Synthesize clear, accurate, and comprehensive answers based on provided context from PDF documents',
            backstory="""You are an expert in natural language generation and information
            synthesis. You have a talent for taking complex information from multiple sources
            and weaving it into coherent, accurate, and easy-to-understand answers. You always
            cite your sources and ensure your answers are grounded in the provided context.
            You never hallucinate or make up information - if the context doesn't contain the
            answer, you say so clearly.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_pdf_qa_crew(self):
        """
        Create complete crew with all three agents

        Returns:
            tuple: (analyzer_agent, researcher_agent, synthesizer_agent)
        """
        analyzer = self.create_pdf_analyzer_agent()
        researcher = self.create_context_researcher_agent()
        synthesizer = self.create_answer_synthesizer_agent()

        return analyzer, researcher, synthesizer


class PDFQuestionAnsweringCrew:
    """
    Complete CrewAI implementation for PDF Question Answering
    Orchestrates the three agents to answer questions about PDF documents
    """

    def __init__(self, index, api_key=None, model="gpt-3.5-turbo", temperature=0.0, use_arxiv=False):
        """
        Initialize PDF Q&A Crew

        Args:
            index: PDF index dictionary with vectors, texts, pages, and summary
            api_key: OpenAI API key
            model: LLM model to use
            temperature: Temperature for responses
            use_arxiv: Enable ArxivPaperTool for academic paper search
        """
        self.index = index
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.temperature = temperature
        self.use_arxiv = use_arxiv

        # Initialize agents factory
        self.agents_factory = PDFCrewAgents(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            use_arxiv=self.use_arxiv
        )

        # Create agents
        self.analyzer, self.researcher, self.synthesizer = \
            self.agents_factory.create_pdf_qa_crew()

    def answer_question(self, question, context_fragments, max_frags=4):
        """
        Answer a question using the crew of agents

        Args:
            question: User's question
            context_fragments: List of relevant text fragments from PDF
            max_frags: Maximum number of fragments to use

        Returns:
            dict: Answer and metadata
        """
        # Prepare context
        context = "\n---\n".join(context_fragments[:max_frags])
        doc_summary = self.index.get('summary', '')

        # Task 1: Analyze document structure
        analyze_task = Task(
            description=f"""Analyze the following document summary and context fragments:

            Document Summary: {doc_summary}

            Context Fragments:
            {context}

            Identify the key topics, structure, and type of information contained in these fragments.
            Provide a brief analysis of what kind of document this is and what information it contains.""",
            agent=self.analyzer,
            expected_output="A brief analysis of the document structure and content type"
        )

        # Task 2: Research relevant context
        research_description = f"""Given the user's question: "{question}"

            And the following context fragments:
            {context}

            Identify which parts of the context are most relevant to answering the question.
            Rank the information by relevance and extract the key facts needed to answer the question."""

        if self.use_arxiv:
            research_description += """

            If the question relates to academic or technical topics, you may search Arxiv for relevant
            research papers to provide additional context and theoretical foundations. Use the ArxivPaperTool
            to find papers related to the question topic."""

        research_description += """

            If the context doesn't contain information to answer the question, state that clearly."""

        research_task = Task(
            description=research_description,
            agent=self.researcher,
            expected_output="Ranked list of relevant information extracted from context, with optional Arxiv paper references if applicable"
        )

        # Task 3: Synthesize answer
        synthesis_task = Task(
            description=f"""Based on the document analysis and research findings,
            answer the following question: "{question}"

            Use only the information provided in the context. Be clear, concise, and accurate.
            If the context doesn't contain enough information to answer the question fully,
            state what information is missing. Always ground your answer in the provided context.""",
            agent=self.synthesizer,
            expected_output="A clear, accurate answer to the user's question based on the context"
        )

        # Create crew
        crew = Crew(
            agents=[self.analyzer, self.researcher, self.synthesizer],
            tasks=[analyze_task, research_task, synthesis_task],
            process=Process.sequential,
            verbose=True
        )

        # Execute crew
        result = crew.kickoff()

        response = {
            'text': str(result),
            'model': self.model,
            'agents_used': ['PDF Analyzer', 'Context Researcher', 'Answer Synthesizer'],
            'context_fragments': len(context_fragments[:max_frags])
        }

        if self.use_arxiv:
            response['tools_enabled'] = ['ArxivPaperTool']

        return response


def create_crew_for_query(index, question, context_fragments, **kwargs):
    """
    Convenience function to create crew and answer question

    Args:
        index: PDF index dictionary
        question: User's question
        context_fragments: List of relevant text fragments
        **kwargs: Additional arguments (api_key, model, temperature, max_frags, use_arxiv)

    Returns:
        dict: Answer and metadata
    """
    crew = PDFQuestionAnsweringCrew(
        index=index,
        api_key=kwargs.get('api_key'),
        model=kwargs.get('model', 'gpt-3.5-turbo'),
        temperature=kwargs.get('temperature', 0.0),
        use_arxiv=kwargs.get('use_arxiv', False)
    )

    return crew.answer_question(
        question=question,
        context_fragments=context_fragments,
        max_frags=kwargs.get('max_frags', 4)
    )
