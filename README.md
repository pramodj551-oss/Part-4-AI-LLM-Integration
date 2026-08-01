# Incident Knowledge Assistant (RAG)

**Capstone Project — Part 4: AI / LLM Integration**

An end-to-end Retrieval-Augmented Generation (RAG) application that combines FAISS vector search, Sentence Transformers, large language models (LLMs), and Streamlit to provide intelligent answers from an incident knowledge base.

The system retrieves the most relevant incident documents using semantic search and generates context-aware responses through an LLM, making it suitable for IT support, cybersecurity knowledge management, and enterprise helpdesk automation.

---

## Project Overview

The Incident Knowledge Assistant solves the limitations of traditional keyword search over large incident repositories. Instead of matching only keywords, the application understands the *semantic meaning* of user queries through vector embeddings.

**Workflow:**

```
User Question → Embedding Generation → FAISS Semantic Search → Context Retrieval → LLM Response Generation → Streamlit UI
```

This architecture significantly improves answer quality compared to conventional search systems.

---

## Key Features

- Retrieval-Augmented Generation (RAG) pipeline
- Semantic search using FAISS
- SentenceTransformer embeddings
- Ollama local LLM support
- Modular Python architecture
- Interactive Streamlit dashboard
- Incident search interface
- Knowledge base explorer
- Analytics dashboard
- Production-ready logging
- Configurable parameters
- Easy GitHub deployment

---

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | Streamlit |
| Embeddings | Sentence Transformers |
| Vector Database | FAISS |
| LLM | Ollama |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| Logging | Python Logging |
| Version Control | Git & GitHub |

---

## Project Structure

```
Incident-Knowledge-Assistant/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
│
├── data/
│   └── employee_attrition.csv
│
├── vector_store/
│   ├── faiss.index
│   └── documents.pkl
│
├── pages/
│   ├── Incident_Search.py
│   ├── Knowledge_Base.py
│   └── Analytics.py
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── llm.py
│   └── chatbot.py
│
└── outputs/
    └── logs/
```

---

## Core Workflow

1. Load incident dataset
2. Generate sentence embeddings
3. Build FAISS vector index
4. Retrieve relevant documents
5. Build retrieval context
6. Generate LLM response
7. Display results in the Streamlit dashboard

---

## Installation

### Prerequisites

Before running the project, ensure the following are installed:

- Python 3.11 or later
- Git
- Ollama
- Visual Studio Code (recommended)

### Clone the Repository

```bash
git clone https://github.com/pramodj551-oss/Part4-AI-Cybersecurity-Assistant.git
cd Part4-AI-Cybersecurity-Assistant
```

### Create a Virtual Environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Install Ollama

