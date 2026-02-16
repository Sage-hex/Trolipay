# SPEC_v1_TECH.md — ChatCommerce v1 Technical Engineering Spec (Strict for Codex)

**Purpose:** This is the strict engineering spec Codex must follow to implement ChatCommerce v1 backend cleanly and predictably, without drift.

**Scope:** NGN-only (v1), Paystack platform payments (Pipeline A), 1.5% platform fee per successful transaction, Telegram-first and WhatsApp alongside, local media storage for v1, Gemini integration only after money loop is stable.

---

## 0) Glossary

- **Platform**: You (the SaaS operator) owning the Paystack integration.
- **Business/Tenant**: A merchant using the platform (e.g., “Blessing Cakes”).
- **Customer**: End user ordering via Telegram/WhatsApp.
- **Pipeline A**: Merchant supplies bank details; platform creates Paystack Subaccount.
- **Minor units**: Kobo for NGN (integer).
- **Money loop**: Reserve order → Pay link → Paystack webhook → Order paid → Receipt.

---

## 1) Non-Negotiable Constraints (Codex MUST enforce)

### 1.1 Versioning

- ALL API routes MUST be prefixed with: `/api/v1`
- Webhooks MUST be versioned too:
  - `/api/v1/webhooks/paystack`
  - `/api/v1/channels/telegram/webhook`
  - `/api/v1/channels/whatsapp/webhook`

### 1.2 Money Standard

- DB stores amounts as **integer kobo** only:
  - Field names MUST use suffix `_kobo` for money amounts.
- Admin input is **whole naira integers** only (no decimals in v1).
- Conversion MUST be:
  - `kobo = naira * 100`
- Platform fee MUST be:
  - `platform_fee_kobo = ceil(total_kobo * 0.015)`
  - `business_payout_kobo = total_kobo - platform_fee_kobo`
- Fee calculation MUST use deterministic arithmetic (Decimal OK). No float storage.

### 1.3 Payment Truth Rule

- An order may transition to `paid` ONLY through VERIFIED Paystack webhook handling.
- There MUST NOT be any admin endpoint or code path that directly sets `order.status = "paid"`.

### 1.4 Multi-Tenancy Rule (Admin)

- `business_id` MUST be derived from JWT ONLY for admin endpoints.
- Admin endpoints MUST NOT accept `business_id` as a request input.
- All repository queries MUST filter by the JWT business_id (tenant scoping).
- Channel endpoints may accept store routing info (store_code), but internal writes must still be scoped to the resolved business_id.
- Cross-tenant access MUST return 404 consistently.

### 1.5 Separation of Concerns (Hard rule)

- **Routers**: validate request, authorize, call service, return response.
  - NO DB queries.
  - NO external HTTP calls.
- **Services**: business logic and orchestration.
  - May call repositories.
  - May call integration clients (Paystack/Telegram/WhatsApp).
- **Repositories**: DB access only.
  - NO HTTP.
  - NO business rules (except trivial filtering).
- **Integrations/Clients**: external API calls only (Paystack/Telegram/WhatsApp/Gemini).
  - NO DB.

### 1.6 Storage v1 Rule

- Store product images and receipts locally:
  - `media/products/`
  - `media/receipts/`
- Serve through FastAPI static mount:
  - `app.mount("/media", StaticFiles(directory="media"), name="media")`
- Filenames MUST be unguessable (uuid or secure random).

### 1.7 Gemini Rule (Strict)

- Gemini integration must be implemented ONLY AFTER money loop (Block 9) is stable.
- Gemini is assist-only:
  - Allowed: intent classification, order extraction suggestions, reply drafting.
  - Forbidden: changing payment/order status, setting totals, inventing prices/delivery fees.
- Any AI-assisted ordering MUST require explicit customer confirmation (“CONFIRM”) before creating/reserving an order.

---

## 2) Build Order (Codex MUST follow)

Codex must implement in this exact sequence. Do NOT skip ahead.

1. Bootstrap: config, db engine, app init, `/health`, static `/media` mount
2. Models + Alembic migrations
3. Money helpers + unit tests
4. Auth routes (register/login/me) + JWT guard dependency
5. Products CRUD + image upload
6. Delivery zones CRUD
7. Payout setup (Paystack subaccount) + status
8. Orders (reserve/list/detail/mark-delivered)
9. Payments init + Paystack webhook (idempotent)
10. Receipt PDF generation + receipts endpoint
11. Telegram webhook adapter (minimal commands)
12. WhatsApp webhook adapter (minimal commands + START <STORE_CODE>)
13. Gemini AI assist (audit + client + ai endpoints, optional bot wiring OFF by default)

