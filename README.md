# SaaS Intelligent AI Agent for Document Automation

A full-stack SaaS platform for intelligent document processing, retrieval, analysis, and conversational interaction with uploaded documents.

The platform allows users to upload documents, extract their content using AI-powered document/vision processing, divide the extracted content into searchable chunks, generate vector embeddings, store those embeddings in PostgreSQL with `pgvector`, and interact with their documents through Retrieval-Augmented Generation (RAG).

The system also provides document classification, summaries, conversational chat, authentication, document management, and an AI agent capable of helping users interact with their document knowledge base.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Main Features](#2-main-features)
- [3. System Architecture](#3-system-architecture)
- [4. Technology Stack](#4-technology-stack)
- [5. Project Structure](#5-project-structure)
- [6. How the System Works](#6-how-the-system-works)
- [7. Document Processing Pipeline](#7-document-processing-pipeline)
- [8. RAG Pipeline](#8-rag-pipeline)
- [9. AI Agent](#9-ai-agent)
- [10. Authentication](#10-authentication)
- [11. Database](#11-database)
- [12. Background Processing](#12-background-processing)
- [13. Ollama Models](#13-ollama-models)
- [14. Docker Architecture](#14-docker-architecture)
- [15. Frontend](#15-frontend)
- [16. Backend](#16-backend)
- [17. API](#17-api)
- [18. Environment Variables](#18-environment-variables)
- [19. Installation and Setup](#19-installation-and-setup)
- [20. Running the Project](#20-running-the-project)
- [21. Database Migrations](#21-database-migrations)
- [22. API Documentation](#22-api-documentation)
- [23. Testing the System](#23-testing-the-system)
- [24. RAG Evaluation](#24-rag-evaluation)
- [25. Troubleshooting](#25-troubleshooting)
- [26. Development Workflow](#26-development-workflow)
- [27. Production Considerations](#27-production-considerations)
- [28. Security](#28-security)
- [29. Future Improvements](#29-future-improvements)
- [30. Project Status](#30-project-status)
- [31. License](#31-license)

---

# 1. Project Overview

## 1.1 Description

**SaaS Intelligent AI Agent for Document Automation** is a web-based platform designed to automate document processing and provide intelligent access to document information.

Instead of requiring users to manually read and search through large documents, the platform transforms uploaded files into structured, searchable knowledge.

The general workflow is:

```text
User
  │
  ▼
Upload Document
  │
  ▼
Document Storage
  │
  ▼
AI-powered Extraction
  │
  ▼
Extracted Text
  │
  ▼
Text Cleaning and Chunking
  │
  ▼
Embedding Generation
  │
  ▼
PostgreSQL + pgvector
  │
  ▼
Semantic Retrieval
  │
  ▼
Relevant Document Context
  │
  ▼
LLM / RAG
  │
  ▼
Generated Answer
```

The platform therefore combines conventional web application technologies with AI technologies to provide an intelligent document-management and question-answering system.

---

# 2. Main Features

## 2.1 User Authentication

The platform provides authentication using:

- User registration
- User login
- Password hashing
- JWT-based authentication
- Protected API endpoints
- Current-user identification
- User-specific document ownership

Authentication is handled by the FastAPI backend.

---

## 2.2 Document Upload

Authenticated users can upload supported documents.

The application validates the file extension before processing the document.

Supported formats include:

```text
.pdf
.png
.jpg
.jpeg
.docx
.txt
.pptx
```

After upload, the document is stored and a database record is created.

The document initially receives a processing status such as:

```text
pending
```

After successful processing:

```text
processed
```

If processing fails:

```text
failed
```

---

## 2.3 AI-powered Document Extraction

The platform extracts textual content from uploaded documents.

Depending on the document type, extraction can involve:

- Text file reading
- DOCX extraction
- PDF processing
- Image processing
- Vision-language model processing

The project uses an Ollama-hosted vision model for AI-powered extraction from visual document content.

The extraction process can preserve page information using page markers such as:

```text
[[PAGE 1]]
...
[[PAGE 2]]
...
```

This allows the system to associate extracted information with its original page.

---

## 2.4 Document Classification

Documents can be analyzed and classified according to their content.

The LLM can help infer document types or classify sections.

Examples of possible document categories include:

- CV
- Invoice
- Article
- Specification
- Report
- Other business documents

Classification is performed through backend services and LLM interaction.

---

## 2.5 Document Chunking

Large extracted documents are divided into smaller pieces called **chunks**.

Chunking is necessary because sending an entire large document to an LLM is inefficient and may exceed the model's context window.

The project uses configurable chunking parameters such as:

```text
Default chunk size: 450
Overlap: 50
Minimum chunk size: 40
Near-duplicate threshold: 0.88
Maximum section chunk: 900
```

Chunks can also contain page information.

A simplified chunk looks like:

```text
Document ID
Chunk ID
Chunk index
Page number
Content
Embedding
```

---

## 2.6 Embeddings

Each document chunk can be transformed into a numerical vector called an **embedding**.

The project uses:

```text
nomic-embed-text
```

for embedding generation.

Embeddings allow the application to compare the semantic similarity between:

```text
User question
```

and:

```text
Document chunks
```

rather than relying only on exact keyword matching.

---

## 2.7 Vector Search

The generated embeddings are stored in PostgreSQL using the `pgvector` extension.

When a user asks a question, the system:

1. Generates an embedding for the question.
2. Compares it with stored document chunk embeddings.
3. Calculates vector similarity/distance.
4. Selects the most relevant chunks.
5. Sends those chunks to the LLM as context.

The configured similarity/distance threshold is:

```text
0.7
```

with lower cosine distance representing greater similarity.

---

## 2.8 Retrieval-Augmented Generation

The platform uses **RAG (Retrieval-Augmented Generation)**.

Instead of asking the LLM to answer solely from its pretrained knowledge, the system first retrieves relevant information from the user's documents.

The simplified process is:

```text
Question
   │
   ▼
Question Embedding
   │
   ▼
Vector Search
   │
   ▼
Relevant Chunks
   │
   ▼
Context Construction
   │
   ▼
RAG Prompt
   │
   ▼
LLM
   │
   ▼
Answer
```

This makes the assistant capable of answering questions based on the user's uploaded documents.

---

## 2.9 Structured Answers

The RAG service can request structured answers from the LLM.

Supported answer categories include concepts such as:

```text
fact
list
count
overview
```

The backend parses the generated response before returning it to the application.

This makes the frontend response more predictable than relying exclusively on arbitrary text.

---

## 2.10 Document Summaries

The platform provides document summarization functionality.

A document can be processed by the LLM to generate a structured summary.

The summary functionality is separated into services responsible for:

- Prompt construction
- LLM invocation
- JSON parsing
- Normalization
- Fallback handling

---

## 2.11 Conversational Chat

Users can interact with their documents through a chat interface.

The system maintains concepts such as:

```text
Chat Session
    │
    ├── User message
    ├── Assistant message
    ├── User message
    └── Assistant message
```

Messages are associated with a user and document/chat session.

---

## 2.12 AI Agent

The platform includes an AI-agent layer on top of the document/RAG system.

The agent can help users:

- Clarify questions
- Rephrase questions
- Retrieve relevant document information
- Access document chunks
- Interact with document knowledge
- Route user requests toward appropriate capabilities

The agent is designed to provide a higher-level interface than directly exposing individual backend services.

---

# 3. System Architecture

The project follows a layered architecture.

```text
                         ┌──────────────────────┐
                         │       User           │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ React + Vite         │
                         │ Frontend             │
                         └──────────┬───────────┘
                                    │ HTTP / JSON
                                    ▼
                         ┌──────────────────────┐
                         │ FastAPI              │
                         │ REST API             │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
          ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
          │ PostgreSQL  │   │   Redis     │   │   Ollama    │
          │ + pgvector  │   │             │   │             │
          └─────────────┘   └──────┬──────┘   └─────────────┘
                                   │
                                   ▼
                            ┌─────────────┐
                            │   Celery    │
                            │   Worker    │
                            └─────────────┘
```

---

# 4. Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Static typing |
| Vite | Development/build tooling |
| CSS | Styling |
| Fetch/API client | Backend communication |

---

## Backend

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Pydantic | API validation and schemas |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| python-jose | JWT handling |
| Passlib / bcrypt | Password hashing |
| LangChain Ollama integration | LLM communication |

---

## Database

| Technology | Purpose |
|---|---|
| PostgreSQL | Relational database |
| pgvector | Vector storage and similarity search |
| SQLAlchemy | Database access |
| Alembic | Schema migrations |

---

## AI

| Technology | Purpose |
|---|---|
| Ollama | Local model serving |
| Qwen3 8B | Main LLM |
| Qwen2.5-VL 7B | Vision/document extraction |
| nomic-embed-text | Embeddings |
| RAG | Document question answering |

---

## Infrastructure

| Technology | Purpose |
|---|---|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Redis | Task broker / operational cache |
| Celery | Background task processing |

---

# 5. Project Structure

A simplified project structure is:

```text
saas-ia-platform/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── documents.py
│   │       ├── chat.py
│   │       ├── summary.py
│   │       └── ...
│   │
│   ├── core/
│   │   ├── security.py
│   │   ├── config.py
│   │   ├── file_validation.py
│   │   └── ...
│   │
│   ├── db/
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── document_chunk.py
│   │   ├── chat_session.py
│   │   └── message.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── chat.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── extraction_service.py
│   │   ├── embedding_service.py
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   ├── classification_service.py
│   │   ├── document_service.py
│   │   ├── chat_service.py
│   │   ├── summary/
│   │   └── ...
│   │
│   └── evaluation/
│       ├── cases.py
│       ├── metrics.py
│       ├── rag_eval.py
│       ├── runner.py
│       └── ...
│
├── alembic/
│   ├── versions/
│   └── ...
│
├── evals/
│   ├── rag_eval.local.jsonl
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
│
├── uploads/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

The exact directory structure may evolve as additional features are added.

---

# 6. How the System Works

## 6.1 User Registration

```text
User
 │
 ▼
React registration form
 │
 ▼
POST /auth/register
 │
 ▼
FastAPI
 │
 ▼
Validate input
 │
 ▼
Hash password
 │
 ▼
Create User model
 │
 ▼
PostgreSQL
```

The password is stored as a secure hash rather than plain text.

---

## 6.2 User Login

```text
User
 │
 ▼
Login form
 │
 ▼
POST /auth/login
 │
 ▼
Validate credentials
 │
 ▼
Verify password hash
 │
 ▼
Create JWT
 │
 ▼
Frontend stores authentication state
```

Subsequent protected requests include the JWT.

---

# 7. Document Processing Pipeline

The document pipeline is one of the most important parts of the application.

```text
Upload
  │
  ▼
Validate extension
  │
  ▼
Save file
  │
  ▼
Create Document record
status = pending
  │
  ▼
Background processing
  │
  ▼
Extract content
  │
  ▼
Clean text
  │
  ▼
Chunk text
  │
  ▼
Generate embeddings
  │
  ▼
Store chunks + embeddings
  │
  ▼
status = processed
```

If an exception occurs:

```text
Processing error
      │
      ▼
status = failed
```

This allows the frontend to display the processing state to the user.

---

# 8. RAG Pipeline

The RAG system is responsible for answering questions using uploaded documents.

## Step 1 — User question

Example:

```text
"What programming languages are listed in my CV?"
```

---

## Step 2 — Create query embedding

The question is sent to the embedding model:

```text
nomic-embed-text
```

The result is a vector.

---

## Step 3 — Vector search

The query vector is compared against the vectors stored for document chunks.

PostgreSQL + pgvector performs the vector search.

---

## Step 4 — Retrieve relevant chunks

The system retrieves the most relevant chunks.

For example:

```text
Chunk 8
Chunk 11
Chunk 4
Chunk 15
Chunk 6
```

---

## Step 5 — Build context

The retrieved chunks are combined into a context.

---

## Step 6 — Generate RAG prompt

The prompt contains:

```text
Question
+
Retrieved document context
+
Conversation history
+
Instructions
```

---

## Step 7 — LLM generation

The prompt is sent to:

```text
qwen3:8b
```

through Ollama.

---

## Step 8 — Parse answer

The backend parses the generated answer and converts it into the application's expected answer format.

---

# 9. AI Agent

The AI agent provides a higher-level interaction layer.

A simplified flow is:

```text
User Request
     │
     ▼
Agent
     │
     ├── Understand request
     │
     ├── Clarify/rephrase if necessary
     │
     ├── Select appropriate capability
     │
     ├── Retrieve document information
     │
     └── Generate response
```

The agent can use the existing RAG and document-processing infrastructure instead of duplicating those systems.

---

# 10. Authentication

The backend uses JWT authentication.

The general process is:

```text
Login
  │
  ▼
Credentials verified
  │
  ▼
JWT generated
  │
  ▼
Client sends JWT
  │
  ▼
HTTP Authorization header
  │
  ▼
FastAPI authentication dependency
  │
  ▼
Decode JWT
  │
  ▼
Retrieve user
  │
  ▼
Protected endpoint
```

The JWT contains the user identifier in the `sub` claim.

Protected resources are checked against the authenticated user's ID.

For example, document access should verify that:

```text
Document.user_id == current_user.id
```

This prevents users from accessing documents belonging to other users.

---

# 11. Database

The project uses PostgreSQL as the primary relational database.

`pgvector` extends PostgreSQL with vector storage and similarity-search capabilities.

## Main entities

### Users

Conceptually:

```text
users
-----
id
email
password
name
profile_image
...
```

---

### Documents

Conceptually:

```text
documents
---------
id
user_id
filename
file_path
doc_type
extracted_text
status
...
```

---

### Document Chunks

Conceptually:

```text
document_chunks
---------------
id
document_id
chunk_index
page_number
content
embedding
```

The `embedding` column uses pgvector.

The project uses a vector dimension of:

```text
768
```

for the configured embedding model.

---

### Chat Sessions

Conceptually:

```text
chat_sessions
-------------
id
user_id
document_id
...
```

---

### Messages

Conceptually:

```text
messages
--------
id
session_id
role
content
...
```

---

# 12. Background Processing

Long-running operations should not unnecessarily block HTTP requests.

The project uses:

```text
Celery
```

for background processing and:

```text
Redis
```

as the task broker.

The architecture is:

```text
FastAPI
   │
   │ enqueue task
   ▼
Redis
   │
   │ task message
   ▼
Celery Worker
   │
   ▼
Document processing
```

Potential background tasks include:

- Document extraction
- AI processing
- Chunk creation
- Embedding generation
- Other long-running operations

---

# 13. Ollama Models

The project uses Ollama to serve local AI models.

## 13.1 Main LLM

```text
qwen3:8b
```

Configured through:

```text
OLLAMA_MODEL
```

This model can be used for:

- Chat
- RAG answer generation
- Classification
- Summaries
- Agent functionality

---

## 13.2 Vision Model

```text
qwen2.5vl:7b
```

Configured through:

```text
VISION_MODEL
```

It is used for document/image understanding and extraction.

---

## 13.3 Embedding Model

```text
nomic-embed-text
```

Configured through:

```text
OLLAMA_EMBEDDING_MODEL
```

It converts text into vectors for semantic search.

---

# 14. Docker Architecture

The project uses Docker to isolate and run infrastructure services.

A typical architecture is:

```text
Docker Compose
│
├── api
│   └── FastAPI
│
├── postgres
│   └── PostgreSQL + pgvector
│
├── redis
│   └── Redis
│
├── celery
│   └── Celery worker
│
└── ollama
    └── Ollama
```

The React frontend can be run directly on the host during development:

```text
React + Vite
     │
     └── localhost:5173
```

while the backend services run in Docker.

The frontend does not need to be containerized for local development.

---

# 15. Frontend

The frontend is implemented using React and TypeScript.

It provides the user interface for:

- Authentication
- Dashboard
- Document upload
- Document listing
- Document details
- Document processing status
- Document summaries
- Chat
- AI-agent interaction
- Profile/settings
- Other application functionality

The frontend communicates with FastAPI using HTTP requests.

Typical development command:

```bash
npm run dev
```

Vite normally exposes the development server at:

```text
http://localhost:5173
```

---

# 16. Backend

The backend is implemented with FastAPI.

The main application is exposed through:

```text
app.main:app
```

The API is responsible for:

- Authentication
- User management
- Document management
- File validation
- Document processing
- RAG
- Chat
- Summaries
- Classification
- AI-agent functionality
- Database access

---

# 17. API

The backend exposes a REST API.

Typical API areas include:

```text
/api/v1/auth
/api/v1/documents
/api/v1/chat
/api/v1/summary
...
```

The exact endpoints depend on the current application implementation.

FastAPI automatically provides interactive documentation.

---

# 18. Environment Variables

Create an environment file based on `.env.example`.

A typical configuration contains variables similar to:

```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_platform

OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=qwen3:8b
VISION_MODEL=qwen2.5vl:7b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

REDIS_URL=redis://redis:6379/0

SECRET_KEY=change-this-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Additional variables may be required depending on the current implementation.

### Important

Never commit real secrets to Git.

Do not commit:

```text
.env
```

if it contains real credentials or secrets.

Instead, commit:

```text
.env.example
```

with safe placeholder values.

---

# 19. Installation and Setup

## 19.1 Prerequisites

Install the following:

- Git
- Docker Desktop
- Node.js
- npm
- Python 3.12+ if running backend components outside Docker
- Sufficient disk space for AI models
- Sufficient RAM for local LLM inference

Because Ollama models can be large, ensure the machine has adequate resources.

---

# 20. Running the Project

## Step 1 — Clone the repository

```bash
git clone <repository-url>
cd saas-ia-platform
```

---

## Step 2 — Configure environment variables

Create:

```text
.env
```

from:

```text
.env.example
```

---

## Step 3 — Start Docker services

Use:

```bash
docker compose up -d
```

If your installation uses the legacy command:

```bash
docker-compose up -d
```

Both commands depend on the installed Docker Compose version.

---

## Step 4 — Check running containers

```bash
docker compose ps
```

You should see the configured services, such as:

```text
api
postgres
redis
celery
ollama
```

---

## Step 5 — Check API

Open:

```text
http://localhost:8000
```

and the interactive Swagger documentation:

```text
http://localhost:8000/docs
```

---

## Step 6 — Start frontend

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 21. Database Migrations

The project uses Alembic for database migrations.

Before starting development, make sure the database is running.

To apply migrations:

```bash
docker compose exec api alembic upgrade head
```

To see migration history:

```bash
docker compose exec api alembic history
```

To see the current migration:

```bash
docker compose exec api alembic current
```

To create a migration after changing SQLAlchemy models:

```bash
docker compose exec api alembic revision --autogenerate -m "describe the change"
```

Then apply it:

```bash
docker compose exec api alembic upgrade head
```

### Recommended workflow

When changing a model:

```text
Modify SQLAlchemy model
        │
        ▼
Generate Alembic migration
        │
        ▼
Review migration
        │
        ▼
alembic upgrade head
        │
        ▼
Database updated
```

Do not rely on modifying models alone to change an existing database.

---

# 22. API Documentation

FastAPI provides automatic OpenAPI documentation.

Open:

```text
http://localhost:8000/docs
```

This provides an interactive interface for testing API endpoints.

Alternative documentation:

```text
http://localhost:8000/redoc
```

The Swagger UI is particularly useful during development because authenticated and unauthenticated endpoints can be tested directly.

---

# 23. Testing the System

A basic end-to-end test should follow this sequence:

```text
1. Register user
        ↓
2. Login
        ↓
3. Receive JWT
        ↓
4. Upload document
        ↓
5. Check document status
        ↓
6. Wait for processing
        ↓
7. Verify extracted text
        ↓
8. Verify chunks
        ↓
9. Verify embeddings
        ↓
10. Ask document question
        ↓
11. Verify RAG response
```

---

# 24. RAG Evaluation

The project includes a dedicated evaluation framework for measuring retrieval and answer quality.

Evaluation cases are stored in JSONL format.

Each case can contain fields such as:

```json
{
  "id": "example-case",
  "document_id": 123,
  "question": "What is the project title?",
  "expected_answer": "Example project",
  "expected_chunk_ids": [374],
  "expected_chunk_indexes": [8],
  "answer_contains": ["Example project"]
}
```

---

## 24.1 Retrieval Metrics

The evaluation framework calculates:

### Hit Rate

Measures whether at least one relevant chunk was retrieved.

```text
Hit = relevant chunk retrieved
```

---

### Recall

Measures how many expected relevant chunks were retrieved.

```text
Recall =
relevant retrieved chunks
-------------------------
expected relevant chunks
```

---

### Mean Reciprocal Rank

MRR evaluates how high the first relevant result appears.

For example:

```text
Relevant result at rank 1 → 1.0
Relevant result at rank 2 → 0.5
Relevant result at rank 3 → 0.333...
```

Higher rank positions therefore produce higher reciprocal-rank values.

---

## 24.2 Generation Metrics

The evaluation framework also calculates:

### Answer Contains Score

Measures the fraction of required terms found in the generated answer.

This is a lexical metric and should not be interpreted as a complete semantic correctness measure.

---

### Token F1

Measures lexical overlap between:

```text
Generated answer
```

and:

```text
Expected answer
```

It calculates:

```text
Precision
Recall
F1
```

Token F1 can penalize valid rewording or additional useful information because it is based on lexical overlap.

---

## 24.3 LLM Judge

The evaluation framework can also ask the configured LLM to evaluate the generated answer against the expected answer.

Run:

```bash
docker-compose exec -T api \
python -m app.evaluation.rag_eval \
evals/rag_eval.local.jsonl \
--limit 5 \
--threshold 0.7 \
--judge \
--output evals/rag_eval.local.judged.report.json
```

The `--judge` option automatically enables answer generation.

The judge uses:

```text
0
0.5
1
```

to represent different levels of correctness.

The resulting metric is an LLM-judged answer-correctness score.

### Important methodological limitation

The current judge compares:

```text
Question
Expected answer
Actual answer
```

It does not explicitly provide the retrieved context to the judge.

Therefore, this metric should not be described as a direct hallucination or grounding score.

---

# 25. RAG Evaluation Results

One evaluated 14-case dataset produced:

```json
{
  "case_count": 14,
  "retrieval_hit_rate": 1,
  "retrieval_recall": 1.0,
  "retrieval_mrr": 0.8809523809523809,
  "answer_contains_score": 0.8333333333333334,
  "answer_token_f1": 0.674839199332203,
  "answer_llm_judge_score": 0.9642857142857143
}
```

These values should be interpreted separately because they measure different aspects of the RAG system.

### Retrieval

```text
Hit Rate: 100%
Recall:   100%
MRR:      88.10%
```

This indicates that the relevant retrieval targets were successfully retrieved in the evaluated cases, although the first relevant result was not always ranked first.

### Answer quality

```text
Answer Contains: 83.33%
Token F1:        67.48%
LLM Judge:       96.43%
```

The difference between lexical metrics and LLM judgment illustrates an important limitation of purely lexical evaluation: an answer can be semantically correct while using different wording from the expected answer.

The evaluation also identified a case where the generated answer omitted some expected project capabilities, specifically Docker and REST API/FastAPI, resulting in a partial LLM-judge score.

---

# 26. Troubleshooting

## Docker containers do not start

Check:

```bash
docker compose ps
```

Then inspect logs:

```bash
docker compose logs api
```

For a specific service:

```bash
docker compose logs postgres
docker compose logs redis
docker compose logs celery
docker compose logs ollama
```

---

## API is not responding

Check:

```bash
docker compose ps
```

Then:

```bash
docker compose logs api
```

Verify that port `8000` is exposed.

Try:

```text
http://localhost:8000/docs
```

---

## PostgreSQL connection error

Check the PostgreSQL container:

```bash
docker compose logs postgres
```

Check the connection URL.

Inside Docker, the database hostname should normally be the Compose service name rather than:

```text
localhost
```

For example:

```text
postgres
```

instead of:

```text
localhost
```

---

## Ollama connection error

Check:

```bash
docker compose logs ollama
```

Verify:

```env
OLLAMA_URL=http://ollama:11434
```

when the backend is communicating with the Ollama container through the Docker network.

---

## Model is missing

Check installed models from the Ollama environment.

For example:

```bash
ollama list
```

The required models include:

```text
qwen3:8b
qwen2.5vl:7b
nomic-embed-text
```

The exact installation process depends on how Ollama is configured in Docker Compose.

---

## Frontend cannot reach backend

If React runs directly on the host:

```text
React → localhost:8000
```

is normally appropriate for browser requests.

Do not automatically use:

```text
http://api:8000
```

in browser-side frontend code.

`api` is a Docker-network service name and is primarily resolvable by other containers on that Docker network.

---

## Celery tasks are not running

Check:

```bash
docker compose logs celery
```

Then check Redis:

```bash
docker compose logs redis
```

The worker and API must be configured to communicate with the same Redis broker.

---

# 27. Development Workflow

A recommended development workflow is:

```text
1. Start Docker
       ↓
2. Start backend services
       ↓
3. Start React frontend
       ↓
4. Make code changes
       ↓
5. Test API
       ↓
6. Test frontend
       ↓
7. Check database
       ↓
8. Run evaluation/tests
       ↓
9. Create migration if models changed
       ↓
10. Commit changes
```

---

## Backend development

Useful commands:

```bash
docker compose ps
```

```bash
docker compose logs -f api
```

```bash
docker compose exec api bash
```

Run migrations:

```bash
docker compose exec api alembic upgrade head
```

---

## Frontend development

```bash
cd frontend
npm install
npm run dev
```

Build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

---

# 28. Production Considerations

The current development architecture should not automatically be considered production-ready.

Before production deployment, consider:

## Security

- Use strong secrets.
- Store secrets outside source control.
- Configure HTTPS.
- Restrict CORS.
- Validate uploaded files carefully.
- Limit upload sizes.
- Validate MIME types in addition to extensions.
- Protect internal services.
- Use secure password hashing.
- Configure JWT expiration appropriately.

---

## Database

- Use production PostgreSQL credentials.
- Configure backups.
- Monitor database size.
- Monitor vector indexes.
- Review pgvector indexing configuration.
- Use migrations consistently.

---

## AI infrastructure

Local Ollama inference can require substantial CPU/GPU/RAM resources.

Production deployment should consider:

- GPU availability
- Model memory requirements
- Concurrent requests
- Model loading time
- Request timeouts
- Worker count
- Queue length
- Resource isolation

---

## Background workers

Celery workers should be monitored for:

- Failed tasks
- Long-running tasks
- Queue size
- Retry behavior
- Worker availability

---

# 29. Security

Security is an important aspect of the application because users upload potentially private documents.

The system should enforce document ownership.

For example:

```python
Document.user_id == current_user.id
```

should be checked before returning, modifying, or deleting a document.

Passwords should never be stored as plain text.

JWT secrets should never be hard-coded into source code.

Uploaded files should also be validated before processing.

---

# 30. Future Improvements

Potential improvements include:

- More advanced document classification
- Better OCR/extraction pipelines
- More robust chunking strategies
- Hybrid keyword + vector search
- Reranking retrieved chunks
- Improved RAG grounding evaluation
- Context-aware conversation memory
- Streaming LLM responses
- Better agent tool selection
- More comprehensive automated tests
- Celery retry policies
- Task monitoring
- Redis caching strategies
- Production deployment
- GPU optimization
- Multi-user collaboration
- Fine-grained document permissions
- Improved evaluation datasets
- Automated RAG regression testing
- More robust structured-output validation
- Better citation/page references in generated answers

---

# 31. Project Status

The platform contains the main components required for an intelligent document automation SaaS application:

```text
                 ┌─────────────────────────┐
                 │ SaaS AI Document        │
                 │ Automation Platform     │
                 └────────────┬────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
      Frontend             Backend              AI
      React              FastAPI             Ollama
          │                   │                   │
          │          ┌────────┼────────┐          │
          │          │        │        │          │
          ▼          ▼        ▼        ▼          ▼
       Browser   PostgreSQL Redis   Celery    LLM/Vision
                       │
                       ▼
                    pgvector
                       │
                       ▼
                 Semantic Search
                       │
                       ▼
                      RAG
                       │
                       ▼
                AI Agent / Chat
```

The project therefore combines:

- Full-stack web development
- REST API development
- Relational database management
- Vector databases
- Authentication
- Document processing
- Natural language processing
- Large language models
- Vision-language models
- Embeddings
- Retrieval-Augmented Generation
- AI agents
- Background task processing
- Containerization
- Automated evaluation

---

# 32. Quick Reference

## Start all Docker services

```bash
docker compose up -d
```

## Stop services

```bash
docker compose down
```

## View services

```bash
docker compose ps
```

## View API logs

```bash
docker compose logs -f api
```

## View Celery logs

```bash
docker compose logs -f celery
```

## Apply migrations

```bash
docker compose exec api alembic upgrade head
```

## Open API documentation

```text
http://localhost:8000/docs
```

## Start frontend

```bash
cd frontend
npm run dev
```

## Build frontend

```bash
cd frontend
npm run build
```

## Run RAG evaluation

```bash
docker-compose exec -T api \
python -m app.evaluation.rag_eval \
evals/rag_eval.local.jsonl \
--limit 5 \
--threshold 0.7 \
--judge \
--output evals/rag_eval.local.judged.report.json
```

---

# 33. Core Concepts

For developers joining the project, the most important concepts are:

| Concept | Role |
|---|---|
| React | Frontend UI |
| TypeScript | Frontend type safety |
| Vite | Frontend development/build tool |
| FastAPI | Backend REST API |
| Pydantic | API schemas and validation |
| SQLAlchemy | Database ORM |
| PostgreSQL | Persistent relational storage |
| pgvector | Vector storage/search |
| Alembic | Database migrations |
| JWT | Authentication |
| Ollama | Local AI model serving |
| Qwen3 | Main LLM |
| Qwen2.5-VL | Vision/document model |
| nomic-embed-text | Embedding model |
| RAG | Retrieval + generation |
| Redis | Message broker / operational cache |
| Celery | Background task execution |
| Docker | Containerization |
| Docker Compose | Multi-service orchestration |

---

# 34. Summary

The project is designed around a pipeline that transforms unstructured documents into an intelligent, searchable knowledge base.

The complete concept can be summarized as:

```text
                     USER
                       │
                       ▼
              React + TypeScript
                       │
                       ▼
                    FastAPI
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
      PostgreSQL      Redis       Ollama
          │            │            │
       pgvector     Celery      AI Models
          │            │            │
          │            ▼            │
          │       Background        │
          │       Processing        │
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
              Document Processing
                       │
                       ▼
                 Text Extraction
                       │
                       ▼
                    Chunking
                       │
                       ▼
                  Embeddings
                       │
                       ▼
                Vector Storage
                       │
                       ▼
                Semantic Search
                       │
                       ▼
                      RAG
                       │
                       ▼
                   AI Agent
                       │
                       ▼
                  User Answer
```

The main architectural principle is to separate responsibilities:

- **React** handles the user interface.
- **FastAPI** handles HTTP/API logic.
- **Pydantic schemas** validate API input/output.
- **SQLAlchemy models** represent database entities.
- **PostgreSQL** stores persistent application data.
- **pgvector** stores and searches embeddings.
- **Redis** transports background task messages.
- **Celery** executes long-running background jobs.
- **Ollama** serves local AI models.
- **RAG** retrieves relevant document information before generation.
- **The AI agent** provides a higher-level intelligent interface.
- **Docker Compose** coordinates the infrastructure services.

This separation makes the system easier to develop, maintain, test, and extend.