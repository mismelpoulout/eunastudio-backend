import requests
import hashlib
import os

FLOW_API_KEY = os.getenv("FLOW_API_KEY")
FLOW_SECRET = os.getenv("FLOW_SECRET")
FLOW_URL = "https://www.flow.cl/api/payment/create"

def create_flow_payment(email, name, amount, concept):
    payload = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": f"EUNA-{email}",
        "subject": concept,
        "currency": "CLP",
        "amount": amount,
        "email": email,
        "urlConfirmation": "https://eunastudio.cl/confirm",
        "urlReturn": "https://eunastudio.cl/return"
    }

    payload["s"] = sign_payload(payload)

    res = requests.post(FLOW_URL, data=payload)
    data = res.json()

    return data.get("token")

def sign_payload(payload):
    raw = "&".join(f"{k}={payload[k]}" for k in sorted(payload))
    return hashlib.sha256((raw + FLOW_SECRET).encode()).hexdigest()