from langchain_core.tools import tool
from typing import Dict

# Mock Ticker Database: Simulating an external API/database lookup
# This handles common names and non-standard symbols (e.g., TSLA vs. 'Tesla')
TICKER_DB: Dict[str, str] = {
    "Jindal Steel and Power": "JSPL.NS", 
    "Jindal Steel": "JSPL.NS",
    "Omaxe": "OMAXE.NS",
    "Caterpillar": "CAT", 
    "Caterpillar Inc.": "CAT",
    "Tesla": "TSLA",
    "Apple": "AAPL"
}

@tool
def resolve_company_ticker(company_name: str) -> str:
    """
    Looks up the official stock ticker symbol for a given company name 
    by querying an external financial database. Returns 'NOT_FOUND' if the ticker 
    cannot be reliably resolved. This tool must be called for every company mentioned.
    """
    normalized_name = company_name.strip()
    
    # Simple, case-insensitive fuzzy lookup
    # This allows the LLM to try variations (e.g., "Caterpillar" vs. "Caterpillar Inc.")
    for name, ticker in TICKER_DB.items():
        if normalized_name.lower() in name.lower() or name.lower() in normalized_name.lower():
             return ticker
             
    # Fallback when the ticker is not in our mock database
    return "NOT_FOUND"

# List of all tools to be bound to the LLM
ALL_TOOLS = [resolve_company_ticker]