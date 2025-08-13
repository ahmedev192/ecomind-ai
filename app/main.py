from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import agent, analyze, documents, external
from app.models.llm_router import LLMRouter

app = FastAPI(title='AI Agent Backend', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(agent.router)
app.include_router(analyze.router)
app.include_router(documents.router)
app.include_router(external.router)

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/models')
def models():
    router = LLMRouter()
    return {'providers': router.providers(), 'defaults': router.default_models()}
