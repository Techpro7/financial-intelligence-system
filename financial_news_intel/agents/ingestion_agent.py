# import feedparser
# import time
# import uuid
# from typing import Dict, Any, List
# from financial_news_intel.core.models import FinancialNewsState, RawArticle

# # --- RSS Feed URLs to Scrape (Based on Problem Statement) ---
# RSS_FEEDS = [
#     # General news/markets
#     "https://b2b.economictimes.indiatimes.com/rss/topstories",
#     "https://www.livemint.com/rss/markets",
#     "http://www.business-standard.com/rss/home_page_top_stories.rss",
#     "https://www.financialexpress.com/feed/",
#     # Note: Feeds for MoneyControl/Trade Brains were generalized to similar available feeds
# ]

# def fetch_articles_from_rss(feeds: list) -> list:
#     """
#     Fetches articles from a list of RSS feeds, extracts key fields, and 
#     formats them as a list of dictionaries.
#     """
#     articles_data = []
    
#     for url in feeds:
#         print(f"  -> Fetching from: {url}")
#         try:
#             feed = feedparser.parse(url)
            
#             for entry in feed.entries:
#                 title = entry.title if hasattr(entry, 'title') else "No Title"
#                 # Use summary or description for the main content snippet
#                 content = entry.summary if hasattr(entry, 'summary') else entry.get('description', '')
#                 source_url = entry.link if hasattr(entry, 'link') else url
                
#                 # Check for minimum content length (e.g., > 100 characters) to filter noise
#                 if title and content and len(content) > 100:
                    
#                     # Generate a unique ID for the RawArticle before Pydantic validation
#                     article_id = str(uuid.uuid4())
                    
#                     articles_data.append({
#                         "id": article_id, 
#                         "title": title.strip(),
#                         "content": content.strip(),
#                         "source_url": source_url,
#                         # Use published date if available, otherwise None
#                         "timestamp": entry.published if hasattr(entry, 'published') else None 
#                     })
            
#             # Brief pause to be respectful of RSS feed servers
#             time.sleep(1) 
            
#         except Exception as e:
#             print(f"  -> Error fetching {url}: {e}")

#     return articles_data

# def news_ingestion_agent(state: FinancialNewsState) -> FinancialNewsState:
#     """
#     Agent 1: Fetches news articles from live RSS feeds, converts them into 
#     RawArticle Pydantic objects, and updates the state.
#     """
#     print("--- Starting News Ingestion Agent (Live RSS Fetch) ---")
    
#     # 1. Fetch data from RSS feeds
#     raw_articles_data = fetch_articles_from_rss(RSS_FEEDS)
#     raw_articles_pydantic: List[RawArticle] = []
    
#     if not raw_articles_data:
#         print("  -> WARNING: No articles fetched from RSS feeds.")
#         state.raw_articles = []
#         state.status = "INGESTION_COMPLETED_EMPTY"
#         return state
        
#     # 2. Convert raw dictionaries to Pydantic models
#     try:
#         for article_data in raw_articles_data:
#             # Validate and convert the dictionary to the RawArticle model
#             raw_article = RawArticle(**article_data)
#             raw_articles_pydantic.append(raw_article)
        
#         print(f"  -> Successfully converted {len(raw_articles_pydantic)} articles to RawArticle objects.")
        
#     except Exception as e:
#         error_msg = f"ERROR during Pydantic validation: {e}"
#         print(error_msg)
#         state.error_message = error_msg
#         state.status = "INGESTION_ERROR"
#         return state
    
#     # 3. Update the LangGraph State
#     state.raw_articles = raw_articles_pydantic
#     state.status = "INGESTION_COMPLETED"
    
#     return state

import feedparser
import time
import uuid
from typing import Dict, Any, List
# Assuming RawArticle is defined in financial_news_intel.core.models
from financial_news_intel.core.models import FinancialNewsState, RawArticle 

