# AI Automation Engineer — 30-Day Learning Project

A hands-on journey from Python and local LLMs to real-world WooCommerce automation. This repository contains the projects built during **Days 1–6**, using **Python, Ollama (Llama 3.2), Pydantic, FastAPI, pytest, and WooCommerce REST APIs/webhooks**.

> **Current milestone:** A WooCommerce order update can trigger a webhook through ngrok, reach FastAPI, retrieve the order, apply Python business rules, generate an Ollama message draft, and log successful completion. This has been observed end-to-end for **order #37**.
>
> **Safety:** The automation generates message **drafts**; it does not send messages or change order status.

## Learning progress

| Day | Project | Main outcome | Status |
| --- | --- | --- | --- |
| 1 | AI Lead Analyzer | Parse leads with Ollama, validate with Pydantic, and classify leads | Implemented |
| 2 | AI Tool Calling | Let Ollama request approved order lookup functions | Implemented; 7 tests previously passed |
| 3 | AI REST API | Expose lead analysis and order assistance via FastAPI | Implemented; 15 Day 3 tests previously passed |
| 4 | Real WooCommerce Integration | Fetch real orders through the WooCommerce REST API | Real API verified; real-order assistant end-to-end answer not yet confirmed |
| 5 | AI Workflow Automation | Apply order rules, generate drafts, and log results | End-to-end workflow confirmed through Day 6; unit tests not yet confirmed |
| 6 | Event-Driven Automation | Receive signed order webhooks and run the Day 5 workflow | Live order #37 processed successfully; full test suite not yet confirmed |

## Architecture

```text
WooCommerce order created/updated
            |
            v
  WooCommerce webhook (HTTPS)
            |
            v
      ngrok (development)
            |
            v
 FastAPI POST /webhooks/woocommerce
            |
     Verify HMAC signature
            |
            v
  BackgroundTasks (development)
            |
            v
   Day 5 order workflow
            |
            +--> WooCommerce REST API: fetch order
            +--> Python: validate and apply business rules
            +--> Ollama: generate message draft
            +--> Logging: record result
```

**Note:** WooCommerce's activation ping uses a different payload from a normal signed order event. The Day 6 receiver handles that ping separately and requires signature verification for normal order events. The unsigned ping exception is for local development only.

## Repository structure

```text
ai-automation/
├── .env                         # Local secrets; do not commit
├── .gitignore
├── .venv/                       # Local Python environment; do not commit
├── day01/
│   └── lead_analyzer.py
├── day02/
│   ├── tools.py
│   └── order_assistant.py
├── day03/
│   └── main.py
├── day04/
│   ├── __init__.py
│   ├── woocommerce_client.py
│   ├── check_connection.py
│   └── real_order_assistant.py
├── day05/
│   ├── __init__.py
│   ├── business_rules.py
│   ├── message_generator.py
│   ├── workflow.py
│   ├── main.py
│   ├── test_business_rules.py
│   └── logs/                    # Generated logs; do not commit
├── day06/
│   ├── __init__.py
│   ├── webhook_security.py
│   ├── main.py
│   └── test_webhook.py
└── README.md
```

Some earlier days may also contain additional test or debugging scripts. Remove temporary authentication/debugging files after use, especially any temporary WordPress MU plugins and `test-fastapi.php`.

## Prerequisites

