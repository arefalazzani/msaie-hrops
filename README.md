# Vendelligent HR Agent

Agentic HR assistant using RAG, MCP, and LLM-based
agent orchestration.

## Technology Stack

- Python 3.14
- FastAPI
- LangChain / LangGraph (planned)
- ChromaDB (planned)
- Python MCP SDK (planned)
- GroqCloud (planned)
- Render (planned)

## Local Setup

1. Create a Python 3.14 virtual environment.
2. Activate the environment.
3. Install dependencies:

   pip install -r requirements.txt

4. Start the application:

   uvicorn app.main:app --reload

5. Open http://localhost:8000/health

## Run Tests

python -m pytest -v

## Project Status

Milestone 1: Project Foundation