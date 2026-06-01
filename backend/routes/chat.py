from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import os
from services.rag import add_document, ask_question
from services.ocr import extract_text_from_file

router = APIRouter(prefix="/api/chat")

UPLOAD_DIR = "uploads"


class ChatRequest(BaseModel):
    message: str


@router.post("/upload")
async def upload_knowledge_doc(file: UploadFile = File(...)):
    # Save file
    safe_name = file.filename.replace(' ', '_')
    file_path = os.path.join(UPLOAD_DIR, f"kb_{safe_name}")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Extract text using existing OCR/PDF service
    extracted = extract_text_from_file(file_path)
    text = extracted.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from document.")
        
    # Add to ChromaDB
    chunks_added = add_document(text, file.filename)
    
    return {"message": f"Successfully processed '{file.filename}'. Added {chunks_added} chunks to knowledge base."}


@router.post("/ask")
async def ask_chatbot(req: ChatRequest):
    if not req.message:
        raise HTTPException(status_code=400, detail="Message is required.")
        
    response = ask_question(req.message)
    return {"reply": response}
