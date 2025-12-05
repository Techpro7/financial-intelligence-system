# 💰 Financial News Intelligence System

A self-contained system for real-time financial news analysis, using a **LangGraph** pipeline powered by a local **Llama 3 LLM (via Ollama)**, and structured with **Docker Compose**.

This system analyzes streaming news, deduplicates stories, and predicts stock impact, sector classification, and a confidence score for each prediction.

---

## 🏗️ Architecture Overview

The system runs as multiple isolated services:

1. **`ollama` (External)**: Runs the local **Llama 3** Large Language Model, which acts as the core "brain" for entity extraction and impact analysis.
2. **`ingestion-worker`**: The continuous processing engine that uses **LangGraph** to fetch, analyze, and store news data.
3. **`api-service`**: A **FastAPI** application that provides a structured interface for querying the analyzed financial data.
4. **`chroma`**: The Vector Database (ChromaDB) used for fast deduplication and semantic search (RAG).

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites-install-the-essential-tools)
- [Installation Steps](#-installation-steps)
- [Starting Ollama Server](#-starting-ollama-server)
- [Project Setup](#-project-setup)
- [Running the System](#-running-the-system)
- [Environment Variables](#-environment-variables)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## 🛠️ Prerequisites - Install the Essential Tools

Before you can clone and run the project, you must install the following software.

### 1.1. Git (Source Code Manager)

Git is required to download the project code from GitHub.

**Windows/macOS:**
- Download the installer from the official Git website: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- Run the installer and follow the setup wizard

**Linux (Debian/Ubuntu):**
    ```bash
    sudo apt update
    sudo apt install git
    ```

**macOS (using Homebrew):**
```bash
brew install git
```

**Verify Installation:**
```bash
git --version
```

### 1.2. Python 3.9+ (Required for Local Development)

While Docker containers include Python, you'll need Python for local development and testing.

**Windows:**
- Download from [https://www.python.org/downloads/](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**macOS:**
```bash
# Using Homebrew
brew install python@3.9

# Or download from python.org
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

**Verify Installation:**
```bash
python3 --version
# Should show Python 3.9.x or higher
```

### 1.3. Docker & Docker Compose (Containerization)

Docker is used to run all services (API, Worker, Database) in isolated, ready-to-use environments.

**Installation:**
- Download and install **Docker Desktop** for your operating system: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- **Start Docker Desktop** after installation
- Ensure the Docker whale icon is visible and running in your system tray/menu bar

**Verify Installation:**
```bash
docker --version
docker-compose --version
```

**Note:** Docker Desktop includes Docker Compose, so you don't need to install it separately.

### 1.4. Ollama (Local LLM Server)

Ollama is a simple tool for running large language models locally. Your `ingestion-worker` connects to this server.

**Installation:**
- Download and install Ollama for your OS: [https://ollama.com/download](https://ollama.com/download)
- **macOS/Linux:** The installer will add Ollama to your PATH
- **Windows:** Run the installer and follow the setup wizard

**Verify Installation:**
```bash
ollama --version
```

---

## 🚀 Installation Steps

### Step 1: Clone the Repository

Clone the project to your computer and navigate into the folder.

```bash
# Replace <YOUR_REPO_URL> with the HTTPS link to your GitHub repository
git clone <YOUR_REPO_URL>
cd financial_intelligence_system
```

### Step 2: Create Python Virtual Environment (Optional but Recommended)

For local development and testing, create a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Python Dependencies (For Local Development)

If you want to run tests or develop locally:

```bash
# Make sure virtual environment is activated
pip install --upgrade pip
pip install -r financial_news_intel/requirements.txt

# Install spaCy language model (required for NER)
python -m spacy download en_core_web_md
```

---

## 🦙 Starting Ollama Server

**CRITICAL:** You must start Ollama and download the LLM model before running the Docker services.

### Step 1: Start Ollama Service

**macOS/Linux:**
```bash
# Start Ollama in the background
ollama serve

# Or if it's already running as a service, verify it's running:
curl http://localhost:11434/api/tags
```

**Windows:**
- Ollama should start automatically after installation
- If not, open the Ollama application from the Start menu

**Verify Ollama is Running:**
```bash
# Test the Ollama API
curl http://localhost:11434/api/tags

# Should return a JSON response with available models
```

### Step 2: Download the Required LLM Model

The system uses **Llama 3** by default. Download it using Ollama:

```bash
# Download Llama 3 (this may take several minutes depending on your internet speed)
ollama pull llama3

# Verify the model is downloaded
ollama list

# Test the model
ollama run llama3 "Hello, how are you?"
```

**Note:** The first time you run `ollama pull llama3`, it will download approximately 4.7GB of data. Ensure you have:
- Sufficient disk space (at least 10GB free recommended)
- Stable internet connection
- Patience (download may take 10-30 minutes depending on speed)

**Alternative Models:**
If you want to use a different model, you can modify the `OLLAMA_MODEL_NAME` in your `.env` file (see Environment Variables section).

---

## 📁 Project Setup

### Step 1: Create Environment File

Create a `.env` file in the project root directory:

```bash
# Navigate to project root
cd financial_intelligence_system

# Create .env file
touch .env
```

### Step 2: Configure Environment Variables

Edit the `.env` file with your preferred settings:

```bash
# .env file content
# LLM Configuration (Ollama)
OLLAMA_MODEL_NAME=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Embedding Model Configuration
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# NER Model Configuration
SPACY_MODEL_NAME=en_core_web_md

# Vector Database (ChromaDB)
CHROMA_DB_MODE=remote
CHROMA_DB_URL=http://chroma:8000
CHROMA_DB_PATH=./chroma_data
CHROMA_COLLECTION_NAME=financial_news_dedup
CHROMA_RAG_COLLECTION_NAME=financial_news_rag

# Deduplication Configuration
DEDUPLICATION_SIMILARITY_THRESHOLD=0.95
```

**Note:** When running in Docker, `CHROMA_DB_URL` should be `http://chroma:8000` (using Docker service name). For local development, use `http://localhost:8000`.

---

## 🏃 Running the System

### Option 1: Using Docker Compose (Recommended)

This is the easiest way to run the entire system.

#### Step 1: Ensure Ollama is Running

**Before starting Docker services, make sure Ollama is running:**

```bash
# Verify Ollama is accessible
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

#### Step 2: Build and Start Docker Services

```bash
# Navigate to project root (where docker-compose.yml is located)
cd financial_intelligence_system

# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Step 3: Verify Services are Running

```bash
# Check running containers
docker-compose ps

# You should see:
# - chroma_server (ChromaDB)
# - financial_intel_api (API Service)
# - financial_intel_worker (Ingestion Worker)
```

#### Step 4: Access the API

Once services are running, you can access:

- **API Documentation (Swagger UI):** http://localhost:8080/docs
- **API Alternative Docs (ReDoc):** http://localhost:8080/redoc
- **ChromaDB:** http://localhost:8000

### Option 2: Local Development (Without Docker)

For local development and testing:

#### Step 1: Start ChromaDB (Using Docker)

```bash
# Start only ChromaDB service
docker-compose up -d chroma

# Verify ChromaDB is running
curl http://localhost:8000/api/v1/heartbeat
```

#### Step 2: Set Environment Variables

```bash
# For local development, update .env:
CHROMA_DB_MODE=local
CHROMA_DB_URL=http://localhost:8000
```

#### Step 3: Run Python Scripts Locally

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run tests
python -m pytest financial_news_intel/tests/

# Run pipeline manually
python financial_news_intel/pipeline.py
```

---

## 🔧 Environment Variables

The system uses environment variables for configuration. Create a `.env` file in the project root:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL_NAME` | `llama3` | The Ollama model to use for LLM operations |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | Sentence transformer model for embeddings |
| `SPACY_MODEL_NAME` | `en_core_web_md` | spaCy model for NER |
| `CHROMA_DB_MODE` | `local` | ChromaDB mode: `local` or `remote` |
| `CHROMA_DB_URL` | `http://localhost:8000` | ChromaDB server URL (use `http://chroma:8000` in Docker) |
| `CHROMA_DB_PATH` | `./chroma_data` | Local ChromaDB data path |
| `CHROMA_COLLECTION_NAME` | `financial_news_dedup` | ChromaDB collection for deduplication |
| `CHROMA_RAG_COLLECTION_NAME` | `financial_news_rag` | ChromaDB collection for RAG |
| `DEDUPLICATION_SIMILARITY_THRESHOLD` | `0.95` | Similarity threshold for deduplication (0-1) |

---

## 🧪 Testing

### Test API Endpoints

There are two ways to test the API:

#### Option 1: Using Web Browser (Manual)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to initialize** (especially the ingestion-worker to process some data):
   ```bash
   # Monitor logs to see when ingestion-worker has processed some articles
   docker-compose logs -f ingestion-worker
   ```
   Wait until you see some articles being processed (usually 1-2 minutes).

3. **Open API Documentation in Browser:**
   - Navigate to: **http://localhost:8080/docs**
   - This opens the Swagger UI where you can:
     - View all available endpoints
     - Test queries interactively
     - See request/response schemas
     - Execute API calls directly from the browser

#### Option 2: Using Automated Browser Script (Recommended)

1. **Build and start Docker services:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

2. **Wait for ingestion-worker to process data:**
   ```bash
   # Monitor the ingestion-worker logs
   docker-compose logs -f ingestion-worker
   ```
   Wait for the LangGraph pipeline to run and process some articles (typically 1-2 minutes after startup).

3. **Run the browser automation script:**
   ```bash
   bash open_browser.sh
   ```
   This script will:
   - Wait 10 seconds for the API to be fully ready
   - Automatically open your default browser
   - Navigate to the Swagger UI at http://localhost:8080/docs
   - Allow you to test queries interactively

### Run Performance and Accuracy Tests

**Important:** Before running tests, you must pause the ingestion-worker service to avoid conflicts.

1. **Pause the ingestion-worker service:**
   ```bash
   docker-compose pause ingestion-worker
   ```

2. **Run the test metrics script inside Docker:**
   ```bash
   # Execute test_metrics.py in the api-service container
   docker-compose exec api-service python test_metrics.py
   ```

3. **Resume the ingestion-worker after testing:**
   ```bash
   docker-compose unpause ingestion-worker
   ```

**What test_metrics.py does:**
- Resets ChromaDB for clean test execution
- Runs the LangGraph pipeline against a golden dataset
- Calculates performance metrics (latency, throughput)
- Measures accuracy (sentiment, entity extraction, impact prediction)
- Provides detailed benchmark results

### Run Unit Tests

```bash
# With Docker (make sure ingestion-worker is paused)
docker-compose pause ingestion-worker
docker-compose exec api-service python -m pytest financial_news_intel/tests/unit/ -v
docker-compose unpause ingestion-worker

# Or locally (with venv activated)
python -m pytest financial_news_intel/tests/unit/ -v
```

### Test Query Agent

```bash
# Run query agent test
python financial_news_intel/tests/unit/test_query_agent.py
```

### Test API Endpoints via Command Line

```bash
# Start services
docker-compose up -d

# Test API health endpoint
curl http://localhost:8080/health

# Test query endpoint
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the recent positive news regarding the IT sector?"}'
```

---

## 🐛 Troubleshooting

### Issue: Ollama Connection Failed

**Symptoms:**
- Error: `Connection refused` or `Failed to connect to Ollama`
- LLM operations fail

**Solutions:**
1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```
2. Start Ollama if not running:
   ```bash
   ollama serve
   ```
3. Verify model is downloaded:
   ```bash
   ollama list
   ```
4. If using Docker, ensure Ollama is accessible from containers:
   - On macOS/Windows: Use `host.docker.internal:11434` instead of `localhost:11434`
   - Update `.env`: `OLLAMA_BASE_URL=http://host.docker.internal:11434`

### Issue: ChromaDB Connection Failed

**Symptoms:**
- Error: `Failed to connect to ChromaDB`
- Vector operations fail

**Solutions:**
1. Verify ChromaDB container is running:
   ```bash
   docker-compose ps chroma
   ```
2. Check ChromaDB logs:
   ```bash
   docker-compose logs chroma
   ```
3. Restart ChromaDB:
   ```bash
   docker-compose restart chroma
   ```
4. Verify ChromaDB is accessible:
   ```bash
   curl http://localhost:8000/api/v1/heartbeat
   ```

### Issue: Sentence Transformer Model Not Loading

**Symptoms:**
- Error: `Error in get_embeddings` or `Model not found`
- Embedding generation fails

**Solutions:**
1. The model downloads automatically on first use
2. Ensure internet connection is available for first-time download
3. Check disk space (model requires ~100MB)
4. Verify model name in `.env`: `EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2`

### Issue: spaCy Model Not Found

**Symptoms:**
- Error: `Can't find model 'en_core_web_md'`

**Solutions:**
```bash
# Download the spaCy model
python -m spacy download en_core_web_md

# Or in Docker:
docker-compose exec api-service python -m spacy download en_core_web_md
```

### Issue: Docker Containers Won't Start

**Symptoms:**
- `docker-compose up` fails
- Containers exit immediately

**Solutions:**
1. Check Docker Desktop is running
2. Check logs:
   ```bash
   docker-compose logs
   ```
3. Rebuild containers:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```
4. Check port conflicts:
   - Port 8000: ChromaDB
   - Port 8080: API Service
   - Port 11434: Ollama

### Issue: Out of Memory Errors

**Symptoms:**
- Containers crash with OOM errors
- System becomes slow

**Solutions:**
1. Increase Docker Desktop memory limit (Settings → Resources → Memory)
2. Use smaller LLM model (e.g., `llama3:8b` instead of `llama3`)
3. Reduce batch sizes in configuration

### Issue: Python Dependencies Installation Fails

**Symptoms:**
- `pip install` errors
- Missing dependencies

**Solutions:**
1. Update pip:
   ```bash
   pip install --upgrade pip
   ```
2. Install build dependencies (Linux):
   ```bash
   sudo apt-get install build-essential python3-dev
   ```
3. Use Docker instead (recommended):
   ```bash
   docker-compose build
   ```

---

## 📊 Service Ports

| Service | Port | Description |
|---------|------|-------------|
| API Service | 8080 | FastAPI application |
| ChromaDB | 8000 | Vector database |
| Ollama | 11434 | LLM server |

---

## 🛑 Stopping the System

### Stop Docker Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: Deletes data)
docker-compose down -v
```

### Stop Ollama

```bash
# Stop Ollama service
# macOS/Linux:
pkill ollama

# Or if running as service:
# macOS: Stop from Activity Monitor
# Windows: Stop from Task Manager
```

---

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Documentation](https://ollama.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

[Add your license information here]

---

## 👥 Authors

[Add author information here]

---

## 🙏 Acknowledgments

- LangChain/LangGraph team for the amazing framework
- Ollama for making local LLMs accessible
- ChromaDB for vector database capabilities

---

**Happy Coding! 🚀**
