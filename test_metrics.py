import time
import os
import sys
from typing import Dict, List, Any

# Ensure the project root is in the path for internal imports to work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# UPDATED IMPORTS: Must use StockImpact and EntitySet to match your models.py
try:
    from financial_news_intel.core.models import FinancialNewsState, ConsolidatedStory, ImpactDirection
    from financial_news_intel.pipeline import financial_news_pipeline 
    from financial_news_intel.core.vector_db import vector_db_client

    # Import the Golden Dataset
    from financial_news_intel.tests.golden_data import RAW_INPUT_ARTICLES, GROUND_TRUTH_MAP
except ImportError as e:
    print(f"FATAL ERROR: Could not resolve internal imports required for testing. Check your path and file locations.")
    print(f"Details: {e}")
    sys.exit(1)


# --- UTILITY AND METRIC CALCULATION FUNCTIONS ---

def calculate_accuracy(actual: ConsolidatedStory, expected: ConsolidatedStory) -> Dict[str, float]:
    """Calculates accuracy metrics by comparing actual pipeline output to ground truth."""
    results = {}
    
    # --- 1. Sentiment Accuracy (Simple Match) ---
    # The gold data uses P, N, T (Enum values). The actual output should match this string value.
    results['Sentiment Accuracy'] = 1.0 if actual.sentiment == expected.sentiment else 0.0
    
    # --- 2. Entity F1 Score (Uses EntitySet fields) ---
    actual_entities = set(c.lower() for c in actual.entities.companies)
    expected_entities = set(c.lower() for c in expected.entities.companies)
    
    # Include regulators for a comprehensive check
    actual_entities.update(c.lower() for c in actual.entities.regulators)
    expected_entities.update(c.lower() for c in expected.entities.regulators)

    intersection = len(actual_entities.intersection(expected_entities))
    
    precision = intersection / len(actual_entities) if len(actual_entities) > 0 else 0.0
    recall = intersection / len(expected_entities) if len(expected_entities) > 0 else 0.0
    
    # F1 Score formula
    f1_denominator = (precision + recall)
    results['Entity F1 Score'] = 2 * (precision * recall) / f1_denominator if f1_denominator > 0 else 0.0
    
    # --- 3. Impact Direction Accuracy (Uses StockImpact fields) ---
    expected_impacts = {i.stock_ticker: i.impact_direction for i in expected.impacted_stocks}
    actual_impacts = {i.stock_ticker: i.impact_direction for i in actual.impacted_stocks}
    
    correct_count = 0
    total_expected = len(expected_impacts)
    
    for ticker, expected_dir in expected_impacts.items():
        # Comparison logic is robust for Enum string values
        if str(actual_impacts.get(ticker)) == str(expected_dir): 
            correct_count += 1
            
    results['Impact Direction Accuracy'] = correct_count / total_expected if total_expected > 0 else 1.0
        
    return results

# --- MAIN BENCHMARK FUNCTION ---
# (The rest of the function remains the same)

def run_performance_and_accuracy_test():
    """Runs the pipeline against the golden dataset and calculates metrics."""
    
    print("\n=================================================================")
    print("--- Starting LangGraph Performance & Accuracy Test ---")
    print("=================================================================")
    
    # 1. CLEANUP (Crucial for isolated testing)
    try:
        # Assuming vector_db_client is configured to point to ChromaDB
        vector_db_client.clear_collection() 
        print("✅ ChromaDB successfully reset for clean test execution.")
    except Exception as e:
        print(f"❌ ERROR during ChromaDB reset: {e}")

    # 2. INJECT GOLDEN INPUT (Bypassing live RSS feed fetch)
    initial_state = FinancialNewsState(
        status="TEST_START", # Triggers the TEST MODE check in ingestion_agent.py
        raw_news_data=RAW_INPUT_ARTICLES # Inject 30 raw articles
    )
    
    # 3. RUN PIPELINE
    print(f"\nStarting LangGraph run with {len(RAW_INPUT_ARTICLES)} injected articles...")
    start_time = time.time()
    
    # Run the compiled graph synchronously
    dict_after_full_run = financial_news_pipeline.invoke(
        initial_state,
        config={"recursion_limit": 500}
    )
    
    end_time = time.time()
    
    # 4. PERFORMANCE BENCHMARKING (Latency/Throughput)
    total_time = end_time - start_time
    final_state = FinancialNewsState(**dict_after_full_run)
    
    actual_stories: List[ConsolidatedStory] = final_state.deduplication_groups
    unique_stories_count = len(GROUND_TRUTH_MAP) 
    

    print("\n--- PERFORMANCE BENCHMARKS ---")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print(f"Total Input Articles: {len(RAW_INPUT_ARTICLES)}")
    print(f"Expected Unique Stories: {unique_stories_count}")
    
    if len(RAW_INPUT_ARTICLES) > 0:
        latency_per_article = total_time / len(RAW_INPUT_ARTICLES)
        print(f"Latency Per Input Article: {latency_per_article:.2f} seconds")
    
if __name__ == "__main__":
    run_performance_and_accuracy_test()