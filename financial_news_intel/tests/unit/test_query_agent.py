# run_query_test.py
import sys
import os
from financial_news_intel.agents.query_agent import query_processing_agent

# --- Sample Queries ---

# Existing Queries
query_1 = "What is the recent positive news regarding the IT sector or Reliance?"
query_2 = "Can you summarize negative regulatory news about the banking sector?"

# New Targeted Queries based on your ingestion data (Metals/Positive)

# 🚀 Query 3: Targets a specific company and sector (Vedanta, Metals)
query_3 = "What is the positive news related to Vedanta or other metal stocks?"

# 🚀 Query 4: Targets the full sector and uses the sentiment filter explicitly
query_4 = "Summarize all positive news impacting the metals and mining sector."

# 🚀 Query 5: Tests the negative filter (Should return 'No relevant news' if only positive data exists)
query_5 = "Is there any recent negative news about SAIL or National Aluminium?"


print("=========================================================")
print("--- Starting Context-Aware Query Agent Test ---")
print("=========================================================")

# Run Query 1 (Existing)
print(f"\n--- Running Query 1: {query_1} ---")
response_1 = query_processing_agent(query_1)
print(f"\nFINAL ANSWER 1:\n{response_1}")

print("\n---------------------------------------------------------")

# Run Query 2 (Existing)
print(f"\n--- Running Query 2: {query_2} ---")
response_2 = query_processing_agent(query_2)
print(f"\nFINAL ANSWER 2:\n{response_2}")

print("\n---------------------------------------------------------")

# Run Query 3 (New - High Match Expected)
print(f"\n--- Running Query 3: {query_3} ---")
response_3 = query_processing_agent(query_3)
print(f"\nFINAL ANSWER 3:\n{response_3}")

print("\n---------------------------------------------------------")

# Run Query 4 (New - Sector Match Expected)
print(f"\n--- Running Query 4: {query_4} ---")
response_4 = query_processing_agent(query_4)
print(f"\nFINAL ANSWER 4:\n{response_4}")

print("\n---------------------------------------------------------")

# Run Query 5 (New - Filter Check: Low/No Match Expected)
print(f"\n--- Running Query 5: {query_5} ---")
response_5 = query_processing_agent(query_5)
print(f"\nFINAL ANSWER 5:\n{response_5}")

print("\n=========================================================")