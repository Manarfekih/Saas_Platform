# Intelligent AI Agent for SaaS Document Automation

**Document Type:** Document

## Overview
The document outlines a project developed by Manar El Fakih Romdhane at the University of Sousse, focusing on creating an intelligent AI agent for SaaS document automation. The system enables users to upload various file types, including PDFs, Word documents, and images, and extracts content using OCR technology. The platform stores documents and allows interaction through a Retrieval-Augmented Generation (RAG) pipeline, with all services running in a Dockerized environment. The architecture integrates a React frontend for user interaction, a FastAPI-based API gateway, and a PostgreSQL relational database for storing documents, metadata, and chat history. Key components include an OCR engine powered by Tesseract, a vector store using pgvector for semantic search, and LangChain for managing the RAG pipeline. The system processes uploaded files through a series of steps, including text extraction, classification, chunking, and embedding, while chat functionality leverages vector similarity searches to retrieve relevant document chunks for generating responses. The project is divided into six phases, starting with environment setup and concluding with Dockerization, ensuring a scalable and modular implementation.

## Key Information
**People:** Manar El Fakih Romdhane
**Organizations:** Tunisian Republic, Ministry of Higher Education and Scientific Research, University of Sousse, Higher Institute of Management of Sousse, Polytechnique SOUSSE

## Detailed Sections

### Project Overview
- **Saas IA platform:** Allows users to upload files, extract content via OCR, store documents, interact via RAG, and runs in Docker with a Flask API.

### Technical Architecture
- **Frontend (optional):** React-based user interface for document uploads and chat interactions.
- **API Gateway:** FastAPI (Python) handles requests and orchestrates services.
- **OCR Engine:** Tesseract + pytesseract extracts text from scanned images and PDFs.
- **LLM Orchestration:** LangChain manages prompt chaining and RAG pipeline operations.
- **Vector Store:** pgvector (PostgreSQL) stores embeddings for semantic search.
- **Relational DB:** PostgreSQL stores documents, metadata, users, and chat history.
- **Containerization:** Docker + Docker Compose packages and runs all services together.

### Document Processing Flow
- **Upload & Processing:** Users upload files via POST /api/v1/documents/upload, which are saved to disk and recorded in the database. OCR extracts text, which is classified, chunked, and embedded for storage in pgvector.

### RAG Query Flow
- **Chatbot Interaction:** Users send questions via POST /api/v1/chat/{session_id}/message. The query is vectorized, matched against stored embeddings, and combined with retrieved chunks to generate responses using GPT-4, Claude, or a local model.

### Project Phases
- **PHASE 1:** Environment Setup for development and testing.
- **PHASE 2:** Database and model design for data storage and structure.
- **PHASE 3:** OCR and document processing implementation.
- **PHASE 4:** RAG pipeline development using LangChain.
- **PHASE 5:** FastAPI endpoint creation for API integration.
- **PHASE 6:** Dockerization and final deployment of the system.

### Use Case & Class Diagrams
- **Use Case Diagram:** User interactions include registration, login, profile editing, document upload, viewing documents, and chat functionality.
- **Class Diagram:** Defines relationships between User, Document, Document_Chunk, ChatSession, and Message entities, with attributes like IDs, content, and embeddings.
