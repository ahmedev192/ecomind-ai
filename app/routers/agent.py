from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from app.models.llm_router import LLMRouter
from app.tools import web_search
from app.memory import store

router = APIRouter(prefix='/chat-agent', tags=['agent'])
router_llm = LLMRouter()

class AgentRequest(BaseModel):
    session_id: str = Field(..., description='Conversation session id for memory')
    message: str
    use_web: bool = False
    temperature: float = 0.2

class AgentResponse(BaseModel):
    response: str
    used_provider: str
    used_model: str
    citations: Optional[List[Dict[str, str]]] = None

SYSTEM_PROMPT = (
    'You are a focused AI agent. Be concise, cite sources only when web tool is used. '
    'Use stepwise reasoning internally but return a clean, actionable answer.'
)

@router.post('', response_model=AgentResponse)
async def chat_agent(req: AgentRequest) -> AgentResponse:
    history = store.get_thread(req.session_id)
    messages: List[Dict[str, str]] = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': req.message})

    citations = None
    if req.use_web:
        try:
            result = web_search.search(req.message, max_results=5)
            snippets = []
            citations = []
            for item in result.get('results', [])[:5]:
                title = item.get('title') or 'source'
                url = item.get('url') or ''
                summary = item.get('content') or item.get('snippet') or ''
                snippets.append(f'- {title}: {summary[:500]}')
                citations.append({'title': title, 'url': url})
            web_context = '\n'.join(snippets) or 'No results.'
            messages.append({'role': 'user', 'content': 'Use this research to answer accurately:\n' + web_context})
        except Exception as e:
            messages.append({'role': 'user', 'content': f'(Web search failed: {e})'})

    provider, model = router_llm.pick('chat')
    answer = await router_llm.chat(messages, provider=provider, model=model, temperature=req.temperature)

    store.append_message(req.session_id, 'user', req.message)
    store.append_message(req.session_id, 'assistant', answer)

    return AgentResponse(response=answer, used_provider=provider, used_model=model, citations=citations)
