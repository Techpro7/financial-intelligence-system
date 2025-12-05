
# from financial_news_intel.core.vector_db import vector_db_client
# from financial_news_intel.core.db_service import db_service
# from financial_news_intel.core.models import QueryFilter
# from financial_news_intel.llm.llm_service import llm_with_structured_output, llm_simple_completion
# from typing import List, Dict, Any
# import sys
# from langchain_core.messages import SystemMessage, HumanMessage

# # --- Helper Functions ---
# def _extract_query_filters(query: str) -> QueryFilter:
#     """
#     Uses the LLM to extract structured search filters from the user's natural language query.
#     """
#     print("-> Step 1: Extracting query intent and filters...")

#     # 1. Define the System Prompt
#     system_prompt = (
#         "You are an expert filter extraction system. Your sole task is to analyze the user's financial news query "
#         "and extract specific search parameters into a JSON object that strictly adheres to the provided schema. "
#         "You MUST analyze the query to fill ALL REQUIRED fields in the schema. "
#         "The 'search_query' field is MANDATORY and must contain the core, simplified search phrase, "
#         "even if other fields are filled. For company/sector/impact fields, if nothing specific is mentioned, use an empty list or None."
#     )
    
#     # 2. Configure the LLM for structured output (using the simple LLM chain)
#     structured_llm = llm_simple_completion.with_structured_output(
#         schema=QueryFilter,
#         method="json_mode" # Essential for Ollama/Llama models
#     )
    
#     # 3. Create the messages list
#     messages = [
#         SystemMessage(content=system_prompt),
#         HumanMessage(content=f"User Query to Analyze: {query}")
#     ]
    
#     # 4. Invoke the structured LLM with the strong prompt
#     try:
#         response: QueryFilter = structured_llm.invoke(messages)
#         return response
#     except Exception as e:
#         # Re-raise the error to be caught by the main agent function for clearer logging
#         print(f"Error during filter extraction: {e}")
#         raise e
    
# def _prepare_chroma_filter(query_filters: QueryFilter) -> Dict[str, Any]:
#     """
#     Converts the Pydantic QueryFilter into ChromaDB's required metadata filter dictionary.
    
#     CRITICAL FIX: Uses the explicit $eq operator for sentiment, as required by ChromaDB
#     for comparisons.
#     """
#     chroma_filter = {}
    
#     # 1. Sentiment filter
#     # Check if impact_direction is set AND it's not the 'ANY' placeholder
#     if query_filters.impact_direction and query_filters.impact_direction.value.upper() != "ANY":
#         # The sentiment is stored as a simple string (e.g., "POSITIVE", "NEGATIVE")
#         # The filter must be wrapped in an operator (e.g., "$eq")
#         chroma_filter['sentiment'] = {"$eq": query_filters.impact_direction.value}
    
#     # NOTE on Entity Filtering: Since companies/sectors are stored as comma-separated 
#     # strings and not lists (due to your ChromaDB version constraint), strict metadata 
#     # filtering by entity name is difficult/unreliable. We rely on the semantic search 
#     # query and the final LLM synthesis (Step 4) to handle entity relevance.
    
#     return chroma_filter # Returns {} if no valid sentiment filter is applied


# # --- Main Agent Function ---


# def query_processing_agent(user_query: str) -> str:
#     """
#     Pure retrieval-based Query Agent.
#     No LLM summarization. Returns all raw articles from SQL DB
#     that match the vector search results.
#     """

#     try:
#         # 1. Extract Filters
#         filters = _extract_query_filters(user_query)
#         print(f"   -> Extracted Filters: Sentiment={filters.impact_direction.value if filters.impact_direction else 'Any'}, Query='{filters.search_query}'")

#         # 2. Prepare Chroma Filter
#         chroma_filter = _prepare_chroma_filter(filters)
#         print(f"   -> Chroma Filter: {chroma_filter}")

#         # 3. Hybrid Search (Vector + Filter)
#         print(f"-> Step 2: Retrieving context from Vector DB...")
#         retrieved_docs = vector_db_client.search(
#             query=filters.search_query,
#             chroma_filter=chroma_filter,
#             top_k=5,
#         )

#         if not retrieved_docs:
#             return "No relevant news articles found for your query."

#         print(f"   -> Found {len(retrieved_docs)} possible matches.")

#         # 4. Fetch full stories from SQL
#         print("-> Step 3: Fetching full stories from SQL...")
#         matched_stories = []

#         for doc in retrieved_docs:
#             story_id = doc.get("metadata", {}).get("db_id")
#             if not story_id:
#                 print(f"   -> Missing db_id for document {doc['id']}, skipping.")
#                 continue

#             story = db_service.fetch_full_story_details(story_id)
#             if story:
#                 matched_stories.append(story)

#         if not matched_stories:
#             return "No SQL-stored stories matched your search results."

#         print(f"-> Retrieved {len(matched_stories)} final stories.")

#         # 5. Format raw output (NO LLM)

#         def format_story(idx: int, s: Dict[str, Any]) -> str:
#             # Clean companies JSON-like string
#             companies = s["companies"]
#             if isinstance(companies, str):
#                 companies = companies.strip("[]").replace("'", "").strip()

