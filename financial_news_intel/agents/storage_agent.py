from financial_news_intel.core.models import FinancialNewsState
from financial_news_intel.core.db_service import db_service        
from financial_news_intel.core.vector_db import vector_db_client  
from langgraph.graph import END

def storage_index_agent(state: FinancialNewsState) -> FinancialNewsState:
    """
    Stores the processed ConsolidatedStory into the Structured Database and 
    the story text and metadata into the Vector Database (ChromaDB) for RAG.
    """
    print("\n--- Running Storage & Indexing Agent ---")
    
    story = state.current_story
    state.error_message = None 

    if not story:
        print("  -> ERROR: No current story found for storage. Exiting.")
        state.status = "ERROR"
        return state

    print(f"  -> Indexing Story ID: {story.unique_story_id[:8]}...")
    
    # 1. Store to Structured Database (SQL)
    try:
        # save_story now inserts into both SQL tables and returns the story_id
        story_id_pk = db_service.save_story(story)
        story.db_id = story_id_pk
        print(f"  -> Stored to Structured DB with ID: {story_id_pk}")
        
    except Exception as e:
        print(f"❌ ERROR saving to Structured DB for {story.unique_story_id[:8]}: {e}")
        state.status = "ERROR"
        state.error_message = f"SQL DB Save Failed: {e}"
        return state

    # 2. Store to Vector Database (ChromaDB)
    try:
       # Metadata needed for RAG filtering
        metadata = {
            # "story_id": story.unique_story_id,
            "companies": ",".join(story.entities.companies), 
            "sectors": ",".join(story.entities.sectors),
            "regulators": ",".join(story.entities.regulators),
            
            "sentiment": story.sentiment,
            "db_id": story_id_pk, # Link back to the SQL record
        }
        
        # We assume vector_db_client has an add_document method for RAG indexing
        vector_id = vector_db_client.add_document(
            id=story.unique_story_id, 
            text=story.text, 
            metadata=metadata
        )
        state.vector_id = vector_id
        print(f"  -> Indexed vector in ChromaDB with ID: {vector_id}")
        
    except Exception as e:
        print(f"❌ ERROR indexing to Vector DB for {story.unique_story_id[:8]}: {e}")
        state.status = "ERROR"
        state.error_message = f"Vector DB Indexing Failed: {e}"
        return state
    
    # 3. Finalize
    state.status = "COMPLETED"
    state.current_story = None 
    print(f"\n--- Storage & Indexing Agent Finished. ---")
    
    return state