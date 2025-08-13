from __future__ import annotations
from typing import Optional, List, Dict, Any
from app.config import settings

class LLMRouter:
    def __init__(self) -> None:
        self.available = {
            'openai': bool(settings.OPENAI_API_KEY),
            'gemini': bool(settings.GEMINI_API_KEY),
            'anthropic': bool(settings.ANTHROPIC_API_KEY),
        }

    def providers(self) -> Dict[str, bool]:
        return self.available

    def default_models(self) -> Dict[str, Optional[str]]:
        return {
            'openai': settings.OPENAI_MODEL if self.available['openai'] else None,
            'gemini': settings.GEMINI_MODEL if self.available['gemini'] else None,
            'anthropic': settings.ANTHROPIC_MODEL if self.available['anthropic'] else None,
        }

    def pick(self, purpose: str = 'general') -> tuple[str, str]:
        if purpose in {'code','long_context'} and self.available['gemini']:
            return ('gemini', settings.GEMINI_MODEL)
        if self.available['openai']:
            return ('openai', settings.OPENAI_MODEL)
        if self.available['gemini']:
            return ('gemini', settings.GEMINI_MODEL)
        if self.available['anthropic']:
            return ('anthropic', settings.ANTHROPIC_MODEL)
        raise RuntimeError('No LLM providers are configured.')

    async def chat(self, messages: List[Dict[str, str]], provider: Optional[str]=None, model: Optional[str]=None, temperature: float=0.2) -> str:
        if provider is None or model is None:
            provider, model = self.pick('chat')

        if provider == 'openai':
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return resp.choices[0].message.content

        if provider == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model_obj = genai.GenerativeModel(model)
            history = [{'role': m['role'], 'parts': [m['content']]} for m in messages[:-1]]
            last = messages[-1]['content']
            chat = model_obj.start_chat(history=history)
            resp = chat.send_message(last, generation_config={'temperature': temperature})
            return resp.text

        if provider == 'anthropic':
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            sys_prompt = ''
            convo = []
            for m in messages:
                if m['role'] == 'system':
                    sys_prompt += m['content'] + '\n'
                else:
                    convo.append({'role': m['role'], 'content': m['content']})
            resp = client.messages.create(
                model=model,
                system=sys_prompt or None,
                max_tokens=1024,
                temperature=temperature,
                messages=convo,
            )
            return resp.content[0].text

        raise ValueError(f'Unknown provider: {provider}')
