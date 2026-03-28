"""
Text chunker for splitting documents into smaller chunks.
Preserves section context and metadata.
"""
import re
from typing import List, Dict


class DocumentChunk:
    """Represents a chunk of text with metadata."""
    
    def __init__(self, text: str, metadata: Dict):
        self.text = text
        self.metadata = metadata


class TextChunker:
    """Splits documents into chunks while preserving context."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_documents(self, documents: List) -> List[DocumentChunk]:
        """Chunk all documents into smaller pieces."""
        all_chunks = []
        
        for doc in documents:
            chunks = self._chunk_by_sections(doc)
            all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def _chunk_by_sections(self, document) -> List[DocumentChunk]:
        """Chunk document by sections for better context preservation."""
        chunks = []
        content = document.content
        base_metadata = document.metadata.copy()
        
        # Split by main sections (## headings)
        sections = re.split(r'\n(?=##\s)', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            # Extract section title
            section_title = self._extract_section_title(section)
            
            # Split long sections into smaller chunks
            section_chunks = self._split_section(section, section_title, base_metadata)
            chunks.extend(section_chunks)
        
        return chunks
    
    def _extract_section_title(self, section: str) -> str:
        """Extract the section title from markdown heading."""
        match = re.match(r'##\s+(.+?)(?:\n|$)', section)
        if match:
            return match.group(1).strip()
        return "Introduction"
    
    def _split_section(self, section: str, section_title: str, base_metadata: Dict) -> List[DocumentChunk]:
        """Split a section into chunks if it's too long."""
        chunks = []
        
        # If section is small enough, keep it as one chunk
        if len(section) <= self.chunk_size:
            metadata = base_metadata.copy()
            metadata['section'] = section_title
            chunks.append(DocumentChunk(text=section, metadata=metadata))
            return chunks
        
        # Split by subsections (### headings)
        subsections = re.split(r'\n(?=###\s)', section)
        
        for subsection in subsections:
            if not subsection.strip():
                continue
            
            subsection_title = self._extract_subsection_title(subsection)
            full_title = f"{section_title} > {subsection_title}" if subsection_title else section_title
            
            # If subsection is still too long, split by paragraphs
            if len(subsection) > self.chunk_size:
                para_chunks = self._split_by_paragraphs(subsection, full_title, base_metadata)
                chunks.extend(para_chunks)
            else:
                metadata = base_metadata.copy()
                metadata['section'] = full_title
                chunks.append(DocumentChunk(text=subsection, metadata=metadata))
        
        return chunks
    
    def _extract_subsection_title(self, subsection: str) -> str:
        """Extract subsection title from markdown heading."""
        match = re.match(r'###\s+(.+?)(?:\n|$)', subsection)
        if match:
            return match.group(1).strip()
        return ""
    
    def _split_by_paragraphs(self, text: str, section_title: str, base_metadata: Dict) -> List[DocumentChunk]:
        """Split long text by paragraphs with overlap."""
        chunks = []
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                metadata = base_metadata.copy()
                metadata['section'] = section_title
                chunks.append(DocumentChunk(text=current_chunk.strip(), metadata=metadata))
                
                # Start new chunk with overlap (last paragraph)
                current_chunk = para + "\n\n"
            else:
                current_chunk += para + "\n\n"
        
        # Add remaining chunk
        if current_chunk.strip():
            metadata = base_metadata.copy()
            metadata['section'] = section_title
            chunks.append(DocumentChunk(text=current_chunk.strip(), metadata=metadata))
        
        return chunks
