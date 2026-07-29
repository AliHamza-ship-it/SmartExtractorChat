# ⚡ Smart Extractor & Chat Service

A full-stack, production-grade LLM application built with FastAPI, OpenRouter, and a Glassmorphism React frontend.

## ✨ Key Features
- **Streaming Chat Endpoint (`/api/chat`)**: Server-Sent Events (SSE) streaming with configurable system prompts.
- **Self-Correcting JSON Extractor (`/api/extract`)**: Converts unstructured text into Pydantic-validated JSON with automatic retry loops and feedback on failure.
- **Token & Cost Tracking**: Calculates token usage and estimated API cost per request.
- **Glassmorphism UI**: High-end translucent design with glow effects and clean tabbed layout.
- **Prompt Eval Script**: Evaluates extraction accuracy across a 10-item test benchmark.

---

## 🚀 Quickstart Guide

### 1. Setup Environment & Virtualenv
```bash
# Clone or create directory
cd smart-extractor-chat

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
2. Configure Environment Variables
   insert your OpenRouter API Key:

Bash
3. Run the Backend API
Bash
uvicorn backend.main:app --reload --port 8000
Interactive API Docs: http://localhost:8000/docs

4. Run the Frontend (React + Vite)
Open a new terminal window:

Bash
cd frontend
npm install
npm run dev
Access UI: http://localhost:3000

5. Run the 10-Item Prompt Evaluation Benchmark
Bash
python scripts/eval.py

---

## 🏃 How to Run Everything

1. **Backend**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn backend.main:app --reload --port 8000
2. **Frontend**:

Bash
cd frontend
npm install
npm run dev
3. **Evaluation Test Suite**:

Bash
python scripts/eval.py