# --- RSS Feed URLs to Scrape (Based on Problem Statement) ---
RSS_FEEDS = [
    "https://b2b.economictimes.indiatimes.com/rss/topstories",
    "https://www.livemint.com/rss/markets",
    "http://www.business-standard.com/rss/home_page_top_stories.rss",
    "https://www.financialexpress.com/feed/",
]

def fetch_articles_from_rss(feeds: list) -> list:
    """
    Fetches articles from a list of RSS feeds, extracts key fields, and 
    formats them as a list of dictionaries.
    """
    articles_data = []
    
    for url in feeds:
        print(f"  -> Fetching from: {url}")
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                title = entry.title if hasattr(entry, 'title') else "No Title"
                content = entry.summary if hasattr(entry, 'summary') else entry.get('description', '')
                source_url = entry.link if hasattr(entry, 'link') else url
                
                if title and content and len(content) > 100:
                    article_id = str(uuid.uuid4())
                    
                    articles_data.append({
                        "id": article_id, 
                        "title": title.strip(),
                        "content": content.strip(),
                        "source_url": source_url,
                        "timestamp": entry.published if hasattr(entry, 'published') else None 
                    })
            
            time.sleep(1) 
            
        except Exception as e:
            print(f"  -> Error fetching {url}: {e}")

    return articles_data

def news_ingestion_agent(state: FinancialNewsState) -> FinancialNewsState:
    """
    Agent 1: Fetches news articles or loads test data, converts them into 
    RawArticle Pydantic objects, and updates the state.
    """
    print("--- Starting News Ingestion Agent ---")
    
    raw_articles_data = []

    # --- 1. CRITICAL TEST MODE CHECK ---
    # We assume 'raw_news_data' is the temporary field used by the test script 
    # to inject the list of dictionaries from golden_data.py
    if hasattr(state, 'raw_news_data') and state.raw_news_data and state.status == "TEST_START":
        print(f"✅ Running in TEST MODE. Processing {len(state.raw_news_data)} injected articles.")
        raw_articles_data = state.raw_news_data
        
        # Clear the temporary field to prevent re-injection in recursive calls
        state.raw_news_data = [] 
    
    else:
        # --- LIVE MODE ---
        print("Agent: Running in LIVE MODE. Fetching live RSS feeds...")
        raw_articles_data = fetch_articles_from_rss(RSS_FEEDS)


    raw_articles_pydantic: List[RawArticle] = []
    
    if not raw_articles_data:
        print("  -> WARNING: No articles processed.")
        state.raw_articles = []
        state.status = "INGESTION_COMPLETED_EMPTY"
        return state
        
    # 2. Convert raw dictionaries to Pydantic models, mapping fields if necessary
    try:
        for article_data in raw_articles_data:
            
            # Map test data fields to Pydantic model fields (ID, Content, URL, Timestamp)
            mapped_data = {
                # ID: Use injected ID if available, otherwise generate a new one
                "id": article_data.get("id", str(uuid.uuid4())), 
                "title": article_data.get("title", "No Title"),
                
                # CONTENT: Map "summary" (from golden_data) to "content"
                "content": article_data.get("content", article_data.get("summary", "")), 
                
                # SOURCE_URL: Map "link" (from golden_data) to "source_url"
                "source_url": article_data.get("source_url", article_data.get("link", "")), 
                
                # TIMESTAMP: Map "published_at" (from golden_data) to "timestamp"
                "timestamp": article_data.get("timestamp", article_data.get("published_at", None)), 
            }
            
            # Validate and convert the mapped dictionary to the RawArticle model
            raw_article = RawArticle(**mapped_data)
            raw_articles_pydantic.append(raw_article)
        
        print(f"  -> Successfully converted {len(raw_articles_pydantic)} articles to RawArticle objects.")
        
    except Exception as e:
        error_msg = f"ERROR during Pydantic validation: {e}"
        print(error_msg)
        state.error_message = error_msg
        state.status = "INGESTION_ERROR"
        return state
    
    # 3. Update the LangGraph State
    state.raw_articles = raw_articles_pydantic
    state.status = "INGESTION_COMPLETED"
    
    return state