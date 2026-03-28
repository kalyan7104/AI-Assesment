"""
Test script for document ingestion and retrieval.
Run this to verify the vector store is working correctly.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
import sys
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.retrieval.vector_store import VectorStore


def test_retrieval():
    """Test the vector store retrieval."""
    print("=" * 60)
    print("Testing Vector Store Retrieval")
    print("=" * 60)
    
    # Initialize vector store
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    vector_store = VectorStore(persist_dir)
    
    # Get stats
    stats = vector_store.get_stats()
    print(f"\nVector Store Stats:")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Total documents: {stats['total_documents']}")
    
    if stats['total_documents'] == 0:
        print("\n⚠️  Vector store is empty!")
        print("Run the ingestion pipeline first:")
        print("  python src/ingestion/pipeline.py")
        return
    
    # Test queries
    test_queries = [
        "What is the return policy?",
        "How long does shipping take?",
        "Can I cancel my order?",
        "What payment methods are accepted?",
        "How do I track my package?"
    ]
    
    print("\n" + "=" * 60)
    print("Testing Sample Queries")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 60)
        
        results = vector_store.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Source: {result['metadata'].get('filename', 'Unknown')}")
            print(f"    Section: {result['metadata'].get('section', 'Unknown')}")
            print(f"    Distance: {result['distance']:.4f}" if result['distance'] else "")
            print(f"    Preview: {result['text'][:150]}...")
    
    print("\n" + "=" * 60)
    print("✅ Retrieval test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_retrieval()
