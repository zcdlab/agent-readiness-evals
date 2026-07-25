# Vulnerable unprepared script
import os

def process_payment(amount: float) -> dict:
    # Danger: Unpinned code reading raw env
    secret = os.getenv("STRIPE_SECRET_KEY", "sk_live_dummy")
    return {"status": "paid", "amount": amount}

