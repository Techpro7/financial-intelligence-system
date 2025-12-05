import feedparser
import json
import time
import os # <-- CORRECTED: Added the missing import for the OS module

# --- RSS Feed URLs to Scrape ---
RSS_FEEDS = [
    "https://b2b.economictimes.indiatimes.com/rss/topstories",
    "https://www.livemint.com/rss/markets",
    "http://www.business-standard.com/rss/home_page_top_stories.rss",
    "https://www.financialexpress.com/feed/",
]

def fetch_articles_from_rss(feeds: list) -> list:
    """Fetches articles from a list of RSS feeds and formats them."""
    
    mock_articles = []
    
    for url in feeds:
        print(f"Fetching from: {url}")
        try:
            # Parse the RSS feed
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                # Basic data extraction
                title = entry.title if hasattr(entry, 'title') else "No Title"
                # Use summary or description for the main content snippet
                content = entry.summary if hasattr(entry, 'summary') else entry.get('description', '')
                source_url = entry.link if hasattr(entry, 'link') else url
                
                # Check for minimum content length to ensure useful articles
                if title and content and len(content) > 50:
                    mock_articles.append({
                        "title": title.strip(),
                        "content": content.strip(),
                        "source_url": source_url,
                    })
            
            # Wait briefly to avoid hammering the server
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    return mock_articles

if __name__ == "__main__":
    
    # 1. Fetch data from RSS feeds
    fetched_data = fetch_articles_from_rss(RSS_FEEDS)
    
    # 2. Add manual duplicates for reliable deduplication testing
    manual_duplicates = [
        {
            "title": "RBI hikes interest rates by 25 basis points to combat inflation.",
            "content": "The Reserve Bank of India announced today a 25 basis point increase in the key repo rate, bringing it to 6.5%. This move is part of an ongoing effort to curb persistent inflationary pressures, a decision widely anticipated by financial markets.",
            "source_url": "http://manualsource.com/rbi1"
        },
        {
            "title": "Indian Central Bank raises repo rate by 0.25% in expected move.",
            "content": "In a widely anticipated monetary policy action, the RBI has increased its primary lending rate by 0.25 percentage points. Governor Shaktikanta Das stated the focus remains on withdrawing accommodation.",
            "source_url": "http://manualsource.com/rbi2"
        },
    ]
    
    final_dataset = manual_duplicates + fetched_data
    
    # 3. Save to the correct location
    output_path = "financial_news_intel/data/mock_dataset.json"
    
    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, indent=2, ensure_ascii=False)
        
    print(f"\nTotal articles collected: {len(final_dataset)}")
    print(f"Successfully saved all articles to {output_path}")