from src.handler import handle_event


def test_handle_event():
    res = handle_event({"id": "ev-1"})
    assert res["status"] == "ok"
    assert res["event_id"] == "ev-1"

