def handle_event(event: dict) -> dict:
    return {"status": "ok", "event_id": event.get("id")}

