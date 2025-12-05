import os
import shutil
import time
from financial_news_intel.core.models import FinancialNewsState, ConsolidatedStory
from financial_news_intel.core.config import CHROMA_DB_PATH
from financial_news_intel.pipeline import financial_news_pipeline 
from financial_news_intel.core.vector_db import vector_db_client

# --- CONFIGURATION & UTILITY ---

def run_full_pipeline_test():
    """
    Tests the full LangGraph flow: Ingestion (Live RSS) -> Deduplication -> Entity -> Impact (with loop).
    
    This version uses only print statements to show flow and output, without assertions.
    """
    
    print("\n=================================================================")
    print("--- Starting Full LangGraph Pipeline Test (Live RSS Flow Check) ---")
    print("=================================================================")
    
    print(f"⚠️ Resetting remote ChromaDB via client.clear_collection() to ensure unique articles are processed...")
    try:
        # 🌟 USE THE CORRECT METHOD NAME: clear_collection()
        vector_db_client.clear_collection() 
        print("✅ ChromaDB successfully reset and collection re-initialized.")
    except Exception as e:
        print(f"❌ FATAL ERROR during ChromaDB reset: {e}")
        # We must exit if we can't clean the DB, as the test is useless otherwise.
        # return
    # 2. Initialize the State
    initial_state = FinancialNewsState(status="STARTING")
    
    # 3. Run the entire graph
    print("\nStarting LangGraph run...")
    print("-> Agent 1: News Ingestion Agent will now fetch live RSS feeds.")
    
    start_time = time.time()
    
    # Invoke the compiled LangGraph pipeline
    dict_after_full_run = financial_news_pipeline.invoke(initial_state,config={"recursion_limit": 150})
    
    end_time = time.time()
    
    print(f"\n=================================================================")
    print(f"LangGraph run completed in {end_time - start_time:.2f} seconds.")
    # print(f"Final State Status: {dict_after_full_run.get('status', 'UNKNOWN')}")
    # 4. Validation and Check Results
    state_after_full_run = FinancialNewsState(**dict_after_full_run)
    
    print("\n--- Final State Validation ---")
    
    # Check 1: Ingestion and Deduplication flow
    deduplication_groups = state_after_full_run.deduplication_groups
    
    if len(deduplication_groups) > 0:
        print(f"✅ Flow Check: Successfully moved from Ingestion -> Deduplication.")
        print(f"   -> Found {len(deduplication_groups)} unique stories for processing.")
    else:
        print("⚠️ Flow Check: Deduplication found 0 unique stories. May be due to empty live RSS feeds, but the flow finished.")

    # Check 2: Looping and Final Processing Success
    processed_story: ConsolidatedStory = state_after_full_run.current_story
    
    if processed_story:
        print("\n✅ Loop Check: The pipeline successfully completed the processing loop.")
        print(f"   -> Final Status: {state_after_full_run.status}")
        
        # Check 3: Full Enrichment on the last processed story
        print(f"\n--- Last Processed Story Details ({processed_story.unique_story_id[:8]}) ---")
        
        # Sentiment Check
        print(f"   -> Sentiment (Entity Agent Output): {processed_story.sentiment or 'N/A'}")

        # Entities Check
        print(f"   -> Entities (Entity Agent Output): {len(processed_story.entities.companies)} companies extracted.")

        # Impacted Stocks Check (Final Agent Output)
        if processed_story.impacted_stocks:
            print(f"   -> Impacts (Stock Impact Agent Output): {len(processed_story.impacted_stocks)} stocks/sectors analyzed.")
            
            # Print details of the first impact for quick verification
            sample_impact = processed_story.impacted_stocks[0]
            # print(f"      -> Sample Ticker: '{sample_impact.symbol}'")
            print(f"      -> Sample Ticker: '{sample_impact.stock_ticker}'")
            print(f"      -> Sample Type: '{sample_impact.type.value}'")
            print(f"      -> Sample Confidence: {sample_impact.confidence:.2f}")
        else:
            print("   -> Impacts: 0 stocks/sectors analyzed or extraction failed.")

    else:
        print("❌ Final Story Check: current_story is None. The processing loop might not have run or was empty.")

    print("\n=================================================================")
    print("Full pipeline flow check complete.")


if __name__ == "__main__":
    run_full_pipeline_test()