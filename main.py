# app/main.py
from fastapi import FastAPI, Body
from xero_client import get_garden_costs
from hubspot_client import add_contact, get_contact
from ai_analysis import analyze_garden
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.post("/track-garden")
async def track_garden(data: dict = Body(...)):
    plants = data.get("plants", 0)
    water = data.get("water", 0)
    contact_email = data.get("email")

    # 1. Get costs from Xero
    costs = get_garden_costs()

    # 2. Add contact to HubSpot (optional)
    if contact_email:
        add_contact(contact_email)

    # 3. AI analysis
    ai_result = analyze_garden(plants, water, costs)

    return {
        "plants": plants,
        "water": water,
        "costs": costs,
        "analysis": ai_result
    }
