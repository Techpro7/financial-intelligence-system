from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    """Model for the incoming user query."""
    query: str

class ImpactModel(BaseModel):
    company_name: str
    stock_ticker: str
    impact_direction: str
    impact_type: str
    confidence: float

class StoryModel(BaseModel):
    story_id: str
    sentiment: str
    companies: List[str]
    impacts: List[ImpactModel]
    article: str

class QueryResponse(BaseModel):
    query: str
    status: str
    count: int
    results: List[StoryModel]
