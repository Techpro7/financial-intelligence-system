# 📐 Financial News Intelligence System: Architecture

This document details the components, data flow, and technologies used in the Financial News Intelligence System.

---

## 1. High-Level Diagram

The system operates as a **Microservices Architecture** utilizing a hybrid data storage approach: **Vector Database (ChromaDB)** for context/search and **Relational Database (SQLite)** for structured persistence.



[Image of Relational Database Schema]


## 2. Component Breakdown

The entire system is containerized and orchestrated by **Docker Compose**, managing three main services and the core LLM dependency (Ollama).

| Component | Service Name | Role | Technology |
| :--- | :--- | :--- | :--- |
| **Orchestration** | `LangGraph Pipeline` | Defines the state machine and flow logic for ingestion and analysis. | Python, LangGraph |
| **Ingestion Scheduler** | `ingestion-worker` | Executes the LangGraph pipeline periodically for continuous data processing. | Python, Docker |
| **API Interface** | `api-service` | Hosts the REST API for user query submission and structured data retrieval (`/query`). | FastAPI, Uvicorn |
| **Vector Database** | `chroma` | Stores news article embeddings for **Deduplication** and **Retrieval-Augmented Generation (RAG)**. | ChromaDB |
| **Structured Database** | *Internal* | Persists the final, enriched `ConsolidatedStory` objects. | SQLite |
| **Core Intelligence** | *External* | Provides LLM inference for entity extraction and impact analysis. | Ollama (Llama 3) |

---

## 3. Data Flow and LangGraph Pipeline

The system's core functionality is encapsulated in a sequential, context-aware **LangGraph State Machine**.

### 3.1. Ingestion Phase

1.  **Ingestion Agent**: Fetches and aggregates raw articles from configured news sources.
2.  **Conversion**: Converts raw article dictionaries into standardized **`RawArticle`** Pydantic models.

### 3.2. Deduplication and Consolidation Phase

1.  **Deduplication Agent**:
    * **Lookup**: Queries **ChromaDB** to find existing stories with high similarity to the new article's embedding.
    * **Consolidation**: Groups similar articles into a single, unique **`ConsolidatedStory`** record.

### 3.3. Analysis and Persistence Phase

1.  **Entity Extraction Agent**: Uses the **Ollama LLM** to extract structured entities (companies, regulators) and general **sentiment** from the consolidated story.
2.  **Impacted Stock Agent (Enhanced)**:
    * Uses the **Ollama LLM** to analyze the story's financial context for each relevant company.
    * **Output**: This agent extracts and provides a structured output (`ImpactModel`) that includes:
        * **Impact Direction** (Positive/Negative/Neutral).
        * **Sector** classification (e.g., 'Technology', 'Financial Services').
        * **Confidence Level** (0.0 to 1.0) for the prediction.
3.  **Storage & Indexing Agent**:
    * **Structured Persistence**: Saves the final, fully enriched `ConsolidatedStory` (including all new impact analysis) into the **SQLite Database**.
    * **Vector Indexing**: Indexes the final story embedding into **ChromaDB**.

---

## 4. Query Flow (Structured Data Retrieval)

The **API Service** processes user queries via the `/query` endpoint by retrieving and presenting structured data directly, **without** a final LLM summarization step.

1.  **Query Agent**: Receives a natural language query (e.g., "What is the market impact of the latest ONGC news?").
2.  **Vector Retrieval**: The agent converts the query into an embedding and uses **ChromaDB** to retrieve the vectors of the top $K$ most relevant `ConsolidatedStory` records (RAG step).
3.  **Context Assembly**: The full, structured `ConsolidatedStory` data corresponding to the retrieved vectors is fetched from the **SQLite Database**.
4.  **Final Output (Structured)**: The agent returns the raw, structured list of **`QueryResponse`** models. This list contains all the financial intelligence found, including the sentiment, entities, detailed impact analysis, sector, and confidence scores, allowing the client to consume and interpret the raw data.

---

For a deeper dive into the fundamental principles of building complex stateful workflows for AI agents, you might find this video useful: [LangGraph: Building Stateful AI Agents](https://www.youtube.com/watch?v=k5_541X8V70).