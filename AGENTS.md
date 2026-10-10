# Codex project instructions

## Project purpose
This is a 30-day, hands-on AI Automation Engineer learning project. Days 1–6 cover a local Ollama Llama 3.2 lead analyzer, Python tool calling, FastAPI endpoints, WooCommerce REST integration, rule-based order workflows and signed WooCommerce webhooks. Continue with **Day 7: reliability, idempotency and retries**.

## Teaching style
- The developer is highly experienced with PHP, WordPress and WooCommerce but is learning Python.
- Explain unfamiliar Python concepts patiently and in practical terms, with PHP analogies where useful.
- Make small, reviewable changes; explain the purpose of each file and important code blocks.
- Show commands for Windows **Git Bash** from the repository root, using `./.venv/Scripts/python.exe` where appropriate.

## Existing structure
- `day01/lead_analyzer.py`: Ollama lead scoring with Pydantic.
- `day02/`: mock WooCommerce order tools and Ollama function calling.
- `day03/main.py`: FastAPI lead and order endpoints.
- `day04/`: WooCommerce REST client and real-order assistant.
- `day05/business_rules.py`: deterministic order decisions.
- `day05/message_generator.py`: Ollama-generated **drafts**.
- `day05/workflow.py`: fetch order, apply rules, generate draft, log.
- `day06/main.py`: signed WooCommerce webhook receiver with background processing.
- `day06/webhook_security.py`: HMAC verification.
- `README.md`: current setup, architecture and progress.

**Important:** `day05/workflow.py` is presently listed in `.gitignore` and might be available only in the local checkout. Do not assume it is in this GitHub repository. Ask the developer to check and commit the intended source file after reviewing for secrets. Do not invent its implementation.

## Local development
- Windows, VS Code, Git Bash, local XAMPP WordPress/WooCommerce at `https://localhost/wordpress`.
- Ollama typically at `http://localhost:11434`, model `llama3.2`.
- FastAPI Day 6: `./.venv/Scripts/python.exe -m uvicorn day06.main:app --reload --port 8001`.
- ngrok exposes the local webhook during tests. Its HTTPS hostname is ephemeral.
- Tests: `./.venv/Scripts/python.exe -m pytest -v`, or limit to the relevant day.

## Security and behavior
- Never commit, print or request real contents of `.env`, WooCommerce API secrets, webhook secret, customer PII, or generated logs.
- Ensure `.env`, `.venv/`, caches and runtime logs are ignored.
- Keep webhook HMAC validation for real WooCommerce order events. An unsigned WooCommerce activation ping has a narrowly scoped exception; never generalize it to unsigned order events.
- Do not automatically send customer messages or mutate WooCommerce orders without explicit approval. Generated messages are drafts and must not promise shipping updates or actions not supported by order data.
- Treat public ngrok exposure and local self-signed TLS workarounds as development-only.
- Prefer deterministic business rules to AI for financial/order decisions; use Decimal for currency.
- Add tests for new logic. Mock WooCommerce, Ollama and network calls in unit tests.

## Verified milestone and open checks
On 2026-10-10, a real WooCommerce update for order #37 triggered the Day 6 workflow, fetched order details successfully, decided `priority_fulfillment_review`, received Ollama HTTP 200 and logged workflow completion.
Still confirm the Day 4 real-order assistant end-to-end response, Day 5 unit tests, and Day 6 webhook tests before marking those checks complete.

## Suggested Day 7 scope
1. Inspect existing webhook and workflow code before editing.
2. Add safe idempotency/deduplication for repeated WooCommerce webhook deliveries using stable event identifiers and a documented persistence strategy.
3. Implement bounded retries with exponential backoff only for transient API/network errors.
4. Keep error logging free of secrets and customer data, and clearly represent success/failure.
5. Add repeat-delivery, invalid-signature, transient-failure and non-retryable-error tests.
6. Preserve prior day behavior and explain how to run and verify changes locally.
