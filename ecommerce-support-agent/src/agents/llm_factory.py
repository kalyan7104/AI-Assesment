"""
LLM factory to create language models based on provider configuration.
Supports: OpenAI, Google Gemini, Groq
"""
import os


def get_llm(temperature: float = 0.1):
    """
    Get configured LLM string identifier for CrewAI.
    
    Args:
        temperature: Temperature for generation (0.0 = deterministic, 1.0 = creative)
    
    Returns:
        LLM string identifier for CrewAI
    """
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    
    if provider == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        return f"openai/{model}"
    
    elif provider == "google":
        model = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        return f"google/{model}"
    
    elif provider == "groq":
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return f"groq/{model}"
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Use 'openai', 'google', or 'groq'")
