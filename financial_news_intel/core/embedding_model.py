# from sentence_transformers import SentenceTransformer
# from typing import List, Optional
# from .config import EMBEDDING_MODEL_NAME 
# import threading


# class EmbeddingModel:
#     """
#     Manages the Sentence Transformer model instance as a singleton.
#     This ensures the model is loaded only once, saving memory and time.
#     """
#     # Use the imported constant as the default model name
#     def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
#         self.model_name = model_name
#         self._model: Optional[SentenceTransformer] = None
#         self._dimension: Optional[int] = None
        
#     def get_model(self) -> SentenceTransformer:
#         """Loads and returns the model, prioritizing CPU for standard setup."""
#         if self._model is None:
#             print(f"Loading Sentence Transformer model: {self.model_name}...")
#             # If using a GPU machine, change device='cpu' to device='cuda'
#             self._model = SentenceTransformer(self.model_name, device='cpu') 
#             self._dimension = self._model.get_sentence_embedding_dimension()
#             print(f"Model loaded. Dimension: {self._dimension}")
#         return self._model
    
#     def get_dimension(self) -> int:
#         """Returns the embedding dimension."""
#         if self._dimension is None:
#             self.get_model() 
#         return self._dimension

# # Initialize the global instance to be imported by other modules
# embedding_model = EmbeddingModel()

# def get_embeddings(texts: List[str]) -> List[List[float]]:
#     """Generates embeddings for a list of text strings."""
#     model = embedding_model.get_model()
#     # Encode texts and convert to list of lists for compatibility
#     embeddings = model.encode(texts, convert_to_numpy=True).tolist()
#     return embeddings

# class ChromaEmbeddingFunctionWrapper:
#     """Wraps the get_embeddings function to satisfy ChromaDB's interface requirements."""
    
#     # CRITICAL FIX: Parameter name MUST be 'input' (not 'texts') to satisfy ChromaDB's API
#     def __call__(self, input: List[str]) -> List[List[float]]:
#         # Pass the 'input' (which is a list of strings) to our existing get_embeddings function
#         return get_embeddings(input)
    
#     def embed_query(self, input: str) -> List[float]:
#         """
#         Embeds a single query string. Required by ChromaDB's query function.
#         """
#         # 1. Wrap the single query string in a list to use the batch function
#         embedding_list_of_lists = get_embeddings([input])
#         if not embedding_list_of_lists:
#             # Raising an error here is the safest way to fail the retrieval step gracefully.
#             # The vector_db.search try/except block will catch this.
#             raise ValueError(
#                 f"Embedding model failed to generate a vector for query: '{input}'. "
#                 "The SentenceTransformer returned an empty result."
#             ) 

#         # 2. Return the single embedding vector (the first element of the list of lists)
#         return embedding_list_of_lists[0]
    
#     def name(self) -> str:
#         """Exposes the required 'name' method for ChromaDB validation."""
#         return EMBEDDING_MODEL_NAME

# embedding_function = ChromaEmbeddingFunctionWrapper()


from sentence_transformers import SentenceTransformer
from typing import List, Optional
from .config import EMBEDDING_MODEL_NAME 
import threading


class EmbeddingModel:
    """
    Manages the Sentence Transformer model instance as a singleton.
    This ensures the model is loaded only once, saving memory and time.
    """
    # Use the imported constant as the default model name
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._dimension: Optional[int] = None
        self._lock = threading.Lock() # 🛑 CRITICAL: Initialize a thread lock
        
    def get_model(self) -> SentenceTransformer:
        """Loads and returns the model, prioritizing CPU for standard setup."""
        if self._model is None:
            print(f"Loading Sentence Transformer model: {self.model_name}...")
            # Ensure model is set to CPU explicitly for stability in Docker
            self._model = SentenceTransformer(self.model_name, device='cpu') 
            self._dimension = self._model.get_sentence_embedding_dimension()
            print(f"Model loaded. Dimension: {self._dimension}")
        return self._model
    
    def get_dimension(self) -> int:
        """Returns the embedding dimension."""
        if self._dimension is None:
            self.get_model() 
        return self._dimension

# Initialize the global instance to be imported by other modules
embedding_model = EmbeddingModel()

# Pre-initialize the model to ensure it's loaded before ChromaDB tries to use it
# This prevents issues where ChromaDB calls the embedding function before the model is loaded
try:
    print("Pre-initializing embedding model for ChromaDB compatibility...")
    embedding_model.get_model()  # Force model loading
    print("Embedding model pre-initialization complete.")
