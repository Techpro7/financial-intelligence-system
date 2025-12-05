# financial_news_intel/scheduler/ingestion_worker.py
import time
from datetime import datetime
import random 
import os
import sys

# Ensure the project root is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the necessary components
from financial_news_intel.pipeline import financial_news_pipeline # Your compiled graph
from financial_news_intel.core.models import FinancialNewsState
from financial_news_intel.core.vector_db import vector_db_client # To clear the DB for testing/fresh runs

def run_ingestion_graph():
    """
    Executes the full LangGraph ingestion pipeline.
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{now}] --- STARTING NEWS INGESTION PIPELINE ---")
    
    # Optional: Clear the DB collection before a fresh ingestion run
    # This is useful for hackathons/testing to ensure old data doesn't interfere.
    try:
        # WARNING: Only run this if you intend to wipe all indexed data before each run!
        # vector_db_client.clear_collection() 
        # print(f"[{now}] VectorDB collection cleared (if enabled).")
        pass
    except Exception as e:
        print(f"[{now}] WARNING: Could not clear VectorDB collection: {e}")
        # Continue ingestion attempt
    
    # 1. Initialize the State (The ingestion agent will fetch news articles)
    initial_state = FinancialNewsState(status="STARTING")
    
    start_time = time.time()
    
    # 2. Invoke the compiled LangGraph pipeline
    # Use a high recursion limit to allow the loop (iterator) to process many stories
    try:
        final_state_dict = financial_news_pipeline.invoke(
            initial_state,
            config={"recursion_limit": 150} 
        )
        final_state = FinancialNewsState(**final_state_dict)
        
        end_time = time.time()
        
        # Log success and statistics
        unique_stories_count = len(final_state.deduplication_groups)
        print(f"[{now}] LangGraph Pipeline finished successfully in {end_time - start_time:.2f} seconds.")
        print(f"[{now}] -> Total unique stories found and processed: {unique_stories_count}")
        print(f"[{now}] --- INGESTION COMPLETE ---")
        
    except Exception as e:
        print(f"[{now}] ❌ CRITICAL: LangGraph Pipeline failed to run: {e}")
        print(f"[{now}] --- INGESTION FAILED ---")

# --- Worker Loop ---
def start_worker(interval_seconds: int = 1000): # Default to 1000 seconds
    """
    Runs the ingestion pipeline repeatedly at the specified interval.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ingestion Worker started. Pipeline will run every {interval_seconds} seconds.")
    
    # Run immediately on startup
    run_ingestion_graph() 
    
    while True:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Waiting for {interval_seconds} seconds until next run...")
        time.sleep(interval_seconds)
        try:
            run_ingestion_graph()
        except Exception as e:
            # This catch is mainly for unexpected outer loop failures
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Worker loop encountered an error: {e}. Continuing.")

if __name__ == "__main__":
    # Start the worker, running every 1000 seconds
    start_worker(interval_seconds=1000)