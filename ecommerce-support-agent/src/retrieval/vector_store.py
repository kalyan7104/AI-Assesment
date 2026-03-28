"""
Vector store manager using ChromaDB.
Handles document embedding, storage, and retrieval.
"""
import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI


class VectorStore:
    """Manages ChromaDB vector store for document retrieval."""
    
    def __init__(self, persist_dir: str, collection_name: str = "policy_documents"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize ChromaDB client and collection."""
        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "E-commerce policy documents"}
        )
        
        print(f"Initialized vector store at {self.persist_dir}")
        print(f"Collection '{self.collection_name}' has {self.collection.count()} documents")
    
    def add_documents(self, chunks: List):
        """Add document chunks to the vector store."""
        if not chunks:
            print("No chunks to add")
            return
        
        print(f"Adding {len(chunks)} chunks to vector store...")
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk.text)
            metadatas.append(chunk.metadata)
            ids.append(f"chunk_{i}")
        
        # Generate embeddings
        embeddings = self._generate_embeddings(documents)
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Successfully added {len(chunks)} chunks to vector store")
        print(f"Total documents in collection: {self.collection.count()}")
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        embeddings = []
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents using semantic similarity."""
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "E-commerce policy documents"}
        )
        print(f"Cleared collection '{self.collection_name}'")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            'collection_name': self.collection_name,
            'total_documents': self.collection.count(),
            'persist_dir': self.persist_dir
        }
