from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import modular routers
from api.routes import learn, quiz, stream

app = FastAPI(
    title="Agentic Adaptive Learning System API",
    description="Backend API for adaptive content and quiz generation",
    version="1.0.0"
)

# ── CORS Configuration ─────────────────────────────────────────────────────────
# Essential for allowing the Streamlit frontend (usually on port 8501)
# to communicate with the FastAPI backend (usually on port 8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ───────────────────────────────────────────────────────────
app.include_router(learn.router)
app.include_router(quiz.router)
app.include_router(stream.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to the Adaptive Learning System API",
        "docs": "/docs"
    }

if __name__ == "__main__":
    # Provides a default entry point if run directly via 'python api/main.py'
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
