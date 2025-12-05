from langchain_core.prompts import ChatPromptTemplate
# We will use PydanticOutputParser if the model doesn't natively support StructuredOutput
from langchain_core.output_parsers import JsonOutputParser 

# Import all models from the single file
from financial_news_intel.core.models import (
    FinancialNewsState, 
    ConsolidatedStory, 
    ExtractedEntity, 
    ImpactedStock,
)
from financial_news_intel.core.llm_model import llm_service

def entity_extraction_agent(state: FinancialNewsState) -> FinancialNewsState:
    """
    Processes the unique ConsolidatedStory objects and uses the LLM 
    to extract structured entities and sentiment, updating the story objects in place.
    """
    print("\n--- Running Entity Extraction Agent ---")
    
    llm = llm_service.get_llm()
    # The parser is for the main structured output: ExtractedEntity
    entity_parser = JsonOutputParser(pydantic_object=ExtractedEntity)
    
    # 1. Define the Entity Extraction prompt
    entity_extraction_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert financial analyst. Your task is to accurately extract key entities (companies, sectors, regulators, people, events) from the provided news story. Ensure the output strictly conforms to the JSON schema. Do not hallucinate data; if an entity type is not present, return an empty list for that field. Focus only on financially relevant information."),
            ("user", "Extract structured entities from the following story.\n\nSTORY CONTENT:\n{story_content}\n\n{format_instructions}"),
        ]
    )
    # Note: For JSON output, sometimes it's more reliable to use llm.bind_tools or llm.with_structured_output 
    # if the LLM supports it, rather than chaining with JsonOutputParser, but we will stick to your chain for now.
    entity_chain = entity_extraction_prompt | llm | entity_parser 

    # 2. Define the Sentiment Extraction prompt (simple string output)
    sentiment_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Analyze the financial news story and assign a single sentiment label: 'Positive', 'Negative', or 'Neutral'. Respond only with the label, nothing else. Do not use quotes or punctuation."),
            ("user", "Determine the sentiment for this story:\n\n{story_content}"),
        ]
    )
    sentiment_chain = sentiment_prompt | llm

    # 3. Iterate and Process
    stories_processed = 0
    
    # Iterate over the list of ConsolidatedStory objects already in the state
    # for story in state.deduplication_groups:
    story = state.current_story
    print(f"  -> Processing Story ID: {story.unique_story_id[:8]}...")
    story_content = story.text
    
    # --- A. Entity Extraction ---
    try:
        # Invocation is fine here as the JsonOutputParser handles the AIMessage
        extracted_data = entity_chain.invoke({
            "story_content": story_content,
            "format_instructions": entity_parser.get_format_instructions(),
        })
        
        # The LLM output (dict) is converted to the Pydantic model
        story.entities = ExtractedEntity(**extracted_data)
        print(f"Entities: Companies={story.entities.companies}")

    except Exception as e:
        print(f"ERROR extracting entities for {story.unique_story_id[:8]}: {e}")
        print(f"{state.status}")
        # state.status = "ERROR"
        
    # --- B. Sentiment Extraction ---
    try:
        #  CRITICAL FIX: Access the .content attribute before using .strip()
        llm_response = sentiment_chain.invoke({"story_content": story_content})
        
        # Ensure llm_response is treated as an AIMessage, extract the string content, 
        # and then clean it up (remove quotes).
        sentiment_label = llm_response.content.strip().replace('"', '')
        
        story.sentiment = sentiment_label
        print(f"Sentiment: {sentiment_label}")
        
    except Exception as e:
        print(f"ERROR extracting sentiment for {story.unique_story_id[:8]}: {e}")
        # state.status = "ERROR"

    stories_processed += 1
            
    print(f"\n--- Entity Extraction Agent Finished. Updated {stories_processed} Story Records. ---")
    
    # The state is updated because we modified the objects *in* the list (state.deduplication_groups)
    return state







# from langchain_core.prompts import ChatPromptTemplate
# # Remove the two lines below:
# # We will use PydanticOutputParser if the model doesn't natively support StructuredOutput
# # from langchain_core.output_parsers import JsonOutputParser 
# # Add the following two lines:
# from langchain_core.messages import SystemMessage, HumanMessage 

# # Import all models from the single file
# from financial_news_intel.core.models import (
#     FinancialNewsState, 
#     ConsolidatedStory, 
#     ExtractedEntity, 
#     # ImpactedStock is not needed here
# )
# from financial_news_intel.core.llm_model import llm_service
# # ...

# def entity_extraction_agent(state: FinancialNewsState) -> FinancialNewsState:
#     """
#     Processes the current story using structured output to extract entities and sentiment.
#     """
#     print("\n--- Running Entity Extraction Agent ---")
    
#     llm = llm_service.get_llm()
#     story = state.current_story
    
#     if not story:
#         print("  -> ERROR: No current story found in state.")
#         return state

#     print(f"  -> Processing Story ID: {story.unique_story_id[:8]}...")
#     story_content = story.text

#     # --- A. Entity Extraction (Structured Output Fix) ---

#     # 1. Define the System Prompt
#     entity_system_message = SystemMessage(
#         content="You are an expert financial analyst. Your task is to accurately extract key entities (companies, sectors, regulators, people, events) from the provided news story. The output MUST strictly conform to the provided JSON schema. Do not hallucinate data; if an entity type is not present, return an empty list for that field. Focus only on financially relevant information."
#     )
    
#     # 2. Create the structured output chain (No prompt argument here due to Ollama bug)
#     structured_entity_chain = llm.with_structured_output(
#         ExtractedEntity, 
#         method="json_mode", # Ensure JSON mode is used
#     )

#     try:
#         state.status = "PROCESSING" 

#         # 3. Invoke the chain by passing the System and Human messages together
#         messages = [
#             entity_system_message,
#             HumanMessage(content=f"STORY CONTENT:\n{story_content}")
#         ]
        
#         # The invocation returns a clean, validated ExtractedEntity Pydantic object
#         extracted_data: ExtractedEntity = structured_entity_chain.invoke(messages)
        
#         story.entities = extracted_data
#         print(f"Entities: Companies={story.entities.companies}")

#     except Exception as e:
#         # 🌟 CRITICAL FIX: Ensure the graph exits cleanly on failure 🌟
#         print(f"❌ ERROR extracting entities for {story.unique_story_id[:8]}: {e}")
#         state.status = "ERROR"
#         return state 
        
#     # --- B. Sentiment Extraction ---
#     # 1. Define the Sentiment Extraction prompt
#     sentiment_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", "Analyze the financial news story and assign a single sentiment label: 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'. Respond ONLY with the label, nothing else. Do not use quotes, punctuation, or any introductory text."),
#             ("user", "Determine the sentiment for this story:\n\n{story_content}"),
#         ]
#     )
#     sentiment_chain = sentiment_prompt | llm
    
#     try:
#         llm_response = sentiment_chain.invoke({"story_content": story_content})
        
#         # Robustly clean and standardize the sentiment label
#         sentiment_label = llm_response.content.strip().upper().replace('"', '').replace("'", "")
        
#         story.sentiment = sentiment_label
#         print(f"Sentiment: {sentiment_label}")
        
#     except Exception as e:
#         print(f"⚠️ WARNING: ERROR extracting sentiment for {story.unique_story_id[:8]}: {e}")
#         story.sentiment = "UNCLEAR" 
    
#     # Success: Update status
#     state.status = "SUCCESS"
    
#     print("\n--- Entity Extraction Agent Finished. Updated 1 Story Record. ---")
    
#     return state