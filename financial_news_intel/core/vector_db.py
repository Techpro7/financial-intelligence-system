import chromadb
# ... other imports
# Import the config variables from where you defined them (e.g., config.py)
from typing import List, Dict, Any
from .config import CHROMA_COLLECTION_NAME, CHROMA_DB_MODE, CHROMA_DB_URL, CHROMA_DB_PATH, CHROMA_RAG_COLLECTION_NAME
from .embedding_model import embedding_function

class VectorDBClient:
    
    def __init__(self):
        # ------------------- CRITICAL LOGIC SWITCH -------------------
        if CHROMA_DB_MODE == "remote":
            # Extract host and port from the URL for stable HttpClient initialization
            # NOTE: We assume CHROMA_DB_URL is "http://host:port"
            
            # 1. Strip 'http://'
            host_port = CHROMA_DB_URL.replace("http://", "") 
            # 2. Split into host and port
            host = host_port.split(':')[0]
            port = host_port.split(':')[1]

            print(f"Connecting to ChromaDB server at {host}:{port}")
            
            # FIX: Use 'host' and 'port' instead of 'url'
            self.client = chromadb.HttpClient(host=host, port=port)
            
        else:
            # Fallback to the local persistent client
            print(f"Initializing ChromaDB local client at {CHROMA_DB_PATH}")
            self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            
        # Get or create the collection, ensuring the embedding function is used
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=embedding_function
        )

        self.rag_collection = self.client.get_or_create_collection(
            name=CHROMA_RAG_COLLECTION_NAME,
            embedding_function=embedding_function
        )

        print(f"ChromaDB collection '{CHROMA_COLLECTION_NAME}' initialized and persistent at {CHROMA_DB_PATH}")

    def add_article_embedding(self, article_id: str, text: str, embedding: List[float]) -> None:
        """Adds a single document and its pre-calculated embedding to the database."""
        try:
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "source": "deduplication_index",
                    #  CRITICAL FIX: Add placeholder metadata for RAG consistency 
                    "companies": "", 
                    "sectors": "",
                    "regulators": "",
                    "sentiment": "UNCLEAR",
                    "db_id": "",
                }], 
                ids=[article_id]
            )
        except Exception as e:
            print(f"Error adding article {article_id} to ChromaDB: {e}")
            raise

    def add_document(self, id: str, text: str, metadata: Dict[str, Any]) -> str:
        """
        Adds the final, full processed story text and rich metadata to the RAG index.
        Relies on the collection's embedding_function to generate the vector automatically.
        
        This method is used by the Storage & Indexing Agent (Agent 5).
        
        Args:
            id: The unique story ID (UUID).
            text: The full consolidated news story content.
            metadata: Rich metadata (companies, sentiment, db_id, etc.) for filtering.
            
        Returns:
            The ID used for the document (the story ID).
        """
        try:
            # Note: We omit the 'embeddings' argument. Chroma will calculate it 
            # using the embedding_function defined in __init__.
            self.rag_collection.add(
                documents=[text],
                metadatas=[metadata], 
                ids=[id]
            )
            return id
        except Exception as e:
            print(f"Error adding RAG document {id} to ChromaDB: {e}")
            raise

    def search(self, query: str, chroma_filter: dict = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Safe semantic RAG search. Handles empty results without throwing errors.
        """

        try:
            # --- 1. Embed the query with your embedding_function ---
            query_embedding = embedding_function.embed_query(query)

            # --- 2. Build query parameters ---
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": top_k,
                "include": ['distances', 'documents', 'metadatas']
            }

            if chroma_filter:
                query_params["where"] = chroma_filter

            # --- 3. Execute the query ---
            results = self.rag_collection.query(**query_params)

            # --- 4. Strong empty-result protection ---
            if (
                not results
                or "ids" not in results
                or len(results["ids"]) == 0
                or len(results["ids"][0]) == 0
            ):
                print("DEBUG: Chroma returned zero search hits.")
                return []

            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]

            # --- 5. Build output safely ---
            output = []
            for i in range(len(ids)):
                output.append({
                    "id": ids[i],
                    "content": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else None
                })

            return output

        except Exception as e:
            import traceback
            print(f"Error during ChromaDB RAG search: {e}")
            print(traceback.format_exc())
            return []

    def check_for_duplicates(self, query_embedding: List[float], n_results: int = 1) -> List[Dict[str, Any]]:
        """
        Queries the ChromaDB collection for the article most semantically similar to the query embedding.
        
        Returns a list of dictionaries with 'id', 'similarity', and 'document'.
        """
        
        # --- CORRECTION APPLIED HERE ---
        # The query call is now clean, only requesting the top match and relevant data.
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['distances', 'documents'] # Request distances and the original text
        )
        
        # Process and format the results for the agent
        processed_results = []
        if results and results.get('ids') and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                # Distance is 1 - Similarity (ChromaDB uses Euclidean distance internally)
                distance = results['distances'][0][i]
                similarity = 1 - distance
                
                processed_results.append({
                    "id": results['ids'][0][i],
                    "similarity": similarity,
                    "document": results['documents'][0][i]
                })
                
        return processed_results
    
    def clear_collection(self) -> None:
        """
        Resets the entire ChromaDB client, deleting all collections and data.
        Crucial for providing a clean state for testing.
        """
        try:
            print("Resetting ChromaDB client (deleting all collections and data)...")
            # The client.reset() is the standard way to wipe the DB for testing
            self.client.reset() 
            
            # Re-initialize the collection after the reset, so the client is ready to use again
            self.collection = self.client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME,
                embedding_function=embedding_function
            )
            print(f"ChromaDB collection '{CHROMA_COLLECTION_NAME}' re-initialized.")

        except Exception as e:
            print(f"ERROR during ChromaDB reset/re-initialization: {e}")
            raise
    
    def get_indexed_documents(self, limit: int = 5) -> Dict[str, Any]:
        """
        Retrieves the first N documents from the RAG collection with all metadata.
        """
        # The 'get' function retrieves documents by ID, or all if no IDs are passed.
        # We include everything (documents, metadatas, embeddings) for a full check.
        results = self.rag_collection.get(
            limit=limit,
            include=['metadatas', 'documents', 'embeddings']
        )
        return results

# Global singleton instance
vector_db_client = VectorDBClient()