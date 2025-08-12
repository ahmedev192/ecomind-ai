# app/hubspot_client.py
import os
import requests

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
BASE_URL = "https://api.hubapi.com"


def add_contact(email):
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    data = {"properties": {"email": email}}
    r = requests.post(url, json=data, headers=headers)
    return r.json()


def get_contact(email):
    url = f"{BASE_URL}/crm/v3/objects/contacts/search"
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    data = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }]
    }
    r = requests.post(url, json=data, headers=headers)
    return r.json()