except Exception as e:
    print(f"Warning: Failed to pre-initialize embedding model: {e}")
    print("Model will be loaded on first use, which may cause delays.")

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generates embeddings for a list of text strings, protected by a thread lock."""
    try:
        # Validate input
        if not texts or not isinstance(texts, list):
            raise ValueError(f"get_embeddings expects a non-empty list of strings, got: {type(texts)}")
        
        if not all(isinstance(text, str) for text in texts):
            raise ValueError(f"All items in texts must be strings")
        
        model = embedding_model.get_model()
        
        if model is None:
            raise ValueError("Embedding model is None. Model initialization failed.")
        
        # 🛑 CRITICAL: Acquire lock to prevent concurrent access to model.encode()
        with embedding_model._lock:
            # Encode texts and convert to list of lists for compatibility
            # We explicitly set show_progress_bar=False to reduce overhead/logs
            embeddings = model.encode(
                texts, 
                convert_to_numpy=True,
                show_progress_bar=False # Turn off progress bar for cleaner logging
            )
            
            # Convert to list of lists
            if hasattr(embeddings, 'tolist'):
                embeddings = embeddings.tolist()
            elif isinstance(embeddings, list):
                # Already a list, ensure it's list of lists
                if embeddings and not isinstance(embeddings[0], list):
                    embeddings = [embeddings]
            else:
                raise ValueError(f"Unexpected embedding format: {type(embeddings)}")
            
            # Validate output
            if not embeddings or len(embeddings) == 0:
                raise ValueError("Embedding model returned empty result")
            
            if len(embeddings) != len(texts):
                raise ValueError(f"Expected {len(texts)} embeddings, got {len(embeddings)}")
        
        return embeddings
    except Exception as e:
        import traceback
        error_msg = f"Error in get_embeddings: {e}\nTraceback: {traceback.format_exc()}"
        print(error_msg)
        raise

class ChromaEmbeddingFunctionWrapper:
    """Wraps the get_embeddings function to satisfy ChromaDB's interface requirements."""
    
    # CRITICAL FIX: Parameter name MUST be 'input' (not 'texts') to satisfy ChromaDB's API
    def __call__(self, input) -> List[List[float]]:
        """
        ChromaDB calls this method when using query_texts or when adding documents.
        Handles various input types that ChromaDB might pass.
        """
        try:
            # Handle None or empty input
            if input is None:
                raise ValueError("ChromaEmbeddingFunctionWrapper.__call__ received None input")
            
            # Convert to list if it's a single string (ChromaDB might pass a single string)
            if isinstance(input, str):
                input = [input]
            
            # Validate it's now a list
            if not isinstance(input, list):
                raise ValueError(f"ChromaEmbeddingFunctionWrapper.__call__ expects a list or string, got {type(input)}: {input}")
            
            if len(input) == 0:
                raise ValueError("ChromaEmbeddingFunctionWrapper.__call__ received empty list")
            
            # Ensure all items are strings (convert if necessary)
            text_list = []
            for item in input:
                if isinstance(item, str):
                    text_list.append(item)
                else:
                    # Try to convert to string
                    text_list.append(str(item))
            
            if not text_list:
                raise ValueError(f"Could not extract any strings from input: {input}")
            
            # Pass the text list to our existing get_embeddings function
            result = get_embeddings(text_list)
            
            # Validate result
            if not result:
                raise ValueError(f"get_embeddings returned empty result for input: {str(input)[:50]}...")
            
            return result
        except Exception as e:
            import traceback
            error_msg = f"Error in ChromaEmbeddingFunctionWrapper.__call__: {e}\nInput type: {type(input)}, Input value: {str(input)[:100] if input else 'None'}\nTraceback: {traceback.format_exc()}"
            print(error_msg)
            raise
    
    def embed_query(self, input: str) -> List[float]:
        """
        Embeds a single query string. Required by ChromaDB's query function.
        This method is called by ChromaDB when using query_texts with a single query.
        """
        try:
            # Validate input
            if not input or not isinstance(input, str):
                raise ValueError(f"embed_query expects a non-empty string, got: {type(input)}")
            
            # 1. Wrap the single query string in a list to use the batch function
            embedding_list_of_lists = get_embeddings([input])
            
            if not embedding_list_of_lists or not embedding_list_of_lists[0]:
                # Raising an error is still necessary as the failsafe, in case the lock 
                # or environment stabilization fails to resolve the issue 100% of the time.
                raise ValueError(
                    f"Embedding model failed to generate a vector for query: '{input}'. "
                    "The SentenceTransformer returned an empty result."
                ) 

            # 2. Return the single embedding vector (the first element of the list of lists)
            return embedding_list_of_lists[0]
        except Exception as e:
            import traceback
            error_msg = f"Error in ChromaEmbeddingFunctionWrapper.embed_query: {e}\nInput: {input}\nTraceback: {traceback.format_exc()}"
            print(error_msg)
            raise
    
    def name(self) -> str:
        """Exposes the required 'name' method for ChromaDB validation."""
        return EMBEDDING_MODEL_NAME

embedding_function = ChromaEmbeddingFunctionWrapper()