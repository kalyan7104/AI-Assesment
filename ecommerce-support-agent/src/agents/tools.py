"""
Custom tools for agents to interact with the vector store.
"""
import os
from typing import List, Dict
from crewai.tools import BaseTool
from pydantic import Field

from src.retrieval.vector_store_multi import VectorStore


class PolicyRetrievalTool(BaseTool):
    """Tool for retrieving relevant policy information from vector store."""
    
    name: str = "Policy Retrieval Tool"
    description: str = (
        "Searches the policy knowledge base for relevant information. "
        "Use this tool to find specific policy details, rules, and procedures. "
        "Input should be a clear question or search query about policies."
    )
    
    vector_store: VectorStore = Field(default=None, exclude=True)
    
    def __init__(self):
        super().__init__()
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.vector_store = VectorStore(persist_dir)
    
    def _run(self, query: str) -> str:
        """Execute the policy retrieval."""
        try:
            # Get top_k from environment or use default
            top_k = int(os.getenv("TOP_K_RESULTS", "5"))
            
            # Get minimum evidence threshold
            min_evidence_threshold = int(os.getenv("MIN_EVIDENCE_THRESHOLD", "2"))
            
            # Search vector store
            results = self.vector_store.search(query, top_k=top_k)
            
            if not results:
                return "No relevant policy information found for this query."
            
            # Check minimum evidence threshold
            if len(results) < min_evidence_threshold:
                return (
                    f"INSUFFICIENT EVIDENCE: Only {len(results)} relevant policy document(s) found, "
                    f"but minimum threshold is {min_evidence_threshold}. "
                    f"Cannot provide a reliable answer without sufficient policy evidence. "
                    f"This query may require human review or the policy may not exist."
                )
            
            # Format results with citations
            formatted_output = self._format_results(results)
            return formatted_output
            
        except Exception as e:
            return f"Error retrieving policy information: {str(e)}"
    
    def _format_results(self, results: List[Dict]) -> str:
        """Format search results with proper citations."""
        output = []
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            text = result['text']
            
            # Extract citation information
            doc_id = metadata.get('document_id', 'Unknown')
            title = metadata.get('title', 'Unknown Policy')
            section = metadata.get('section', 'General')
            
            # Format each result
            output.append(f"\n--- Source {i} ---")
            output.append(f"Document: {title} ({doc_id})")
            output.append(f"Section: {section}")
            output.append(f"\nContent:\n{text}")
            output.append("-" * 50)
        
        return "\n".join(output)


class PolicySearchTool(BaseTool):
    """Simplified tool for quick policy searches."""
    
    name: str = "Quick Policy Search"
    description: str = (
        "Quickly search for specific policy terms or topics. "
        "Returns concise, relevant policy excerpts. "
        "Best for finding specific rules, timeframes, or requirements."
    )
    
    vector_store: VectorStore = Field(default=None, exclude=True)
    
    def __init__(self):
        super().__init__()
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.vector_store = VectorStore(persist_dir)
    
    def _run(self, query: str) -> str:
        """Execute quick policy search."""
        try:
            # Use fewer results for quick search
            results = self.vector_store.search(query, top_k=3)
            
            if not results:
                return "No policy information found."
            
            # Return concise format
            output = []
            for result in results:
                metadata = result['metadata']
                text = result['text'][:300]  # Truncate for brevity
                
                output.append(
                    f"[{metadata.get('document_id', 'N/A')}] "
                    f"{metadata.get('section', 'N/A')}: {text}..."
                )
            
            return "\n\n".join(output)
            
        except Exception as e:
            return f"Search error: {str(e)}"
