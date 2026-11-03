from pathlib import Path


def test_chat_streams_sse_and_logs_cost(client):
    payload = {
        "messages": [{"role": "user", "content": "What is the frequency band?"}],
        "temperature": 0.2,
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    body = response.text
    assert "data: " in body
    assert "event: done" in body
    assert "cost_usd" in body

    # Cost log should be recorded
    cost_file = Path(client.settings.cost_log_path)
    assert cost_file.exists()
    lines = cost_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert "input_tokens" in lines[0]


def test_chat_rejects_bad_input(client):
    payload = {
        "messages": [{"role": "attacker", "content": "hello"}],
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 422