---

## 3) Technology Stack (v1)

- Python 3.12
- FastAPI + Uvicorn
- PostgreSQL
- SQLModel (ORM)
- Alembic (migrations)
- passlib[bcrypt] (password hashing)
- python-jose (JWT)
- httpx (external HTTP)
- reportlab (PDF receipts)
- pytest (tests)

---

## 4) Repository Layout (Strict)

Codex must create/maintain these paths and not deviate without strong reason.

app/
main.py
api/v1/
auth.py
business.py
products.py
delivery.py
payout.py
orders.py
payments.py
receipts.py
webhooks.py
channels_telegram.py
channels_whatsapp.py
ai.py # ONLY after Block 9 stable
core/
config.py
db.py
security.py
errors.py
logging.py
models/
init.py
business.py
user.py
payout_profile.py
product.py
delivery_zone.py
customer.py
conversation.py
order.py
payment.py
receipt.py
message_log.py
ai_audit.py # ONLY after Block 9 stable
repositories/
business_repo.py
user_repo.py
payout_repo.py
product_repo.py
delivery_repo.py
customer_repo.py
conversation_repo.py
order_repo.py
payment_repo.py
receipt_repo.py
message_log_repo.py
ai_audit_repo.py # ONLY after Block 9 stable
services/
money.py
pricing_service.py
order_service.py
paystack_service.py
receipt_service.py
telegram_service.py
whatsapp_service.py
ai/
gemini_client.py
prompts.py
schemas.py
safety.py
ai_service.py
tests/
test_money.py
test_pricing.py
test_order_flow.py
migrations/

---

## 5) Database Schema (v1) — SQLModel Tables + Constraints

All tables MUST include only fields listed here for v1. Additional fields require justification.

### 5.1 business

- id (PK)
- name (text, indexed)
- store_code (text, unique, indexed) e.g. "BLESSING"
- currency (text, default "NGN")
- created_at (timestamp)

### 5.2 user

- id (PK)
- business_id (FK -> business.id, indexed)
- email (text, unique, indexed)
- password_hash (text)
- role (text, default "owner")
- created_at

### 5.3 payout_profile

- business_id (FK -> business.id, UNIQUE)
- bank_name
- account_number
- account_name
- paystack_subaccount_code (nullable initially)
- status (text: pending/active/failed, default pending)
- created_at

### 5.4 product

- id (PK)
- business_id (FK, indexed)
- name (text, indexed)
- description (nullable)
- base_price_kobo (int)
- image_url (nullable) e.g. "/media/products/<file>.jpg"
- is_active (bool, default true)
- created_at

### 5.5 delivery_zone

- id (PK)
- business_id (FK, indexed)
- name (text)
- fee_kobo (int)
- is_active (bool, default true)

### 5.6 customer

- id (PK)
- business_id (FK, indexed)
- channel_type (text, indexed) = "telegram" | "whatsapp"
- channel_user_id (text, indexed) = telegram user id or whatsapp phone string
- display_name (nullable)
- created_at
  **Constraint recommendation:** unique(business_id, channel_type, channel_user_id)

### 5.7 conversation

- id (PK)
- business_id (FK, indexed)
- customer_id (FK, indexed)
- channel_type (text, indexed)
- channel_thread_id (text, indexed) = telegram chat_id / whatsapp thread
- current_state (text, default "idle")
- last_message_at (timestamp)

### 5.8 order

- id (PK)
- business_id (FK, indexed)
- customer_id (FK, indexed)
- channel_type (text, indexed)
- status (text, indexed) default "reserved"
- subtotal_kobo (int)
- delivery_fee_kobo (int)
- total_kobo (int)
- platform_fee_kobo (int)
- business_payout_kobo (int)
- delivery_zone_id (nullable FK -> delivery_zone.id)
- delivery_address (nullable text)
- expires_at (nullable timestamp)
- created_at (timestamp)

### 5.9 order_item

- id (PK)
- order_id (FK -> order.id, indexed)
- product_id (nullable FK -> product.id)
- name_snapshot (text)
- unit_price_kobo (int)
- quantity (int)
- line_total_kobo (int)

### 5.10 payment

- id (PK)
- order_id (FK -> order.id, indexed)
- provider (text, default "paystack")
- status (text, indexed, default "initiated") = initiated/success/failed
- amount_kobo (int)
- currency (text, default "NGN")
- paystack_reference (nullable text, UNIQUE, indexed)
- authorization_url (nullable text)
- raw_event_json (nullable text)
- created_at
- confirmed_at (nullable)