Download and install Ollama from [ollama.com/download](https://ollama.com/download), then verify the installation:

```bash
ollama --version
```

### Download an LLM Model

Example using Gemma:

```bash
ollama pull gemma3:4b
```

Or use another supported model:

```bash
ollama pull llama3.2
ollama pull mistral
ollama pull qwen2.5
```

---

## Project Configuration

Update configuration values in `src/config.py`, including:

- Dataset location
- FAISS index path
- Embedding model
- Ollama model name
- Number of retrieved documents (`TOP_K_RESULTS`)
- Logging configuration

---

## Prepare the Knowledge Base

Place the incident dataset in the project's data directory:

```
data/
└── employee_attrition.csv
```

Generate embeddings and build the FAISS index before launching the application.

---

## Run the Application

```bash
streamlit run app.py
```

The dashboard will be available in your browser at the default local Streamlit address after startup.

---

## RAG Architecture

The application follows a Retrieval-Augmented Generation (RAG) workflow to answer user questions using the organization's incident knowledge base.

```
User Query
     │
     ▼
SentenceTransformer Embedding
     │
     ▼
FAISS Vector Search
     │
     ▼
Top-K Relevant Documents
     │
     ▼
Context Builder
     │
     ▼
Ollama Large Language Model
     │
     ▼
AI-Generated Response
     │
     ▼
Streamlit User Interface
```

This approach reduces hallucinations by grounding the LLM with relevant incident documents retrieved from the vector database.

---

## Core Modules

### `src/data_loader.py`
- Loading the incident dataset
- Dataset validation
- Handling missing values
- Returning clean data for embedding generation

### `src/embeddings.py`
- Loading the SentenceTransformer model
- Generating document embeddings
- Batch embedding generation
- Embedding validation

### `src/vector_store.py`
- Creating the FAISS index
- Saving the vector database
- Loading an existing index
- Performing similarity search

### `src/retriever.py`
- Converting user queries into embeddings
- Retrieving top-K relevant documents
- Building LLM context
- Returning retrieval metadata

### `src/llm.py`
- Connecting to the Ollama server
- Sending prompts to the selected LLM
- Receiving AI-generated responses
- Managing prompt templates and inference settings

### `src/chatbot.py`
- Coordinating the complete RAG pipeline
- Retrieving relevant context
- Calling the LLM
- Returning the final answer
- Handling conversation flow and errors

---

## Streamlit Pages

### Home (`app.py`)
- Application entry point
- Sidebar navigation
- System overview
- Health status

### Incident Search
- Natural language question answering
- Semantic incident search
- Retrieved document preview
- AI-generated response
- Retrieval score display

### Knowledge Base
- Browse incident records
- Search and filter documents
- Dataset statistics
- Document preview
- Export functionality

### Analytics
- Knowledge base metrics
- Embedding statistics
- FAISS index information
- Retrieval analytics
- Interactive visualizations

---

## Application Workflow

1. Load the incident dataset.
2. Generate vector embeddings using SentenceTransformers.
3. Build or load the FAISS vector index.
4. Accept a user question from the Streamlit interface.
5. Convert the question into an embedding.
6. Retrieve the top-K most relevant documents.
7. Build a context from the retrieved documents.
8. Send the context and user question to the Ollama LLM.
9. Display the generated answer along with retrieval details.

---

## Example Questions

You can ask questions such as:

- How do I reset my password?
- How do I connect to the VPN?
- What is the incident escalation process?
- How do I report a phishing email?
- What should I do if my account is locked?
- Explain the password policy.
- How can I request software installation?
- What are the steps to resolve a network outage?

---

## Future Enhancements

The project can be extended with:

- Conversation memory for multi-turn chat
- Hybrid search (BM25 + FAISS)
- Metadata filtering
- User authentication
- Role-based access control
- Feedback collection
- Knowledge base management portal
- Document upload from the UI
- Support for multiple LLM providers
- Docker deployment
- Cloud deployment (AWS, Azure, GCP)

---

## Troubleshooting

**FAISS index not found**
Ensure the vector database has been created before running the application.

**Ollama connection error**
Verify that the Ollama service is running:

```bash
ollama serve
```

Also ensure the configured model has been downloaded.

**Missing Python packages**
Install all required dependencies again:

```bash
pip install -r requirements.txt
```

**Streamlit application not starting**
Verify the installation and run:

```bash
streamlit run app.py
```

---

## License

This project is released under the MIT License. See the `LICENSE` file for complete license information.

---

## Author

**Pramod Prakash Jadhav**
AI/ML Developer | Security Analyst

GitHub: [github.com/pramodj551-oss](https://github.com/pramodj551-oss)

---

## Acknowledgements

This project was developed as part of the Applied Artificial Intelligence & Machine Learning Capstone Project.

Technologies and libraries used include:

- Python
- Streamlit
- Pandas
- NumPy
- Sentence Transformers
- FAISS
- Ollama
- Plotly
- Scikit-learn
- Git & GitHub

---

## Project Status

| | |
|---|---|
| **Current Version** | 1.0.0 |
| **Development Status** | Production Ready |
| **Architecture** | Retrieval-Augmented Generation (RAG) |
| **Deployment Target** | Streamlit + Ollama + FAISS |

---

## Repository Checklist

- ✅ Modular project architecture
- ✅ Production-ready Python code
- ✅ Streamlit web application
- ✅ FAISS vector database
- ✅ SentenceTransformer embeddings
- ✅ Ollama LLM integration
- ✅ Semantic document retrieval
- ✅ Interactive analytics dashboard
- ✅ Logging and configuration management
- ✅ GitHub-ready project structure

---

*Thank you for exploring the Incident Knowledge Assistant (RAG) project!*
