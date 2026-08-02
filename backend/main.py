from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, extract, auth

app = FastAPI(
    title="Smart Extractor & Chat Service",
    description="Production-grade FastAPI service with SSE Streaming, DB & Auth",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router) # Newly added
app.include_router(chat.router)
app.include_router(extract.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Smart Extractor & Chat"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)