### 5.11 receipt

- id (PK)
- order_id (FK -> order.id, indexed)
- receipt_number (text, indexed)
- pdf_url (text) e.g. "/media/receipts/<file>.pdf"
- created_at

### 5.12 message_log

- id (PK)
- business_id (FK -> business.id, indexed)
- customer_id (nullable FK -> customer.id)
- channel_type (text)
- direction (text) = in/out
- text (nullable)
- status (text, default "sent")
- created_at

### 5.13 ai_audit (ONLY after Block 9 stable)

- id (PK)
- business_id (FK, indexed)
- customer_id (nullable FK, indexed)
- feature_name (text)
- model (text)
- request_text (text)
- response_text (text)
- response_json (nullable text)
- status (text) = success/failure
- error (nullable text)
- created_at

---

## 6) API Contract (Strict)

All endpoints return JSON. All admin endpoints require JWT unless stated otherwise.

### 6.1 Auth

- POST `/api/v1/auth/register`
  - Creates business + owner user.
  - Enforces unique store_code and unique email.
- POST `/api/v1/auth/login`
  - Returns JWT with user_id and business_id.
- GET `/api/v1/me`
  - Returns current user and business summary.

### 6.2 Business

- GET `/api/v1/business` (JWT)
- PATCH `/api/v1/business` (JWT) — v1 minimal fields only (name)

### 6.3 Uploads

- POST `/api/v1/uploads/product-image` (JWT)
  - multipart form file -> saves to `media/products/`
  - returns `{ "image_url": "/media/products/<filename>" }`

### 6.4 Products (JWT, tenant scoped)

- POST `/api/v1/products`
  - accepts `base_price_naira` (int) input
  - stores `base_price_kobo = base_price_naira * 100`
- GET `/api/v1/products`
- PATCH `/api/v1/products/{id}`
- DELETE `/api/v1/products/{id}` -> soft delete (is_active=false)

### 6.5 Delivery zones (JWT, tenant scoped)

- POST `/api/v1/delivery-zones` accepts `fee_naira` (int), stores `fee_kobo`
- GET `/api/v1/delivery-zones`
- PATCH `/api/v1/delivery-zones/{id}`
- DELETE `/api/v1/delivery-zones/{id}` -> soft delete (is_active=false)

### 6.6 Payout setup (JWT, tenant scoped)

- POST `/api/v1/payout/setup`
  - input: bank_name, account_number, account_name
  - service creates Paystack subaccount (Pipeline A)
  - persists payout_profile status=active + subaccount_code
- GET `/api/v1/payout/status`

### 6.7 Orders (JWT for dashboard; reserve used by channels)

- POST `/api/v1/orders/reserve`
  - used by Telegram/WhatsApp adapters
  - may accept `store_code` to resolve business in channel flow
  - creates order in `reserved` state with `expires_at = now + 60min`
- GET `/api/v1/orders` (JWT)
- GET `/api/v1/orders/{id}` (JWT)
- POST `/api/v1/orders/{id}/mark-delivered` (JWT)
  - allowed only if order.status == "paid"

### 6.8 Payments + webhook (core money loop)

- POST `/api/v1/orders/{id}/pay` (JWT or internal use)
  - Preconditions:
    - order.status == "reserved"
    - payout_profile.status == "active"
  - initializes Paystack payment for `order.total_kobo`
  - configures split/subaccount:
    - business receives payout_kobo
    - platform retains platform_fee_kobo
  - stores Payment(reference, authorization_url) and sets order.status="payment_pending"
- POST `/api/v1/webhooks/paystack` (no JWT)
  - verifies signature
  - idempotent processing:
    - if payment already success, return ok
  - on success:
    - payment.status = success
    - order.status = paid
    - generate receipt pdf and store receipt row

### 6.9 Receipts

- GET `/api/v1/receipts/{order_id}` (JWT dashboard)
  - returns receipt_number + pdf_url
  - receipt must exist for paid orders; generate if missing (optional)

### 6.10 Channels (no JWT; provider validation required)

- POST `/api/v1/channels/telegram/webhook`
- POST `/api/v1/channels/whatsapp/webhook`

---

## 7) Service Layer Contracts (Strict)

### 7.1 MoneyService (app/services/money.py)

- `naira_to_kobo(naira_int:int)->int`
- `calc_platform_fee_kobo(total_kobo:int, fee_rate=Decimal("0.015"))->int` using ceil
- tests MUST cover rounding behavior

