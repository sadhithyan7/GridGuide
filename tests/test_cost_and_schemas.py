import pytest
from pydantic import ValidationError

from app.cost import cost_usd
from app.schemas import ChatRequest, Message, StructuredAnswer, Usage


def test_cost_usd_calculation():
    usage = Usage(input_tokens=1000, output_tokens=500)
    # price: $1.0 per million in, $2.0 per million out
    cost = cost_usd(usage, price_in_per_m=1.0, price_out_per_m=2.0)
    expected = (1000 * 1.0 + 500 * 2.0) / 1_000_000
    assert abs(cost - expected) < 1e-9


def test_schemas_validation():
    # Valid request
    req = ChatRequest(messages=[Message(role="user", content="hello")], temperature=0.5)
    assert len(req.messages) == 1
    assert req.temperature == 0.5

    # Invalid role fails regex validation
    with pytest.raises(ValidationError):
        Message(role="hacker", content="hello")

    # StructuredAnswer schema
    ans = StructuredAnswer(answer="Grid Code Clause 5.2", confidence=0.95, sources=["IEGC.pdf"])
    assert ans.confidence == 0.95
