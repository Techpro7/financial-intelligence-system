from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel # Correct Type Hinting
from .config import OLLAMA_MODEL_NAME, OLLAMA_BASE_URL 

class LLMService:
    """
    A singleton class to manage the Ollama LLM connection instance.
    Switched to ChatOllama for Pydantic/Tool binding compatibility.
    """
    def __init__(self, model_name: str = OLLAMA_MODEL_NAME, base_url: str = OLLAMA_BASE_URL):
        # Initialize the ChatOllama client
        # We use a low temperature here as most agent/tool use benefits from deterministic output.
        self._llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.0) 
        print(f"ChatOllama client initialized: Model='{model_name}', URL='{base_url}'")

    def get_llm(self) -> BaseChatModel:
        """Returns the configured ChatOllama LLM instance."""
        return self._llm

# Global instance for easy import across all agents
llm_service = LLMService()