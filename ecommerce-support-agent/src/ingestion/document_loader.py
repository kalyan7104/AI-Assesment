"""
Document loader for policy documents.
Loads markdown, HTML, and PDF files and extracts metadata.
"""
import os
from pathlib import Path
from typing import List, Dict
import re

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class PolicyDocument:
    """Represents a policy document with metadata."""
    
    def __init__(self, content: str, metadata: Dict):
        self.content = content
        self.metadata = metadata


class DocumentLoader:
    """Loads and processes policy documents from markdown files."""
    
    def __init__(self, policies_dir: str):
        self.policies_dir = Path(policies_dir)
    
    def load_documents(self) -> List[PolicyDocument]:
        """Load all policy documents from the policies directory."""
        documents = []
        
        # Load markdown files
        for file_path in self.policies_dir.glob("*.md"):
            doc = self._load_single_document(file_path)
            if doc:
                documents.append(doc)
        
        # Load HTML files
        for file_path in self.policies_dir.glob("*.html"):
            doc = self._load_single_document(file_path)
            if doc:
                documents.append(doc)
        
        # Load PDF files
        for file_path in self.policies_dir.glob("*.pdf"):
            doc = self._load_single_document(file_path)
            if doc:
                documents.append(doc)
        
        print(f"Loaded {len(documents)} policy documents")
        return documents
    
    def _load_single_document(self, file_path: Path) -> PolicyDocument:
        """Load a single document (markdown, HTML, or PDF) and extract metadata."""
        try:
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.md':
                content = self._load_markdown(file_path)
            elif file_ext == '.html':
                content = self._load_html(file_path)
            elif file_ext == '.pdf':
                content = self._load_pdf(file_path)
            else:
                print(f"Unsupported file type: {file_ext}")
                return None
            
            if not content:
                return None
            
            metadata = self._extract_metadata(content, file_path)
            
            return PolicyDocument(content=content, metadata=metadata)
        
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    def _load_markdown(self, file_path: Path) -> str:
        """Load markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_html(self, file_path: Path) -> str:
        """Load and parse HTML file."""
        if BeautifulSoup is None:
            print("Warning: BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _load_pdf(self, file_path: Path) -> str:
        """Load and parse PDF file."""
        if PdfReader is None:
            print("Warning: PyPDF2 not installed. Install with: pip install pypdf2")
            return None
        
        try:
            reader = PdfReader(str(file_path))
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return '\n\n'.join(text_parts)
        
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
            return None
    
    def _extract_metadata(self, content: str, file_path: Path) -> Dict:
        """Extract metadata from document content."""
        metadata = {
            'source': str(file_path),
            'filename': file_path.name,
        }
        
        # Extract title (first heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Extract document ID
        doc_id_match = re.search(r'\*\*Document ID:\*\*\s+(.+)$', content, re.MULTILINE)
        if doc_id_match:
            metadata['document_id'] = doc_id_match.group(1).strip()
        
        # Extract version
        version_match = re.search(r'\*\*Version:\*\*\s+(.+)$', content, re.MULTILINE)
        if version_match:
            metadata['version'] = version_match.group(1).strip()
        
        # Extract last updated
        updated_match = re.search(r'\*\*Last Updated:\*\*\s+(.+)$', content, re.MULTILINE)
        if updated_match:
            metadata['last_updated'] = updated_match.group(1).strip()
        
        return metadata
