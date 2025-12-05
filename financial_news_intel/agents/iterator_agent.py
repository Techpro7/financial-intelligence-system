# financial_news_intel/agents/iterator_agent.py

from financial_news_intel.core.models import FinancialNewsState

def story_iterator_agent(state: FinancialNewsState) -> FinancialNewsState:
    """
    Manages the queue of unique stories for batch processing.
    
    1. Pops the next unique story from the deduplication_groups list (the queue).
    2. Sets the popped story as the current_story for the next agent to process.
    3. Ensures the deduplication_groups list shrinks, which allows the main 
       LangGraph loop conditional edge to eventually trigger END.
    """
    
    # Check if there are any stories left in the queue
    if state.deduplication_groups:
        
        # 1. CRITICAL: Pop the next story from the beginning of the list (queue)
        next_story = state.deduplication_groups.pop(0)
        
        # 2. Set it as the current_story for the downstream agents (Entity, Impact)
        state.current_story = next_story
        
        # 3. Print status for debugging and visibility
        stories_remaining = len(state.deduplication_groups)
        print(f"--- Iterator: Setting current_story to ID: {next_story.unique_story_id[:8]}... ({stories_remaining} stories remaining)")
    else:
        # If the list is empty, clear current_story (shouldn't be strictly necessary if graph routing is correct)
        state.current_story = None 
        print("--- Iterator: Queue empty. Signaling end of batch.")
        
    # Return the updated state (the list is now shorter and current_story is set)
    return state