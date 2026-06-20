# services/paystack.py
from decimal import Decimal

import httpx
from app.core.config import settings

PAYSTACK_BASE = "https://api.paystack.co"
HEADERS = {
    "Authorization": f"Bearer {settings.paystack_secret_key}",
    "Content-Type": "application/json",
}

async def initialize_transaction(email: str, amount_naira: Decimal, reference: str, metadata: dict) -> dict:
    """Amount must be in kobo (1 NGN = 100 kobo)"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYSTACK_BASE}/transaction/initialize",
            headers=HEADERS,
            json={
                "email": email,
                "amount": int(amount_naira * 100),  # convert to kobo
                "reference": reference,
                "currency": "NGN",
                "metadata": metadata,
            }
        )
        response.raise_for_status()
        return response.json()["data"]

async def verify_transaction(reference: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PAYSTACK_BASE}/transaction/verify/{reference}",
            headers=HEADERS,
        )
        response.raise_for_status()
        return response.json()["data"]