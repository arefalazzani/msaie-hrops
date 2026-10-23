from fastapi import FastAPI

app = FastAPI(
    title="Vendelligent HR Agent",
    version="0.1.0",
    description="Agentic HR assistant with RAG and MCP"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "vendelligent-hr-agent"
    }