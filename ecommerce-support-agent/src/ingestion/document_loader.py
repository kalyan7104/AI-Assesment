"""
Document loader for policy documents.
Loads markdown files and extracts metadata.
"""
import os
from pathlib import Path
from typing import List, Dict
import re


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
        
        for file_path in self.policies_dir.glob("*.md"):
            doc = self._load_single_document(file_path)
            if doc:
                documents.append(doc)
        
        print(f"Loaded {len(documents)} policy documents")
        return documents
    
    def _load_single_document(self, file_path: Path) -> PolicyDocument:
        """Load a single markdown document and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = self._extract_metadata(content, file_path)
            
            return PolicyDocument(content=content, metadata=metadata)
        
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
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
