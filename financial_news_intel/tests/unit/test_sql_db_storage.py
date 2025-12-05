from financial_news_intel.core.db_service import db_service

results = db_service.fetch_all_stories_with_impacts()

print("\n--- SQL DB CONTENT CHECK ---")
for result in results:
    print(f"\nStory ID: {result['story_id']}")
    print(f"  Sentiment: {result['sentiment']}")
    print(f"  Companies: {result['companies']}")
    print(f"  Total Impacts: {result['impacts_count']}")
    if result['sample_impacts']:
        ticker, direction, confidence = result['sample_impacts'][0]
        print(f"  Sample Impact: {ticker} ({direction}, Confidence: {confidence})")