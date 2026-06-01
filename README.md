# InvoSense – Intelligent Invoice Processing & RAG Chatbot
A **full‑stack AI‑powered application** that lets you upload invoices, extracts key data via OCR, classifies documents, validates totals, stores results in SQLite, and provides a **policy/knowledge‑base chatbot** powered by Google Gemini (RAG) for on‑demand Q&A.
---
## 🎯 Project Highlights
|
 Feature 
|
 Description 
|
|
---------
|
-------------
|
|
**
OCR extraction
**
|
 Uses 
**
Tesseract
**
 (via 
`sentence‑transformers`
 embeddings) to read PDFs & images. 
|
|
**
Document classification
**
|
 Detects 
*
Valid Invoice
*
, 
*
Ambiguous
*
, or 
*
Not an Invoice
*
 with confidence scores. 
|
|
**
Math validation
**
|
 Automatically checks that line‑item totals add up correctly. 
|
|
**
SQLite persistence
**
|
 All extracted data lives in 
`backend/invosense.db`
. 
|
|
**
Dynamic Dashboard
**
|
 Visual analytics (spending trends, upload history) built with 
**
React
**
 & 
**
Recharts
**
. 
|
|
**
RAG Chatbot
**
|
 Upload policy documents, ask natural‑language questions – the backend retrieves relevant chunks from a local ChromaDB vector store and answers using 
**
Gemini‑Flash
**
. 
|
|
**
Docker‑ready
**
|
 Simple 
`docker compose`
 (backend + frontend) for production deployments. 
|
|
**
Cross‑platform
**
|
 Runs on Windows (tested) and Linux/macOS with minimal changes. 
|
---
## 📦 Quick Start (Windows)
> **Prerequisites**  
> * Python 3.12+ (installed)  
> * Node 20+ (for the frontend)  
> * **Tesseract OCR** – download the 64‑bit installer from the [UB Mannheim repo](https://github.com/UB-Mannheim/tesseract/wiki) and note the install path (e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`).  
1. **Clone the repo** (you already have it locally)  
   ```powershell
   git clone https://github.com/jennifer2006-github/InvoSense.git
   cd InvoSense
Backend setup

powershell


cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Create a .env file (or edit the existing one) and add:


GEMINI_API_KEY=YOUR_GEMINI_KEY
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
Run the API

powershell


uvicorn main:app --reload
Frontend setup
Open a new terminal:

powershell


cd ..\frontend
npm install
npm run dev
The app will be reachable at http://localhost:5173.

Upload a policy document (optional)
Navigate to the Policy Chatbot tab, upload a PDF/DOCX, then ask questions like:

What is the refund policy for returned items?
🛠️ Development & Testing
Run unit tests (backend):

powershell


pytest
Add new routes – see backend/routes/ for examples (upload.py, invoice.py, chat.py).

Add new React pages – place components under frontend/src/pages/ and update the router in frontend/src/App.jsx.

Update the RAG pipeline – modify backend/services/rag.py:

Change the embedding model (SentenceTransformer('all-MiniLM-L6-v2') by default).
Adjust the ChromaDB collection name or storage path (backend/chroma_db/).
📚 API Overview
Endpoint	Method	Description
/api/upload	POST	Upload an invoice image/PDF; returns extracted fields & classification.
/api/invoices	GET	List all processed invoices with timestamps and confidence.
/api/chat	POST	Ask a question to the policy RAG chatbot; returns answer and source snippets.
/api/analytics	GET	Summary stats for dashboards (total spend, invoices per day, etc.).
Reference the OpenAPI docs at http://localhost:8000/docs when the server is running.

