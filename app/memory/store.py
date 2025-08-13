from __future__ import annotations
import os, json
from typing import List, Dict, Any
from app.config import settings

os.makedirs(os.path.dirname(settings.MEMORY_PATH), exist_ok=True)
if not os.path.exists(settings.MEMORY_PATH):
    with open(settings.MEMORY_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f)

def _load() -> Dict[str, Any]:
    with open(settings.MEMORY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save(data: Dict[str, Any]) -> None:
    with open(settings.MEMORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_message(session_id: str, role: str, content: str) -> None:
    data = _load()
    thread: List[Dict[str, str]] = data.get(session_id, [])
    thread.append({'role': role, 'content': content})
    data[session_id] = thread[-50:]
    _save(data)

def get_thread(session_id: str) -> List[Dict[str, str]]:
    data = _load()
    return data.get(session_id, [])

def reset(session_id: str) -> None:
    data = _load()
    data[session_id] = []
    _save(data)
