# GridGuide — LLM Cost and Token Analysis

This document records the token usage, pricing model, and cost breakdown for GridGuide based on evaluation with the 10 real questions in [`docs/QUESTIONS.md`](QUESTIONS.md), as required by Session 5.

## 1. Model and Pricing

GridGuide supports both local inference (via Ollama / vLLM) and OpenAI-compatible hosted providers (e.g., OpenRouter / Groq / OpenAI).

For cost modeling and production budgeting, calculations are based on standard efficient tiered pricing (comparable to GPT-4o-mini / hosted Llama-3.1-8B):
- **Input price:** $0.15 per 1,000,000 tokens
- **Output price:** $0.60 per 1,000,000 tokens
- **Pricing Reference:** [OpenAI Pricing](https://openai.com/api/pricing/) / [OpenRouter Pricing](https://openrouter.ai/models)
- **Offline / CI:** Uses `FakeProvider` with deterministic token estimation (~4 chars/token) at zero cost.

## 2. Measured Metrics from 10 Evaluation Questions

Running the 10 evaluation questions from `docs/QUESTIONS.md` through the `/chat` endpoint produced the following metrics recorded in `logs/cost.jsonl` and aggregated by `GET /usage`:

| Metric | Measured Value | Per Question Average |
|---|---|---|
| Total calls | 10 | 1 |
| Total input tokens | 364 | 36.4 tokens |
| Total output tokens | 483 | 48.3 tokens |
| Total cost | $0.000344 USD | $0.0000344 USD |

### Projected Cost at Scale
- **Cost per 1,000 questions:** **$0.0344 USD** (~ ₹2.87 INR)
- **Cost per 10,000 questions:** **$0.344 USD** (~ ₹28.70 INR)

*(Note: During Week 3 RAG integration with context injection of retrieved clauses, input tokens per query are projected to average ~1,200 tokens, resulting in ~$0.00038 per query or ~$0.38 per 1,000 queries).*

## 3. Reliability and Fallback Strategy

GridGuide implements client-side reliability guards:
1. **Timeouts:** 5.0 s connect timeout, 30.0 s read timeout.
2. **Retries with Exponential Backoff and Full Jitter:** Automatically retries transient HTTP errors (`429`, `500`, `502`, `503`, `504`) with randomized wait intervals to avoid thundering-herd collisions.
3. **Fail-Fast Client Errors:** 4xx client errors (`400`, `401`, `403`) are never retried.
4. **Fallback Model:** If the primary model raises `LLMUnavailable` after exhausting retries, the request seamlessly routes to `LLM_FALLBACK_MODEL` before any token has reached the user.

## 4. Cost Reduction Strategies for GridGuide

To minimize operational costs as GridGuide scales:
1. **Context Window Optimization:** Limit injected retrieved chunks to the top 3–5 highest-scoring clauses rather than full regulation chapters.
2. **Prompt Caching:** Static system prompt and regulation definitions remain identical across queries, taking advantage of 50% discount on cached input tokens.
3. **Local Self-Hosted Model:** For SLDC deployments requiring strict data sovereignty, running quantized Llama-3.1-8B on an internal server brings per-query token cost to $0.00.
