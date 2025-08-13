from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.models.llm_router import LLMRouter
from app.tools import web_search

router = APIRouter(prefix='/external-insights', tags=['external'])
llm = LLMRouter()

class InsightsRequest(BaseModel):
    query: str
    max_results: int = 5
    temperature: float = 0.2

@router.post('')
async def external_insights(req: InsightsRequest) -> Dict[str, Any]:
    try:
        result = web_search.search(req.query, max_results=req.max_results)
    except Exception as e:
        raise HTTPException(400, f'Web search failed: {e}')
    snippets = []
    for item in result.get('results', [])[: req.max_results]:
        title = item.get('title') or 'source'
        content = item.get('content') or item.get('snippet') or ''
        url = item.get('url') or ''
        snippets.append(f'- {title}: {content[:500]} (source: {url})')
    research_block = '\n'.join(snippets)
    provider, model = llm.pick('general')
    synthesis = await llm.chat([
        {'role':'user','content': 'Synthesize neutrally with 3 takeaways and 3 risks:\n' + research_block}
    ], provider=provider, model=model, temperature=req.temperature)
    return {'query': req.query, 'model': model, 'provider': provider, 'synthesis': synthesis,
            'sources': [{'title': (i.get('title') or 'source'), 'url': (i.get('url') or '')} for i in result.get('results', [])[: req.max_results]]}