- Windows with **Git Bash** and **VS Code** (commands below use Git Bash)
- Python 3.10+ (3.11+ recommended)
- [Ollama](https://ollama.com/) with the `llama3.2` model
- XAMPP with a local WordPress + WooCommerce installation
- WooCommerce REST API consumer key and secret
- [ngrok](https://ngrok.com/download) for webhook testing over public HTTPS

## Quick start

From your project root:

```bash
# Create the virtual environment if it does not exist
python -m venv .venv

# Activate it in Git Bash
source .venv/Scripts/activate

# Install the packages used across Days 1–6
python -m pip install --upgrade pip
python -m pip install ollama pydantic fastapi "uvicorn[standard]" httpx python-dotenv pytest

# Download the local model (once)
ollama pull llama3.2
```

Keep Ollama running. Depending on your installation, the Ollama application may already run its local server; otherwise start it using `ollama serve`.

### Environment variables

Create `.env` at the project root:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

WOOCOMMERCE_URL=https://localhost/wordpress
WOOCOMMERCE_CONSUMER_KEY=your_consumer_key
WOOCOMMERCE_CONSUMER_SECRET=your_consumer_secret

WOOCOMMERCE_WEBHOOK_SECRET=your_long_random_webhook_secret
```

Generate a webhook secret:

```bash
./.venv/Scripts/python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set the **same webhook secret** in WooCommerce's webhook settings. It is **not** the same as the WooCommerce REST API consumer secret.

> Local XAMPP may use a self-signed HTTPS certificate. Trust a development certificate where possible; never disable TLS verification in production. Never publish API credentials, webhook secrets, customer data, or `.env`.

Recommended `.gitignore` entries:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
*.pyc
day05/logs/
```

## Day-by-day projects

### Day 1 — AI Lead Analyzer

**File:** `day01/lead_analyzer.py`

- Analyze unstructured lead information using local Ollama.
- Convert model output to structured data.
- Validate with Pydantic.
- Apply Python-based lead scoring and classification (Hot / Warm / Cold).

```bash
./.venv/Scripts/python.exe -m day01.lead_analyzer
```

### Day 2 — AI Tool Calling

**Files:** `day02/tools.py`, `day02/order_assistant.py`

- Define mock order functions: `get_order_status(order_id)` and `get_order_total(order_id)`.
- Supply approved tool definitions to Ollama.
- Inspect tool calls, validate arguments, execute allowlisted functions, and return results to the model.

```bash
./.venv/Scripts/python.exe -m day02.order_assistant
```

### Day 3 — FastAPI REST API

**File:** `day03/main.py`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Welcome/status |
| GET | `/health` | Health check |
| POST | `/analyze-lead` | Day 1 lead analysis |
| POST | `/ask-order` | Day 2 mock order assistant |

```bash
./.venv/Scripts/python.exe -m uvicorn day03.main:app --reload --port 8000
```

Swagger UI: <http://127.0.0.1:8000/docs>

### Day 4 — Real WooCommerce REST API

**Files:** `day04/woocommerce_client.py`, `day04/check_connection.py`, `day04/real_order_assistant.py`

- Connect to local WooCommerce with REST API credentials.
- Fetch and sanitize order details: ID, status, total, and currency.
- Integrate the real-order lookup with Ollama tool calling.

```bash
./.venv/Scripts/python.exe -m day04.check_connection
./.venv/Scripts/python.exe -m day04.real_order_assistant
```

**Verified:** WooCommerce REST API returned real order **#42** successfully. A separate successful end-to-end response from the Day 4 interactive real-order assistant is still to be verified.

### Day 5 — AI Order Workflow

**Files:** `day05/business_rules.py`, `day05/message_generator.py`, `day05/workflow.py`, `day05/main.py`

The workflow:

1. Fetches an order through the Day 4 WooCommerce client.
2. Validates order fields and monetary total using `Decimal`.
3. Selects an action with deterministic Python rules.
4. Asks Ollama to generate a **draft** customer message.
5. Logs completion or failure to `day05/logs/workflow.log`.

```bash
./.venv/Scripts/python.exe -m day05.main
```

Example rule actions include `await_payment`, `manual_review`, `prepare_fulfillment`, and `priority_fulfillment_review`. The high-value threshold in this learning project is illustrative and should be made store/currency-specific before production use.

### Day 6 — WooCommerce Webhooks

**Files:** `day06/webhook_security.py`, `day06/main.py`, `day06/test_webhook.py`

- Receive WooCommerce webhook POST requests.
- Verify normal order-event signatures using HMAC-SHA256.
- Acknowledge WooCommerce's separate activation ping.
- Schedule the Day 5 workflow after validating an order event.

Start FastAPI:

```bash
./.venv/Scripts/python.exe -m uvicorn day06.main:app --reload --port 8001
```

Check <http://127.0.0.1:8001/health> and <http://127.0.0.1:8001/docs>.

In a second terminal:

```bash
ngrok http 8001
```

Configure the WooCommerce webhook at **WooCommerce → Settings → Advanced → Webhooks**:

| Setting | Value |
| --- | --- |
| Status | Active |
| Topic | Order updated |
| Delivery URL | `https://YOUR-NGROK-DOMAIN/webhooks/woocommerce` |
| Secret | Same value as `WOOCOMMERCE_WEBHOOK_SECRET` |

The ngrok URL is session-specific unless your ngrok account provides a stable domain. Update WooCommerce if it changes.

**Verified live run:** Order **#37** triggered the workflow, WooCommerce returned HTTP 200 for its order lookup, the rules selected `priority_fulfillment_review`, Ollama returned HTTP 200, and the workflow logged successful completion.

## Testing

Run individual suites:

```bash
./.venv/Scripts/python.exe -m pytest day05/test_business_rules.py -v
./.venv/Scripts/python.exe -m pytest day06/test_webhook.py -v
```

Run all discovered tests:

```bash
./.venv/Scripts/python.exe -m pytest -v
```

**Previously observed:** Seven Day 2 tests and fifteen Day 3 tests passed. Day 5's five business-rule tests and Day 6's six webhook tests were provided but their final passing results have **not** been confirmed in this conversation.

## Days 1–6 checklist

### Day 1 — AI Lead Analyzer
- [x] Set up Python, VS Code, and virtual environment
- [x] Install and run Ollama with Llama 3.2
- [x] Create lead analyzer
- [x] Extract structured JSON from unstructured lead data
- [x] Validate with Pydantic
- [x] Implement lead classification

### Day 2 — Tool Calling
- [x] Implement mock order status and total tools
- [x] Pass tools to Ollama
- [x] Parse `tool_calls` and arguments
- [x] Restrict execution to approved tools
- [x] Return tool results to Ollama
- [x] Pass seven tests

### Day 3 — FastAPI
- [x] Create FastAPI routes and Pydantic request models
- [x] Build `/analyze-lead` and `/ask-order`
- [x] Run Uvicorn and use Swagger
- [x] Pass fifteen Day 3 tests

### Day 4 — Real WooCommerce
- [x] Configure local WooCommerce and REST API credentials
- [x] Implement WooCommerce Python client
- [x] Successfully fetch real order #42
- [x] Implement real-order Ollama assistant
- [ ] Confirm an end-to-end Ollama answer for a real order

### Day 5 — Workflow Automation
- [x] Create business rules, message generator, and orchestrator
- [x] Fetch and validate real order data
- [x] Generate a message draft with Ollama
- [x] Record workflow logs
- [ ] Confirm five business-rule tests pass

### Day 6 — Event-Driven Automation
- [x] Build FastAPI webhook receiver
- [x] Implement signature verification
- [x] Handle WooCommerce activation ping
- [x] Connect ngrok and save the WooCommerce webhook
- [x] Trigger real order #37 automatically
- [x] Confirm WooCommerce API, business rules, and Ollama completed
- [ ] Confirm six webhook tests pass

## Troubleshooting

**Browser says `405 Method Not Allowed` at `/webhooks/woocommerce`**  
Expected when opening a POST-only endpoint with a browser GET request. Use `/health` for a browser connectivity check.

**WooCommerce says `A valid URL was not provided`**  
WordPress safe HTTP validation may reject local loopback addresses and nonstandard ports. Use an HTTPS development tunnel rather than disabling security checks globally.

**Webhook returns `401 Unauthorized`**  
Check whether it is an activation ping or a normal order event. The observed activation ping used `application/x-www-form-urlencoded` with `webhook_id=...`; normal order events require a valid `X-WC-Webhook-Signature` matching the shared secret. Inspect request metadata in the ngrok inspector without exposing sensitive data.

**Workflow starts but does not finish**  
Check that Ollama is running, the selected model is available, and `day05/logs/workflow.log` contains no error. Model generation may take several seconds.

**Duplicate “Workflow completed” log entries**  
Both Day 5 and Day 6 can log the same completion; this is cosmetic and can be cleaned up later.

## Production readiness and next steps

This is a **learning project**, not yet a production-ready integration. Before production deployment:

- Remove temporary local WordPress security workarounds and debugging files.
- Require trusted HTTPS and keep secrets out of source control.
- Review the unsigned activation-ping exception; never bypass signatures for order events.
- Add webhook deduplication/idempotency and persistent job processing.
- Add retries, timeouts, monitoring, and failure recovery.
- Authenticate and authorize any public order lookup endpoints; never expose arbitrary customer orders.
- Keep AI-generated customer messages as drafts until reviewed and explicitly approved for sending.
- Avoid storing unnecessary customer personal data in logs.

**Day 7 preview:** Reliability, retries, and idempotency for webhook-driven workflows.

---

Built as part of a practical **30-day AI Automation Engineer learning roadmap**.
