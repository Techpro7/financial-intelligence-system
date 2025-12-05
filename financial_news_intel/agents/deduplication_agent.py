from typing import Dict
from financial_news_intel.core.models import FinancialNewsState, RawArticle, ConsolidatedStory, ExtractedEntity
from financial_news_intel.core.embedding_model import get_embeddings
from financial_news_intel.core.vector_db import vector_db_client
from financial_news_intel.core.config import DEDUPLICATION_SIMILARITY_THRESHOLD
import uuid

def deduplication_agent(state: FinancialNewsState) -> FinancialNewsState:
    """
    Processes raw articles to identify unique stories, consolidates duplicates,
    and populates the 'deduplication_groups' field in the state.
    """
    print("--- Starting Deduplication Agent ---")
    
    # Use a mapping of the Vector DB ID (the ConsolidatedStory ID) to the actual story object
    current_unique_stories: Dict[str, ConsolidatedStory] = {}
    
    # 1. Process all raw articles in the batch
    for article in state.raw_articles:
        # A. Generate Embedding for the article content
        # We'll use the title and content for a slightly richer embedding vector
        text_to_embed = article.title + " " + article.content[:500] 
        article_embedding = get_embeddings([text_to_embed])[0]
        
        # B. Check Vector DB for duplicates
        similar_results = vector_db_client.check_for_duplicates(
            query_embedding=article_embedding
        )

        is_duplicate = False
        
        if similar_results:
            # Check the closest match against the threshold
            best_match = similar_results[0]
            
            if best_match['similarity'] >= DEDUPLICATION_SIMILARITY_THRESHOLD:
                print(f"  [DUPLICATE] Article {article.id} matches Story ID {best_match['id']} with similarity {best_match['similarity']:.3f}")
                is_duplicate = True
                
                # C. Handle Duplication (Add article to the existing ConsolidatedStory)
                # This requires retrieving the original story from the existing 'deduplication_groups'
                # or from the 'current_unique_stories' if it was found in this batch.
                
                # For simplicity in this first agent, we will only consolidate articles found
                # in the *current batch* that map to the *same* representative article in this batch.
                # A fully robust system would retrieve and update the story from a persistent DB.
                
                # However, for a clean LangGraph step, we'll focus on identifying the unique ones
                # and put the unique story (represented by the first article) into the groups.
                # Since we don't have a persistent DB for the story itself yet (only the vector ID),
                # we'll create a new story for every unique article found.

        
        if not is_duplicate:
            print(f"  [UNIQUE] Article {article.id} is a new unique story. Adding vector to DB.")
            
            # D. If unique, create a new ConsolidatedStory
            new_story = ConsolidatedStory(
                # Ensure the story text is the original article's content for the first stage
                text=article.content, 
                source_articles=[article],
                # Initialize entities structure
                entities=ExtractedEntity(),
            )
            
            # E. Add the new story's vector to the Vector DB
            # We index the title/snippet, but use the new_story.unique_story_id as the DB ID
            vector_db_client.add_article_embedding(
                article_id=new_story.unique_story_id,
                text=article.title + " " + article.content[:200],
                embedding=article_embedding
            )
            
            current_unique_stories[new_story.unique_story_id] = new_story

    # 2. Update the LangGraph State
    # Move the unique ConsolidatedStories to the 'deduplication_groups' queue
    state.deduplication_groups.extend(list(current_unique_stories.values()))
    state.raw_articles = [] # Clear the raw articles queue for the next batch
    
    # Update status for the next agent
    state.status = "DEDUPLICATION_COMPLETED"
    
    print(f"--- Deduplication Agent Finished. {len(current_unique_stories)} unique stories found. ---")
    return state