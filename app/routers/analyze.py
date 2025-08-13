from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.models.llm_router import LLMRouter

router = APIRouter(prefix='/analyze', tags=['analyze'])
llm = LLMRouter()

class AnalyzeRequest(BaseModel):
    task: str = Field(..., description='garden | requirements_extract | sales_insights_demo')
    payload: Dict[str, Any] = Field(default_factory=dict)
    temperature: float = 0.1

@router.post('')
async def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    task = req.task.lower()
    if task == 'garden':
        plants = req.payload.get('plants', 0)
        water = req.payload.get('water', 0.0)
        costs = req.payload.get('costs', 0.0)
        prompt = (
            'You are a garden operations analyst. Given the stats, compute simple KPIs and give short advice.\n\n'
            f'Plants: {plants}\nWater (L): {water}\nCosts ($): {costs}\n\n'
            'Return JSON with: kpis (dict), risks (list), tips (list).'
        )
        messages = [{'role':'user','content': prompt}]
        provider, model = llm.pick('general')
        text = await llm.chat(messages, provider=provider, model=model, temperature=req.temperature)
        return {'task':'garden', 'model': model, 'provider': provider, 'result_raw': text}

    if task == 'requirements_extract':
        text = req.payload.get('text') or ''
        if not text.strip():
            raise HTTPException(400, 'payload.text is required')
        prompt = (
            'Extract software requirements from the text. Return JSON with: '\
            'functional_requirements, nonfunctional_requirements, constraints, open_questions.\n\n' + text
        )
        messages = [{'role':'user','content': prompt}]
        provider, model = llm.pick('general')
        out = await llm.chat(messages, provider=provider, model=model, temperature=req.temperature)
        return {'task':'requirements_extract','model':model,'provider':provider,'result_raw':out}

    if task == 'sales_insights_demo':
        data = req.payload.get('data', [])
        prompt = 'Given sales records (JSON array), summarize trends, top products, anomalies, and 3 actions.\n' + str(data)
        messages = [{'role':'user','content': prompt}]
        provider, model = llm.pick('general')
        out = await llm.chat(messages, provider=provider, model=model, temperature=req.temperature)
        return {'task':'sales_insights_demo','model':model,'provider':provider,'result_markdown':out}

    raise HTTPException(400, f'Unknown task: {req.task}')
