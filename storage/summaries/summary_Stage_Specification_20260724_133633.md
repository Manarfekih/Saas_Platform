# Intelligent AI Agent for SaaS Document Automation

**Document Type:** Document

## Overview
This document outlines the development of an intelligent AI agent designed for SaaS document automation, created by Manar El Fakih Romdhane at the Higher Institute of Management of Sousse in Tunisia. The project focuses on building a platform that enables users to upload various document formats, extract content via OCR, and interact with stored data using a Retrieval-Augmented Generation (RAG) system. The platform operates within a Docker containerized environment, featuring a REST API built with FlaskAPI and leveraging technologies like Tesseract for OCR, LangChain for managing the RAG pipeline, and PostgreSQL with pgvector for semantic search capabilities. The system's architecture includes a layered design with frontend components, an API gateway, and backend services for document processing and chat functionality. Key workflows involve document upload, text extraction, classification, chunking, and embedding for semantic retrieval, while the chatbot integrates with vector stores to provide context-aware responses. The project is divided into six phases, starting with environment setup and concluding with Dockerization, ensuring a scalable and modular implementation.

## Key Information
**People:** Manar El Fakih Romdhane
**Organizations:** Tunisian Republic, Ministry of Higher Education and Scientific Research, University of Sousse, Higher Institute of Management of Sousse

## Detailed Sections

### Project Overview
- **Platform Functionality:** The platform allows users to upload documents in PDF, Word, and image formats, extracts content via OCR, stores documents, and enables interaction through RAG. It runs in a Docker container with a FlaskAPI-based REST API.

### System Architecture
- **Use Case Diagram:** The diagram defines user interactions including registration, login, document upload, viewing, and chat functionality.

### Technical Components
- **Class Diagram:** The diagram illustrates relationships between User, Document, Document_Chunk, ChatSession, and Message entities, with detailed attributes and associations.

### Technology Stack
- **Layered Architecture:** The system uses React for the frontend, FastAPI as the API gateway, Tesseract for OCR, LangChain for RAG orchestration, pgvector for vector storage, and PostgreSQL for relational data storage.

### Workflow Processes
- **Document Processing Flow:** Documents are uploaded, processed through OCR, classified, chunked, and embedded for storage. Users receive notifications upon completion.

### Project Phases
- **Development Stages:** The project is divided into six phases: environment setup, database and model creation, OCR integration, RAG pipeline development, API endpoint implementation, and Dockerization for deployment.
