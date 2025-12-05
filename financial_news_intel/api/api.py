from fastapi import FastAPI
from financial_news_intel.agents.query_agent import query_processing_agent
from financial_news_intel.api.models import QueryRequest, QueryResponse

# Initialize the FastAPI app
app = FastAPI(
    title="Financial News Intelligence API",
    description="API for the Context-Aware Query System.",
    version="1.0.0"
)

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Accepts a natural language query and returns structured financial intelligence.
    """
    print(f"\n[API] Received query: {request.query}")

    try:
        # The Query Agent now returns a dict:
        # { "status": "...", "count": int, "results": [ ... ] }
        results = query_processing_agent(request.query)

        # Build the response model
        return QueryResponse(
            query=request.query,
            status=results["status"],
            count=results["count"],
            results=results["results"]
        )

    except Exception as e:
        print(f"[API Error] Query processing failed: {e}")

        # Return graceful error response
        return QueryResponse(
            query=request.query,
            status="ERROR",
            count=0,
            results=[]
        )

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "Query API"}
