#!/bin/bash

echo "🔧 Creating project structure for financial_news_intel..."

# -----------------------------
# 1. Create project root
# -----------------------------
mkdir -p financial_news_intel
cd financial_news_intel || exit

# -----------------------------
# 2. Create virtual environment
# -----------------------------
echo "📦 Creating virtual environment..."
python3 -m venv venv

echo "📌 Activating virtual environment..."
# macOS/Linux activation
source venv/bin/activate

# -----------------------------
# 3. Create directories
# -----------------------------
echo "📁 Creating directories..."

mkdir -p agents
mkdir -p core
mkdir -p api
mkdir -p data
mkdir -p tests/unit
mkdir -p tests/integration

# -----------------------------
# 4. Create agent files
# -----------------------------
echo "🧩 Creating agent files..."

touch agents/__init__.py
touch agents/ingestion_agent.py
touch agents/deduplication_agent.py
touch agents/entity_agent.py
touch agents/impact_agent.py
touch agents/storage_agent.py
touch agents/query_agent.py

# -----------------------------
# 5. Create core files
# -----------------------------
touch core/__init__.py
touch core/langgraph_flow.py
touch core/ner_model.py
touch core/embedding_model.py
touch core/vector_db.py

# -----------------------------
# 6. Create API files
# -----------------------------
touch api/__init__.py
touch api/main.py

# -----------------------------
# 7. Create data files
# -----------------------------
touch data/mock_dataset.json
touch data/stock_mapping.json

# -----------------------------
# 8. Create test files
# -----------------------------
touch tests/__init__.py
touch tests/unit/test_deduplication.py
touch tests/integration/test_full_flow.py

# -----------------------------
# 9. Project-level files
# -----------------------------
touch ARCHITECTURE.md
touch README.md
touch run.py

# -----------------------------
# 10. Create requirements
# -----------------------------
cat <<EOF > requirements.txt
langgraph
fastapi
uvicorn
sentence-transformers
chromadb
python-dotenv
pydantic
requests
EOF

echo "✅ Project setup complete!"
echo "📌 Virtual environment is ACTIVE."
echo "➡️ Next: install dependencies using: pip install -r requirements.txt"
