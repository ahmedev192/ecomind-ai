from __future__ import annotations
from typing import Dict, Any
import requests
from app.config import settings

TAVILY_URL = 'https://api.tavily.com/search'

def search(query: str, max_results: int = 5) -> Dict[str, Any]:
    if not settings.TAVILY_API_KEY:
        raise RuntimeError('TAVILY_API_KEY is not set.')
    payload = {
        'api_key': settings.TAVILY_API_KEY,
        'query': query,
        'max_results': max_results,
        'search_depth': 'advanced',
        'include_answer': True,
        'include_images': False,
        'include_raw_content': False,
    }
    r = requests.post(TAVILY_URL, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()
