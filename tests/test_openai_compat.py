import asyncio

import httpx
import pytest

from app.llm.base import LLMError, LLMUnavailable, StreamResult
from app.llm.openai_compat import OpenAICompatProvider
from app.schemas import Message

MSGS = [Message(role="user", content="hello")]


def collect(p):
    result = StreamResult()

    async def run():
        return "".join([piece async for piece in p.stream_chat(MSGS, 0.2, result)])

    return asyncio.run(run()), result


def test_openai_compat_streams_chunks():
    def handler(request):
        lines = [
            'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            'data: {"choices": [{"delta": {"content": " world"}}]}',
            'data: {"usage": {"prompt_tokens": 5, "completion_tokens": 2}}',
            "data: [DONE]",
        ]
        content = "\n\n".join(lines) + "\n\n"
        return httpx.Response(200, text=content, headers={"Content-Type": "text/event-stream"})

    provider = OpenAICompatProvider(
        base_url="http://test/v1",
        api_key="key",
        model="test-model",
        transport=httpx.MockTransport(handler),
    )
    text, result = collect(provider)
    assert text == "Hello world"
    assert result.usage.input_tokens == 5
    assert result.usage.output_tokens == 2


def test_openai_compat_retries_on_503_and_succeeds():
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return httpx.Response(503, text="Service Unavailable")
        lines = [
            'data: {"choices": [{"delta": {"content": "recovered"}}]}',
            "data: [DONE]",
        ]
        return httpx.Response(200, text="\n\n".join(lines) + "\n\n")

    provider = OpenAICompatProvider(
        base_url="http://test/v1",
        api_key="key",
        model="test-model",
        max_retries=3,
        backoff_base_seconds=0.0,
        transport=httpx.MockTransport(handler),
    )
    text, _ = collect(provider)
    assert text == "recovered"
    assert attempts == 3


def test_openai_compat_does_not_retry_401():
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(401, json={"error": "unauthorized"})

    provider = OpenAICompatProvider(
        base_url="http://test/v1",
        api_key="bad-key",
        model="test-model",
        max_retries=3,
        backoff_base_seconds=0.0,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(LLMError) as exc_info:
        collect(provider)
    assert "401" in str(exc_info.value)
    assert attempts == 1  # No retries on 401


def test_openai_compat_timeout_raises_llm_unavailable():
    def handler(request):
        raise httpx.ReadTimeout("read timed out", request=request)

    provider = OpenAICompatProvider(
        base_url="http://test/v1",
        api_key="key",
        model="test-model",
        max_retries=2,
        backoff_base_seconds=0.0,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(LLMUnavailable) as exc_info:
        collect(provider)
    assert "LLM call failed after 3 attempts" in str(exc_info.value)


def test_openai_compat_mid_stream_failure_raises_llm_error():
    async def broken_stream(request):
        async def byte_generator():
            yield b'data: {"choices": [{"delta": {"content": "start"}}]}\n\n'
            # Simulating transport disconnect mid-stream
            raise httpx.TransportError("connection dropped mid-stream")

        return httpx.Response(200, content=byte_generator())

    provider = OpenAICompatProvider(
        base_url="http://test/v1",
        api_key="key",
        model="test-model",
        max_retries=2,
        backoff_base_seconds=0.0,
        transport=httpx.MockTransport(broken_stream),
    )
    with pytest.raises(LLMError) as exc_info:
        collect(provider)
    assert "stream broke mid-answer" in str(exc_info.value)
