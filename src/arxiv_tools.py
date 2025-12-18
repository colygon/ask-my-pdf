"""
ArxivPaperTool Integration for Ask my PDF
Agent 58 Tool Enhancement T4

This module integrates CrewAI's ArxivPaperTool to fetch academic papers from Arxiv.
The tool enables agents to search for and retrieve relevant academic papers that can
provide additional context for PDF analysis and question answering.
"""

from crewai_tools import ArxivPaperTool


class PDFArxivTools:
    """Factory class for creating and managing Arxiv tools for PDF analysis"""

    def __init__(self):
        """Initialize Arxiv tools"""
        self.arxiv_tool = None

    def create_arxiv_tool(self):
        """
        Create and configure ArxivPaperTool

        The ArxivPaperTool allows agents to:
        - Search for academic papers on Arxiv
        - Retrieve paper abstracts and metadata
        - Find related research to provide additional context

        Returns:
            ArxivPaperTool: Configured Arxiv paper search tool
        """
        if self.arxiv_tool is None:
            self.arxiv_tool = ArxivPaperTool()
        return self.arxiv_tool

    def get_tools(self):
        """
        Get all available tools as a list

        Returns:
            list: List of configured tools [ArxivPaperTool]
        """
        return [self.create_arxiv_tool()]


def create_arxiv_tool():
    """
    Convenience function to create a single ArxivPaperTool instance

    Usage:
        from arxiv_tools import create_arxiv_tool

        arxiv_tool = create_arxiv_tool()

    Returns:
        ArxivPaperTool: Configured Arxiv paper search tool
    """
    factory = PDFArxivTools()
    return factory.create_arxiv_tool()


def get_all_pdf_tools():
    """
    Get all available tools for PDF analysis

    Usage:
        from arxiv_tools import get_all_pdf_tools

        tools = get_all_pdf_tools()
        # Pass tools to agents

    Returns:
        list: List of all available tools
    """
    factory = PDFArxivTools()
    return factory.get_tools()
