# financial_news_intel/llm/llm_service.py

from financial_news_intel.core.llm_model import llm_service
from langchain_core.pydantic_v1 import BaseModel 

# Get the base Ollama LLM instance
base_ollama_llm = llm_service.get_llm()

# 1. Simple LLM instance for final answer synthesis (direct use of the base LLM)
llm_simple_completion = base_ollama_llm

# 2. Structured Output LLM instance for extracting RAG filters
# We use .with_structured_output to force the LLM to return a Pydantic object.
# Note: Ollama/Llama models rely on the `json_mode` or similar backend for this.
llm_with_structured_output = base_ollama_llm.with_structured_output(
    schema=BaseModel, # Placeholder schema. The actual schema is applied in query_agent.py
    method="json_mode" # Use 'json_mode' for Ollama/Llama models for reliable structured output
)

print("LLM chains initialized for query agent.")