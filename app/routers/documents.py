from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any
from app.models.llm_router import LLMRouter
from PyPDF2 import PdfReader

router = APIRouter(prefix='/process-document', tags=['documents'])
llm = LLMRouter()

def read_file_text(upload: UploadFile) -> str:
    name = upload.filename.lower()
    if name.endswith('.txt'):
        return upload.file.read().decode('utf-8', errors='ignore')
    if name.endswith('.pdf'):
        reader = PdfReader(upload.file)
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or '')
        return '\n'.join(text)
    raise HTTPException(400, 'Only .txt or .pdf files are supported.')

@router.post('')
async def process_document(file: UploadFile = File(...), purpose: str = Form(default='general')) -> Dict[str, Any]:
    raw_text = read_file_text(file)
    if not raw_text.strip():
        raise HTTPException(400, 'Could not extract text from the document.')
    provider, model = llm.pick('long_context')
    summary = await llm.chat([
        {'role':'user','content': f'Summarize for {purpose}.\n\n' + raw_text[:12000]}
    ], provider=provider, model=model, temperature=0.2)
    keypoints = await llm.chat([
        {'role':'user','content': 'List 5-8 bullet key points.\n\n' + raw_text[:12000]}
    ], provider=provider, model=model, temperature=0.2)
    chunks, chunk_size = [], 3000
    for i in range(0, min(len(raw_text), 24000), chunk_size):
        chunks.append(raw_text[i:i+chunk_size])
    return {'summary': summary, 'key_points': keypoints, 'chunks': chunks}
