# financial_news_intel/pipeline.py (UPDATED CODE)

from langgraph.graph import StateGraph, END
from financial_news_intel.core.models import FinancialNewsState

# Import all required agents and the iterator
from financial_news_intel.agents.ingestion_agent import news_ingestion_agent # <-- NEW IMPORT
from financial_news_intel.agents.deduplication_agent import deduplication_agent
from financial_news_intel.agents.entity_agent import entity_extraction_agent
from financial_news_intel.agents.impact_agent import impact_stock_agent
from financial_news_intel.agents.iterator_agent import story_iterator_agent 
from financial_news_intel.agents.storage_agent import storage_index_agent

# --- Define the Workflow ---

# 1. Initialize the StateGraph
workflow = StateGraph(FinancialNewsState)

# 2. Add all nodes
workflow.add_node("ingestion", news_ingestion_agent)     
workflow.add_node("deduplicate", deduplication_agent)
workflow.add_node("iterator", story_iterator_agent)      
workflow.add_node("entity_extract", entity_extraction_agent)
workflow.add_node("impact_stock", impact_stock_agent)
workflow.add_node("storage_index", storage_index_agent)

# 3. Define the Edges

# Set the entry point 
workflow.set_entry_point("ingestion") # <-- ENTRY POINT 

# A. Ingestion -> Deduplication
workflow.add_edge("ingestion", "deduplicate") 

# B. Deduplication -> (Start Loop) OR (END)
# Start the loop if unique stories were found, by going to the iterator first.
workflow.add_conditional_edges(
    "deduplicate",
    # If the list is NOT empty, go to the Iterator
    lambda state: "iterator" if len(state.deduplication_groups)>0 else END,
    {
        "iterator": "iterator", 
        END: END,
    },
)

# C. Iterator -> Entity Extract 
# workflow.add_edge("iterator", "entity_extract")

workflow.add_conditional_edges(
    "iterator",
    # If there are no stories to process, go to END
    lambda state: "entity_extract" if state.current_story is not None else END,
    {
        "entity_extract": "entity_extract",
        END: END,
    },
)

# C. Entity Extraction -> (Impact) OR (Loop back on Error)
# If the entity agent failed, skip impact and go back to iterator for next story.
workflow.add_conditional_edges(
    "entity_extract",
    # Note: Use state.status to conditionally route
    lambda state: "impact_stock" if state.current_story is not None else END,
    {
        "impact_stock": "impact_stock", 
        # "iterator": "iterator", # Skips the failed story
        END: END,
    },
)

# D. Entity Extraction -> Stock Impact 
# workflow.add_edge("entity_extract", "impact_stock")

# E. Stock Impact -> (Loop Back) OR (END)
workflow.add_conditional_edges(
    "impact_stock",
    # If there are MORE stories left in the deduplication_groups list (the queue), 
    # loop back to the ITERATOR to fetch the NEXT story.
    lambda state: "storage_index" if state.status != "ERROR" else "iterator",
    {
        "storage_index": "storage_index", 
        "iterator": "iterator",
    },
)

workflow.add_conditional_edges(
    "storage_index",
    # If there are MORE stories left in the deduplication_groups list (the queue), 
    # loop back to the ITERATOR to fetch the NEXT story.
    lambda state: "iterator" if len(state.deduplication_groups)>0 else END,
    {
        "iterator": "iterator", 
        END: END,    
    }, 
)   

# 4. Compile the graph
financial_news_pipeline = workflow.compile()
print("LangGraph Pipeline compiled successfully with live ingestion enabled.")