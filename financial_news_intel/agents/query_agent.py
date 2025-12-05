
from financial_news_intel.core.vector_db import vector_db_client
from financial_news_intel.core.db_service import db_service
from financial_news_intel.core.models import QueryFilter
from typing import Dict, Any, List


# ----------------------------------------
# 1. Extract Query Filters (NO LLM)
# ----------------------------------------
def _extract_query_filters(query: str) -> QueryFilter:
    """
    PURE deterministic filter extraction.
    No LLM, no hallucinations, no JSON errors.

    We only use `search_query` for RAG search.
    All other filter fields are optional.
    """
    return QueryFilter(
        search_query=query,
        companies_or_tickers=[],
        sectors=[],
        impact_direction=None
    )


# ----------------------------------------
# 2. Prepare Chroma Filters
# ----------------------------------------
def _prepare_chroma_filter(query_filters: QueryFilter) -> Dict[str, Any]:
    """
    Converts QueryFilter → ChromaDB metadata filters.
    Only sentiment is supported for now.
    """
    chroma_filter = {}

    if query_filters.impact_direction and query_filters.impact_direction.value.upper() != "ANY":
        chroma_filter["sentiment"] = {"$eq": query_filters.impact_direction.value}

    return chroma_filter


# ----------------------------------------
# 3. Main Query Processing Agent
# ----------------------------------------
def query_processing_agent(user_query: str) -> Dict[str, Any]:
    """
    Returns a JSON response:
    {
        "status": "SUCCESS",
        "count": <int>,
        "results": [story, story, ...]
    }

    No LLM used. Pure RAG pipeline:
    - vector DB → top matches
    - SQL → full story information
    """
    try:
        # STEP 1: Extract filters (NO LLM)
        filters = _extract_query_filters(user_query)
        print(f"[QueryAgent] Extracted Filters → {filters}")

        # STEP 2: Construct Chroma metadata filter (optional sentiment)
        chroma_filter = _prepare_chroma_filter(filters)
        print(f"[QueryAgent] Chroma Filter: {chroma_filter}")

        # STEP 3: Vector search
        print("[QueryAgent] Retrieving documents from vector DB...")
        retrieved_docs = vector_db_client.search(
            query=filters.search_query,
            chroma_filter=chroma_filter,
            top_k=7,
        )

        if not retrieved_docs:
            return {
                "status": "SUCCESS",
                "count": 0,
                "results": []
            }

        print(f"[QueryAgent] Vector matches → {len(retrieved_docs)}")

        # STEP 4: Fetch SQL details
        matched_stories = []
        print("[QueryAgent] Fetching full SQL stories...")

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

        print(f"[QueryAgent] Final matched stories → {len(matched_stories)}")

        # STEP 5: Format structured JSON
        results_json = []
        for s in matched_stories:

            # ----- Clean companies list -----
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

            # ----- Impacts -----
            impacts = []
            for imp in s["impacts"]:
                impacts.append({
                    "company_name": imp["company_name"],
                    "stock_ticker": imp["stock_ticker"],
                    "impact_direction": imp["impact_direction"],
                    "impact_type": imp["impact_type"],
                    "confidence": imp["confidence"],
                })

            # ----- Final story JSON -----
            results_json.append({
                "story_id": s["story_id"],
                "sentiment": s["sentiment"],
                "companies": companies,
                "impacts": impacts,
                "article": s["text"],
            })

        # Final output
        return {
            "status": "SUCCESS",
            "count": len(results_json),
            "results": results_json
        }

    except Exception as e:
        print(f"[QueryAgent ERROR] {e}")
        return {
            "status": "ERROR",
            "count": 0,
            "results": []
        }