### 7.2 PricingService (app/services/pricing_service.py)

Input:

- business_id
- items: [{product_id, quantity}]
- delivery_zone_id optional
  Output (all kobo):
- subtotal_kobo
- delivery_fee_kobo
- total_kobo
- platform_fee_kobo
- business_payout_kobo

Rules:

- product prices loaded from DB (tenant scoped)
- delivery fee loaded from DB (tenant scoped)
- totals computed using MoneyService

### 7.3 OrderService (app/services/order_service.py)

- `reserve_order(...)`:
  - upsert customer
  - create order + order_items snapshots
  - set status reserved, expires_at
- `mark_delivered(order_id)`:
  - allowed only if paid

### 7.4 PaystackService (app/services/paystack_service.py)

- `create_subaccount(business, bank details)->subaccount_code`
- `init_transaction(order, customer_email, subaccount_code, fee config)-> {reference, authorization_url}`
- `verify_webhook(signature_header, raw_body)->bool`
- `parse_webhook_event(raw_json)->(reference, status, amount, metadata)`

### 7.5 ReceiptService (app/services/receipt_service.py)

- `generate_receipt(order_id)->Receipt`
  - creates PDF file under media/receipts (unguessable filename)
  - stores receipt row with receipt_number and pdf_url

### 7.6 TelegramService / WhatsAppService

- Must implement minimal command parsing and call core services:
  - list products
  - reserve order
  - pay order (get authorization_url)
- Must log inbound/outbound message_log
- No direct DB writes inside webhook handler; any DB operations via services/repos

---

## 8) Webhook Security (Strict)

### 8.1 Paystack

- Verify HMAC signature per Paystack’s documented scheme for webhooks (implementation in PaystackService).
- Reject invalid signature (return 400/401).
- Store raw_event_json in Payment for audit (optional but recommended).
- Idempotency:
  - Unique constraint on paystack_reference
  - If already processed (payment.success), return `{ok:true}` without changes

---

## 9) Channel MVP Behaviors (Strict)

### 9.1 Telegram command set (v1)

- `/start <STORE_CODE>` -> set business context
- `products` -> list products with ids and prices
- `buy <product_id> <qty>` -> reserve order (no delivery)
- `delivery <zone_id> <address>` -> attach delivery to latest reserved order
- `pay` -> create payment link for latest reserved order and send link

### 9.2 WhatsApp MVP routing + commands (v1)

- Must start with: `START <STORE_CODE>`
- Then same commands as Telegram.

---

## 10) Testing Requirements (Minimum viable)

Tests MUST exist and pass for:

- Money math:
  - naira_to_kobo
  - fee calc with ceil
- Order reserve flow:
  - correct totals and fee
- Webhook idempotency:
  - applying same webhook twice doesn’t double-process
- Auth basics:
  - register/login/me

Mock Paystack HTTP calls in tests.

---

## 11) Error Handling (Strict)

- Use typed exceptions in `core/errors.py` mapped to HTTP errors.
- Routers MUST not leak stack traces.
- Provide consistent error response shape:
  - `{ "error": { "code": "...", "message": "...", "details": ... } }` (recommended)

---

## 12) Gemini AI Integration (Phase after money loop stable)

Gemini implementation MUST be isolated behind:

- `AI_ENABLED` flag
- per-business `ai_enabled` (default false)

### 12.1 AI endpoints (JWT protected)

- POST `/api/v1/ai/classify-intent`
- POST `/api/v1/ai/extract-order`
- POST `/api/v1/ai/draft-reply`

### 12.2 AI audit logging (mandatory)

Every AI call must create an AIAudit row (success or failure).

### 12.3 Bot wiring (optional, OFF by default)

If enabled:

- AI can suggest extracted orders but must ask customer to CONFIRM.
- Only on explicit CONFIRM do we call `reserve_order`.

---

## 13) Definition of Done (v1)

v1 is complete when:

- Business can register/login and configure:
  - payout subaccount
  - products
  - delivery zones
- Telegram customer can:
  - reserve order, pay, webhook confirms, receipt generated
- WhatsApp customer can:
  - START store, reserve, pay, webhook confirms
- Platform fee 1.5% computed and stored on every paid order
- Webhook idempotency proven by tests
- No manual paid-state exists
- Gemini code either absent or isolated and off by default

---

## 14) Codex Implementation Rule

When implementing, Codex MUST:

- Implement exactly one “block” at a time.
- Avoid creating unused scaffolding.
- Provide file diffs and run commands for verification.
- Not introduce Stripe, international currencies, or new features not in this spec.
