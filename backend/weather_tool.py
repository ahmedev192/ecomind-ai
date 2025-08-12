# app/weather_tool.py
import requests
import os

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    r = requests.get(url)
    return r.json()
