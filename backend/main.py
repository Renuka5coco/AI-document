from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import shutil
import uuid
from ocr_service import extract_text
from ai_extractor import extract_structured_data
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    _, ext = os.path.splitext(file.filename)
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)                        
        
    extracted_text = extract_text(file_path)
    structured_data = extract_structured_data(extracted_text)
        
    return {
        "status": "success",
        "filename": unique_filename,
        "data": structured_data
    }

@app.get("/documents")
def get_documents():
    documents = []
    for filename in os.listdir(PROCESSED_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(PROCESSED_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                documents.append({"filename": filename, "data": data})
            except Exception:
                pass
    return {"documents": documents}
