"""
Vector store manager using ChromaDB with multi-provider support.
Supports both OpenAI and Google Gemini for embeddings.
"""
import os
from typing import List, Dict
import chromadb

# Import based on provider
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class VectorStore:
    """Manages ChromaDB vector store with multi-provider embedding support."""
    
    def __init__(self, persist_dir: str, collection_name: str = "policy_documents"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        # Determine provider
        self.provider = os.getenv("LLM_PROVIDER", "google").lower()
        
        # For Groq, we need to use a different provider for embeddings
        # since Groq doesn't provide embedding models
        embedding_provider = self.provider
        if self.provider == "groq":
            # Default to Google for embeddings when using Groq
            embedding_provider = os.getenv("EMBEDDING_PROVIDER", "google").lower()
            print(f"Using Groq for LLM, {embedding_provider.upper()} for embeddings")
        
        # Initialize embedding client based on provider
        if embedding_provider == "openai":
            if OpenAI is None:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            self.embedding_provider = "openai"
        elif embedding_provider == "google":
            if genai is None:
                raise ImportError("Google GenAI package not installed. Run: pip install google-genai")
            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            self.genai_client = client
            self.embedding_model = "gemini-embedding-001"
            self.embedding_provider = "google"
        else:
            raise ValueError(f"Unsupported embedding provider: {embedding_provider}. Use 'openai' or 'google'")
        
        print(f"Using {embedding_provider.upper()} for embeddings")
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize ChromaDB client and collection."""
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
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
        """Generate embeddings using configured provider."""
        if self.embedding_provider == "openai":
            return self._generate_openai_embeddings(texts)
        elif self.embedding_provider == "google":
            return self._generate_google_embeddings(texts)
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
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
    
    def _generate_google_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google Gemini API."""
        import time
        embeddings = []
        
        print(f"Generating embeddings for {len(texts)} texts using Gemini...")
        print("Note: Free tier limit is 100 requests/minute, adding delays...")
        
        for i, text in enumerate(texts):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(texts)}")
            
            # Rate limiting: 100 requests per minute = 1 request per 0.6 seconds
            if i > 0 and i % 90 == 0:
                print("  Pausing for 60 seconds to respect rate limits...")
                time.sleep(60)
            
            try:
                response = self.genai_client.models.embed_content(
                    model=self.embedding_model,
                    contents=text
                )
                embeddings.append(response.embeddings[0].values)
                time.sleep(0.7)  # Small delay between requests
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"  Rate limit hit at {i}/{len(texts)}, waiting 60 seconds...")
                    time.sleep(60)
                    # Retry
                    response = self.genai_client.models.embed_content(
                        model=self.embedding_model,
                        contents=text
                    )
                    embeddings.append(response.embeddings[0].values)
                else:
                    raise
        
        print(f"  Completed: {len(texts)}/{len(texts)}")
        return embeddings
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents using semantic similarity."""
        # Generate query embedding
        if self.embedding_provider == "google":
            response = self.genai_client.models.embed_content(
                model=self.embedding_model,
                contents=query
            )
            query_embedding = response.embeddings[0].values
        else:
            query_embedding = self._generate_openai_embeddings([query])[0]
        
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
            'persist_dir': self.persist_dir,
            'provider': self.provider
        }
