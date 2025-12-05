from pydantic.v1 import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum # <-- NEW: Import Enum
import uuid

# --- Helper Enums ---
class ImpactType(str, Enum):
    """The type of impact, aligning with problem statement requirements."""
    DIRECT = "direct"
    SECTOR = "sector"
    REGULATORY = "regulatory"


class ImpactDirection(str, Enum):
    """The directional impact of the news story on a specific stock."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    UNCLEAR = "UNCLEAR"

# --- Helper Data Structures ---

class RawArticle(BaseModel):
    """Represents a single raw news article fetched from a source."""
    # We must add an ID for tracking in the VectorDB and deduplication logic
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    source_url: str
    # The timestamp is often available but kept optional here
    timestamp: Optional[str] = None 

class ImpactedStock(BaseModel):
    """
    Structured data for a single impacted stock, resolved by the Impacted Stock Agent.
    Note: Fields updated to match the new agent's requirements.
    """
    company_name: str = Field(description="The formal name of the company.")
    stock_ticker: str = Field(description="The resolved stock market ticker symbol (e.g., TSLA, CAT).")
    impact_direction: ImpactDirection = Field(description="The expected directional impact (POSITIVE, NEGATIVE, NEUTRAL) based on the story's context.")

    # New required fields
    confidence: float = Field(description="Confidence score (0.0 to 1.0) based on the type of impact (1.0 for direct).")
    type: ImpactType = Field(description="The nature of the impact: 'direct', 'sector', or 'regulatory'.")


class ImpactedStockList(BaseModel):
    """A wrapper for the list of ImpactedStock objects."""
    impacts: List[ImpactedStock] = Field(description="A list of all resolved stock and sector impacts from the story.")


class ExtractedEntity(BaseModel):
    """Structured container for all entities extracted from the news story."""
    companies: List[str] = Field(default_factory=list)
    sectors: List[str] = Field(default_factory=list)
    regulators: List[str] = Field(default_factory=list)
    people: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)

class ConsolidatedStory(BaseModel):
    """The final, unique, and processed news item."""
    unique_story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str                                   # Consolidated text from duplicates
    # Store the Pydantic objects instead of just string IDs/URLs
    source_articles: List[RawArticle] = Field(default_factory=list) 
    entities: ExtractedEntity = Field(default_factory=ExtractedEntity)
    # FIELD CHANGE: Updated to use the new ImpactedStock schema
    impacted_stocks: List[ImpactedStock] = Field(default_factory=list) 
    sentiment: Optional[str] = None

    db_id: Optional[str] = Field(None, description="The primary key of this story in the Structured DB.")
    vector_id: Optional[str] = Field(None, description="The ID of this document in the Vector DB (Chroma).")
# --- LangGraph State Definition ---

class FinancialNewsState(BaseModel):
    """
    The central state object passed between the agents in the LangGraph workflow.
    """
    # 1. Ingestion Agent Input
    raw_articles: List[RawArticle] = Field(default_factory=list, description="A batch of raw articles (Pydantic objects).")

    # 2. Deduplication Agent Output
    # Groups of articles that form a unique story (list of ConsolidatedStory objects)
    deduplication_groups: List[ConsolidatedStory] = Field(default_factory=list, description="Unique stories awaiting further processing.")

    # 3. Processing Pipeline (used to process one unique story group at a time)
    current_story: Optional[ConsolidatedStory] = Field(None, description="The structured data for the story currently being processed.")

    # Error/Status Handling & Metrics
    status: str = Field("INITIALIZED", description="Current stage (e.g., 'INGESTING', 'DEDUPLICATING', 'COMPLETED').")
    error_message: Optional[str] = None
    
    # Metric for Evaluation
    dedup_accuracy_check: Optional[float] = None
    raw_news_data: List[Dict[str, Any]] = Field(default_factory=list, description="Temporary field for injecting raw article dicts in TEST mode.")

    # 4. Storage & Indexing Agent Output
    vector_id: Optional[str] = None
    db_id: Optional[str] = None
    
    class Config:
        # Allows fields like the LangChain/Ollama objects to be stored if needed later
        arbitrary_types_allowed = True

class QueryFilter(BaseModel):
    """
    Structured object defining the necessary search parameters extracted from a
    natural language user query.
    """
    # Use stock tickers or company names for precise lookup
    companies_or_tickers: List[str] = Field(
        default_factory=list,
        description="List of specific company names or stock tickers (e.g., TSLA, Reliance) mentioned in the query."
    )
    # Target sectors for filtering
    sectors: List[str] = Field(
        default_factory=list,
        description="List of industry sectors (e.g., Banking, Auto, IT) mentioned in the query."
    )
    # Desired directional impact for filtering the news
    impact_direction: Optional[ImpactDirection] = Field(
        None,
        description="The required stock impact direction if specified (e.g., 'POSITIVE', 'NEGATIVE', 'NEUTRAL'). Set to None if not specified."
    )
    # The clean, rephrased query string for semantic search
    search_query: str = Field(
        description="The clean, simplified, non-filter part of the user query for semantic search (e.g., 'latest news about dividend payments').",
        alias="query"
    )