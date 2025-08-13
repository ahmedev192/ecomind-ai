from __future__ import annotations
import requests

def current_weather(lat: float, lon: float) -> dict:
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true'
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json().get('current_weather', {})
