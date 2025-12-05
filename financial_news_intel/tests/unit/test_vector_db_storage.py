from financial_news_intel.core.vector_db import vector_db_client

vector_results = vector_db_client.get_indexed_documents(limit=20)

print("\n--- CHROMADB VECTOR INDEX CHECK (Top Documents) ---")
if vector_results.get('ids'):
    for i, doc_id in enumerate(vector_results['ids']):
        metadata = vector_results['metadatas'][i]

        print(f"\nDocument ID: {doc_id[:8]}...")
        print(f"  db_id: {metadata.get('db_id', 'N/A')}")
        print(f"  Companies: {metadata.get('companies', 'N/A')}")
        print(f"  Sectors: {metadata.get('sectors', 'N/A')}")
        print(f"  Regulators: {metadata.get('regulators', 'N/A')}")
        print(f"  Sentiment: {metadata.get('sentiment', 'N/A')}")
        print(f"  Vector Dimensions: {len(vector_results['embeddings'][i])}")
        print(f"  Document Snippet: {vector_results['documents'][i][:120]}...")

else:
    print("No documents found in the ChromaDB RAG collection.")
