# GridGuide — System Architecture & Design

GridGuide is an AI-powered regulatory assistant for power-system engineers and power traders, navigating Indian Electricity Grid Code (IEGC) and Central Electricity Regulatory Commission (CERC) regulations in English and Hindi.

---

## 1. System Architecture

```
                       +---------------------------------------+
                       |           Client / Browser            |
                       +-------------------+-------------------+
                                           |
                              HTTP / SSE   |   GET /health, /ready, /usage
                                           |   POST /chat, POST /ask
                                           v
                       +---------------------------------------+
                       |          FastAPI API Service          |
                       |  (Docker Container: python:3.12-slim) |
                       +-------------------+-------------------+
                                           |
                     +---------------------+---------------------+
                     |                                           |
                     v                                           v
+---------------------------------------+     +-------------------------------------+
|        LLM Provider Layer             |     |       PostgreSQL 16 + pgvector      |
|  - OpenAI-compatible streaming client |     |  (Docker Service: pgvector:pg16)    |
|  - Retries with backoff & full jitter |     |  - Document metadata & chunks       |
|  - LLMUnavailable fallback wrapper    |     |  - Multilingual vector embeddings   |
|  - Token counting & cost logging      |     |  - HNSW index for cosine distance   |
+---------------------------------------+     +-------------------------------------+
```

---

## 2. API Endpoints

### 2.1 `GET /health`
- **Purpose:** Liveness check. Confirms the FastAPI process is running.
- **Dependencies:** None (must not touch database or external APIs).
- **Response (200 OK):**
```json
{
  "status": "ok",
  "app": "gridguide",
  "environment": "local"
}
```

---

### 2.2 `GET /ready`
- **Purpose:** Readiness check. Confirms dependencies (PostgreSQL database) are reachable.
- **Dependencies:** PostgreSQL (`SELECT 1` with 3-second timeout).
- **Responses:**
  - `200 OK` (connected): `{"status": "ready", "database": "ok"}`
  - `200 OK` (no DB configured): `{"status": "ready", "database": "not configured"}`
  - `503 Service Unavailable`: `{"status": "not ready", "database": "connection timed out"}`

---

### 2.3 `POST /chat`
- **Purpose:** Streams assistant responses via Server-Sent Events (SSE) with resilience and cost accounting.
- **Request Body (`application/json`):**
```json
{
  "messages": [
    {"role": "user", "content": "What is the permitted frequency band under the current IEGC?"}
  ],
  "temperature": 0.2
}
```
- **Validation:**
  - `messages`: 1 to 50 items.
  - `role`: regex pattern `^(system|user|assistant)$`.
  - `content`: 1 to 20,000 characters.
  - `temperature`: float between 0.0 and 2.0.
- **Response:** `text/event-stream`
  - Delta chunks: `data: {"delta": "According"}\n\n`
  - On error: `event: error\ndata: {"error": "..."}\n\n`
  - Completion: `event: done\ndata: {"usage": {"input_tokens": 35, "output_tokens": 42}, "cost_usd": 0.00003}\n\n`

---

### 2.4 `GET /usage`
- **Purpose:** Aggregates call volume, token counts, and expenditure grouped by UTC date from `logs/cost.jsonl`.
- **Response (200 OK):**
```json
{
  "2026-10-24": {
    "calls": 12,
    "input_tokens": 4200,
    "output_tokens": 1500,
    "cost_usd": 0.00153
  }
}
```

---

### 2.5 `POST /ask` *(Planned for Week 3 — RAG Ingestion)*
- **Purpose:** Retrieval-augmented Q&A with page-level regulatory citations and bilingual answer card formatting.
- **Request Body:**
```json
{
  "question": "ग्रिड कोड के अनुसार शेड्यूल में संशोधन कितने समय पहले किया जा सकता है?",
  "language": "hi",
  "top_k": 4
}
```
- **Response (200 OK):**
```json
{
  "answer": "ग्रिड कोड के तहत, उत्पादन कंपनियों और खरीदारों द्वारा वास्तविक समय संचालन से 7 या 8 समय-ब्लॉक पहले शेड्यूल संशोधन प्रस्तुत किया जा सकता है...",
  "clause_reference": "IEGC 2023, Part 5: Scheduling and Despatch Code, Regulation 47(4)",
  "citations": [
    {
      "document": "Draft-IEGC-07062022.pdf",
      "page": 78,
      "clause": "47(4)",
      "snippet": "Revision of schedule on declared capability and requisition shall be effective from the 7th or 8th time block..."
    }
  ],
  "confidence": 0.92
}
```

---

## 3. Database Schema (PostgreSQL 16 + pgvector)

The database schema stores CERC regulatory publications, chunked sections, and vector embeddings for semantic and cross-lingual retrieval.

### 3.1 Table: `documents`
Tracks source PDF regulations downloaded from CERC.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'IEGC', 'DSM', 'GNA', 'OA', 'PMR', etc.
    source_url TEXT NOT NULL,
    total_pages INTEGER NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    sha256_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Table: `document_chunks`
Stores text segments along with structural metadata (page number, clause identifier) and multilingual embeddings.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    clause_number VARCHAR(50),      -- e.g., 'Regulation 6(1)', 'Clause 5.2'
    heading VARCHAR(255),           -- e.g., 'Operating Frequency Range'
    content_en TEXT NOT NULL,       -- Original English statutory text
    token_count INTEGER NOT NULL,
    embedding vector(1536),         -- Compatible with text-embedding-3-small / multilingual embedding models
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_doc_chunk UNIQUE (document_id, chunk_index)
);

-- HNSW cosine distance index for vector similarity search
CREATE INDEX idx_chunks_embedding ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- B-Tree indexes for relational filtering
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_page_number ON document_chunks(page_number);
```

---

## 4. Reliability and Fallback Workflow

```
[User Request]
       |
       v
+--------------+
| POST /chat   |
+--------------+
       |
       v
+-------------------------------+      Transient Error
| Main Provider                 | --------------------------+
| (e.g. Primary Model, timeout) |                           |
+-------------------------------+                           v
       |                                          +-------------------+
       | Success                                  | Retry with Jitter |
       |                                          | (attempts 1..3)   |
       v                                          +-------------------+
[Stream response pieces to user]                            |
       |                                                    v
       |                                          All Retries Failed?
       |                                                    |
       |                                                    v (Yes -> LLMUnavailable)
       |                                          +-------------------+
       |                                          | Fallback Provider |
       |                                          | (Backup Model)    |
       |                                          +-------------------+
       |                                                    |
       | <--------------------------------------------------+
       v
+-------------------------------------+
| log_call() -> logs/cost.jsonl       |
| Send SSE "event: done" with usage   |
+-------------------------------------+
```
