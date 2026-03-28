"""
Ingestion pipeline to process policy documents and build vector store.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from src.ingestion.document_loader import DocumentLoader
from src.ingestion.text_chunker import TextChunker
from src.retrieval.vector_store import VectorStore


class IngestionPipeline:
    """Orchestrates the document ingestion process."""
    
    def __init__(self, policies_dir: str, persist_dir: str, chunk_size: int = 800, chunk_overlap: int = 100):
        self.policies_dir = policies_dir
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize components
        self.document_loader = DocumentLoader(policies_dir)
        self.text_chunker = TextChunker(chunk_size, chunk_overlap)
        self.vector_store = VectorStore(persist_dir)
    
    def run(self, force_rebuild: bool = False):
        """Run the complete ingestion pipeline."""
        print("=" * 60)
        print("Starting Document Ingestion Pipeline")
        print("=" * 60)
        
        # Check if vector store already exists
        stats = self.vector_store.get_stats()
        if stats['total_documents'] > 0 and not force_rebuild:
            print(f"\nVector store already exists with {stats['total_documents']} documents")
            print("Use force_rebuild=True to rebuild from scratch")
            return
        
        if force_rebuild:
            print("\nForce rebuild enabled - clearing existing vector store...")
            self.vector_store.clear_collection()
        
        # Step 1: Load documents
        print("\n[Step 1/3] Loading policy documents...")
        documents = self.document_loader.load_documents()
        
        if not documents:
            print("Error: No documents loaded!")
            return
        
        # Step 2: Chunk documents
        print("\n[Step 2/3] Chunking documents...")
        chunks = self.text_chunker.chunk_documents(documents)
        
        if not chunks:
            print("Error: No chunks created!")
            return
        
        # Step 3: Add to vector store
        print("\n[Step 3/3] Adding chunks to vector store...")
        self.vector_store.add_documents(chunks)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Ingestion Pipeline Complete!")
        print("=" * 60)
        stats = self.vector_store.get_stats()
        print(f"Collection: {stats['collection_name']}")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Persist directory: {stats['persist_dir']}")
        print("=" * 60)


def main():
    """Main function to run ingestion pipeline."""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    base_dir = Path(__file__).parent.parent.parent
    policies_dir = base_dir / "data" / "policies"
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", str(base_dir / "chroma_db"))
    chunk_size = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    # Verify policies directory exists
    if not policies_dir.exists():
        print(f"Error: Policies directory not found at {policies_dir}")
        return
    
    # Create and run pipeline
    pipeline = IngestionPipeline(
        policies_dir=str(policies_dir),
        persist_dir=persist_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Run with force_rebuild=True to rebuild from scratch
    pipeline.run(force_rebuild=True)


if __name__ == "__main__":
    main()