#             # Format impacts
#             if s["impacts"]:
#                 impacts = "\n".join([
#                     f"  - {imp['company_name']} ({imp['stock_ticker']}): "
#                     f"{imp['impact_direction']} [{imp['impact_type']}] "
#                     f"(confidence={imp['confidence']})"
#                     for imp in s["impacts"]
#                 ])
#             else:
#                 impacts = "  - None"

#             return f"""
# === STORY {idx} ===
# ID: {s['story_id']}
# Sentiment: {s['sentiment']}
# Companies: {companies}

# Impacts:
# {impacts}

# Article:
# {s['text']}
# ----------------------------------------
# """
#         final_output = "\n".join([
#         format_story(i + 1, s)
#         for i, s in enumerate(matched_stories)
#         ])

#         return final_output.strip()

#     except Exception as e:
#         return f"Query Agent Error: {e}"


from financial_news_intel.core.vector_db import vector_db_client
from financial_news_intel.core.db_service import db_service
from financial_news_intel.core.models import QueryFilter
from financial_news_intel.llm.llm_service import llm_simple_completion
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage


# ----------------------------------------
# 1. Extract Query Filters
# ----------------------------------------
def _extract_query_filters(query: str) -> QueryFilter:
    print("-> Step 1: Extracting query intent and filters...")

    system_prompt = (
        "You are an expert filter extraction system. Extract structured search filters "
        "strictly following the schema. The 'search_query' MUST always be filled."
    )

    structured_llm = llm_simple_completion.with_structured_output(
        schema=QueryFilter,
        method="json_mode"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User Query to Analyze: {query}")
    ]

    try:
        response: QueryFilter = structured_llm.invoke(messages)
        return response
    except Exception as e:
        print(f"Error during filter extraction: {e}")
        raise e


# ----------------------------------------
# 2. Prepare Chroma Filters
# ----------------------------------------
def _prepare_chroma_filter(query_filters: QueryFilter) -> Dict[str, Any]:
    chroma_filter = {}

    if query_filters.impact_direction and query_filters.impact_direction.value.upper() != "ANY":
        chroma_filter["sentiment"] = {"$eq": query_filters.impact_direction.value}

    return chroma_filter


# ----------------------------------------
# 3. Main Query Processing Agent (Updated)
# ----------------------------------------
def query_processing_agent(user_query: str) -> Dict[str, Any]:
    """
    Returns a JSON response:
    {
        "status": "SUCCESS",
        "count": <int>,
        "results": [ { story }, ... ]
    }
    """

    try:
        # STEP 1: Extract filters
        filters = _extract_query_filters(user_query)
        print(f"   -> Extracted Filters: {filters}")

        # STEP 2: Chroma metadata filter
        chroma_filter = _prepare_chroma_filter(filters)
        print(f"   -> Chroma Filter: {chroma_filter}")

        # STEP 3: Vector search
        print("-> Step 2: Retrieving context from Vector DB...")
        retrieved_docs = vector_db_client.search(
            query=filters.search_query,
            chroma_filter=chroma_filter,
            top_k=5
        )

        if not retrieved_docs:
            return {
                "status": "SUCCESS",
                "count": 0,
                "results": []
            }

        print(f"   -> Found {len(retrieved_docs)} possible matches.")

        # STEP 4: Fetch SQL stories
        matched_stories = []
        print("-> Step 3: Fetching full stories from SQL...")

        for doc in retrieved_docs:
            story_id = doc.get("metadata", {}).get("db_id")
            if not story_id:
                continue

            story = db_service.fetch_full_story_details(story_id)
            if story:
                matched_stories.append(story)

        if not matched_stories:
            return {
                "status": "SUCCESS",
                "count": 0,
                "results": []
            }

        print(f"-> Retrieved {len(matched_stories)} final stories.")

        # STEP 5: Convert raw DB rows to structured JSON
        json_results = []

        for s in matched_stories:
            # companies is stored as "['A', 'B']" string → convert to list
            companies_raw = s["companies"]
            if isinstance(companies_raw, str):
                companies = (
                    companies_raw.strip("[]")
                    .replace("'", "")
                    .split(",")
                )
                companies = [c.strip() for c in companies if c.strip()]
            else:
                companies = companies_raw

            # impacts list
            impacts = []
            for imp in s["impacts"]:
                impacts.append({
                    "company_name": imp["company_name"],
                    "stock_ticker": imp["stock_ticker"],
                    "impact_direction": imp["impact_direction"],
                    "impact_type": imp["impact_type"],
                    "confidence": imp["confidence"]
                })

            json_results.append({
                "story_id": s["story_id"],
                "sentiment": s["sentiment"],
                "companies": companies,
                "impacts": impacts,
                "article": s["text"]
            })

        # FINAL JSON OUTPUT
        return {
            "status": "SUCCESS",
            "count": len(json_results),
            "results": json_results
        }

    except Exception as e:
        print(f"[Query Agent Error]: {e}")
        return {
            "status": "ERROR",
            "count": 0,
            "results": []
        }
