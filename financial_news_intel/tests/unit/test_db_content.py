# test_db_contents.py
import json
from financial_news_intel.core.db_service import db_service

print("--- STORIES TABLE CONTENTS ---")
stories = db_service.fetch_all_stories_table()
print(json.dumps(stories, indent=2))

print("\n--- STOCK_IMPACTS TABLE CONTENTS ---")
impacts = db_service.fetch_all_stock_impacts_table()
print(json.dumps(impacts, indent=2))


# # test_db_contents.py
# import pandas as pd
# from financial_news_intel.core.db_service import db_service

# def print_table_dataframes():
#     # --- STORIES TABLE ---
#     stories_data = db_service.fetch_all_stories_table()
    
#     print("\n=========================================================")
#     print("      Table 1: Stories (Main News Data)")
#     print("=========================================================")
    
#     if stories_data:
#         # Create DataFrame
#         stories_df = pd.DataFrame(stories_data)
        
#         # Truncate long text fields for cleaner terminal display
#         if 'story_text' in stories_df.columns:
#             # Shorten the story text and other JSON fields for readability
#             stories_df['story_id'] = stories_df['story_id'].str.slice(0, 8) + '...'
#             stories_df['story_text'] = stories_df['story_text'].str.slice(0, 70) + '...'
#             stories_df['companies_json'] = stories_df['companies_json'].str.slice(0, 40) + '...'

#         print(stories_df.to_string())
#         print(f"\nTotal rows in Stories table: {len(stories_data)}")
#     else:
#         print("The Stories table is empty.")


#     # --- STOCK_IMPACTS TABLE ---
#     impacts_data = db_service.fetch_all_stock_impacts_table()
    
#     print("\n=========================================================")
#     print("      Table 2: Stock_Impacts (Linkage Data)")
#     print("=========================================================")

#     if impacts_data:
#         # Create DataFrame
#         impacts_df = pd.DataFrame(impacts_data)
        
#         # Truncate story_id for readability
#         if 'story_id' in impacts_df.columns:
#             impacts_df['story_id'] = impacts_df['story_id'].str.slice(0, 8) + '...'
            
#         print(impacts_df.to_string())
#         print(f"\nTotal rows in Stock_Impacts table: {len(impacts_data)}")
#     else:
#         print("The Stock_Impacts table is empty.")


# if __name__ == "__main__":
#     print_table_dataframes()