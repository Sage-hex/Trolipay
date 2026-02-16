# CODEX_CONTROL_SHEET.md — ChatCommerce v1 (Brutal Gate Checklist)

**Rule:** You do NOT start the next Codex prompt until the current gate is ✅ PASS.  
If anything is ❌ FAIL, you fix it immediately (same step), then re-run checks.

---

## Global invariants (must always be true)
- [ ] All routes are under `/api/v1`
- [ ] Money is stored ONLY as integer kobo; money fields end with `_kobo`
- [ ] Admin inputs are whole naira integers only (no decimals)
- [ ] Currency is fixed to `"NGN"` and not accepted from clients
- [ ] Routers do **no DB calls** and **no HTTP calls**
- [ ] Services contain business logic (call repos + clients)
- [ ] Repos do DB only (tenant scoped)
- [ ] Cross-tenant access returns **404** consistently
- [ ] No manual path sets `order.status="paid"` (webhook-only truth)

---

# STEP GATES (run in order)

## Gate 1 — Bootstrap skeleton
**Expected outputs**
- [ ] `GET /api/v1/health` returns `{"ok": true}`
- [ ] `/media` static mount works and server doesn’t crash even if folders empty
- [ ] Config loads env vars without hardcoding secrets
- [ ] DB session dependency exists (even if DB not used yet)

**Commands**
- [ ] `uvicorn app.main:app --reload` runs cleanly
- [ ] `curl http://127.0.0.1:8000/api/v1/health` returns ok

✅ PASS / ❌ FAIL: _______

---

## Gate 2 — Models + Alembic migrations
**Expected outputs**
- [ ] All v1 tables exist as SQLModel models
- [ ] Constraints exist:
  - [ ] business.store_code UNIQUE
  - [ ] user.email UNIQUE
  - [ ] payout_profile.business_id UNIQUE
  - [ ] customer UNIQUE(business_id, channel_type, channel_user_id)
  - [ ] payment.paystack_reference UNIQUE (nullable ok)
- [ ] All money fields are `int` and end with `_kobo`
- [ ] currency defaults `"NGN"` where required

**Commands**
- [ ] `alembic revision --autogenerate -m "init"` works
- [ ] `alembic upgrade head` works on a fresh DB

✅ PASS / ❌ FAIL: _______

---

## Gate 3 — Money helpers + tests
**Expected outputs**
- [ ] `naira_to_kobo(18000) == 1800000`
- [ ] `calc_platform_fee_kobo(1800000) == 27000`
- [ ] Ceil rounding tested (fractional fee rounds UP)

**Commands**
- [ ] `pytest -q` passes

✅ PASS / ❌ FAIL: _______

---

## Gate 4 — Auth + global error shape
**Expected outputs**
- [ ] Register creates Business + owner User atomically
- [ ] Login returns JWT containing `user_id` and `business_id`
- [ ] `/api/v1/me` returns user + business summary
- [ ] Global error handler returns:
  - [ ] `{ "error": { "code": "...", "message": "...", "details": null } }`

**Commands**
- [ ] Register → Login → Me tested manually or via pytest

✅ PASS / ❌ FAIL: _______

---

## Gate 5 — Business endpoints
**Expected outputs**
- [ ] `GET /api/v1/business` works (JWT)
- [ ] `PATCH /api/v1/business` updates `name` ONLY
- [ ] store_code cannot be changed (reject)
- [ ] tenant scoping enforced (no cross-tenant leak)

✅ PASS / ❌ FAIL: _______

---

## Gate 6 — Products + Upload
**Expected outputs**
- [ ] CRUD under `/api/v1/products` works (JWT)
- [ ] create/update accepts `base_price_naira` (int) and stores `base_price_kobo`
- [ ] delete is soft-disable (`is_active=false`)
- [ ] upload endpoint saves to `media/products/<uuid>.<ext>`
- [ ] upload returns `image_url` under `/media/products/...`
- [ ] tenant scoping enforced

✅ PASS / ❌ FAIL: _______

---

## Gate 7 — Delivery zones
**Expected outputs**
- [ ] CRUD under `/api/v1/delivery-zones` works (JWT)
- [ ] accepts `fee_naira` (int) stores `fee_kobo`
- [ ] delete soft-disables
- [ ] tenant scoping enforced

✅ PASS / ❌ FAIL: _______

---

## Gate 8 — Payout setup (Paystack subaccount)
**Expected outputs**
- [ ] `POST /api/v1/payout/setup` stores payout_profile + subaccount_code on success
- [ ] `GET /api/v1/payout/status` returns correct profile
- [ ] httpx calls exist ONLY in Paystack client/service, not router
- [ ] provider failures are returned with consistent error shape
- [ ] tests mock Paystack client (no real HTTP in tests)

✅ PASS / ❌ FAIL: _______

---

## Gate 9 — Orders core + expiry guard
**Expected outputs**
- [ ] reserve creates:
  - [ ] Customer upsert (business_id + channel_type + channel_user_id)
  - [ ] Order status reserved
  - [ ] expires_at = now + 60 minutes
  - [ ] OrderItems snapshots (name_snapshot, unit_price_kobo, qty, line_total_kobo)
  - [ ] subtotal_kobo + delivery_fee_kobo + total_kobo + platform_fee_kobo + business_payout_kobo
- [ ] mark-delivered rejects unless order is paid
- [ ] expiry-on-access implemented (helper exists)

✅ PASS / ❌ FAIL: _______

---

## Gate 10 — Set delivery + recalc + expiry enforced
**Expected outputs**
- [ ] `POST /api/v1/orders/{id}/set-delivery`
  - [ ] allowed ONLY when status=reserved
  - [ ] rejects if expired (and sets expired)
  - [ ] recalculates delivery_fee_kobo, total_kobo, platform_fee_kobo, business_payout_kobo
- [ ] tests cover recalc and expiry rejection

✅ PASS / ❌ FAIL: _______

---

## Gate 11 — Payments init + Paystack webhook (core money truth)
**Expected outputs**
**Pay init**
- [ ] only if reserved AND not expired AND payout_profile active
- [ ] requires customer_email else 400 EMAIL_REQUIRED
- [ ] preferred init uses: currency="NGN", subaccount, transaction_charge=platform_fee_kobo
- [ ] fallback init exists (collect to platform) and does NOT block payment
- [ ] Payment created: status initiated, amount_kobo=order.total_kobo, reference unique
- [ ] order.status becomes payment_pending (not paid)

**Webhook**
- [ ] verifies `x-paystack-signature` = HMAC SHA512(raw_body, PAYSTACK_SECRET_KEY)
- [ ] reference must exist
- [ ] amount must equal order.total_kobo
- [ ] idempotent: second webhook does nothing
- [ ] ONLY here sets order.status=paid

✅ PASS / ❌ FAIL: _______

---

## Gate 12 — Receipts PDF + endpoint
**Expected outputs**
- [ ] webhook success triggers receipt generation
- [ ] PDF written to `media/receipts/<uuid>.pdf`
- [ ] Receipt row stored with receipt_number + pdf_url
- [ ] `GET /api/v1/receipts/{order_id}` returns receipt

✅ PASS / ❌ FAIL: _______

---

## Gate 13 — Telegram adapter
**Expected outputs**
- [ ] endpoint: `/api/v1/channels/telegram/webhook/{token}`
- [ ] token validation enforced (reject wrong token)
- [ ] commands supported (text-only):
  - [ ] `/start <STORE_CODE>`
  - [ ] `products`
  - [ ] `buy <product_id> <qty>`
  - [ ] `delivery <zone_id> <address>`
  - [ ] `pay`
- [ ] message_log records inbound/outbound
- [ ] adapter calls services only (no DB in router)

✅ PASS / ❌ FAIL: _______

---

## Gate 14 — WhatsApp adapter
**Expected outputs**
- [ ] GET verification handshake works (WHATSAPP_VERIFY_TOKEN)
- [ ] POST handler parses messages
- [ ] requires `START <STORE_CODE>` to set context
- [ ] same commands as Telegram
- [ ] message_log records inbound/outbound

✅ PASS / ❌ FAIL: _______

---

## Gate 15 — Gemini assist (only after gates 1–14 pass)
**Rule: do NOT start if Gate 11–12 aren’t stable.**

**Expected outputs**
- [ ] AI_ENABLED global flag + per-business ai_enabled default false
- [ ] AIAudit table logs every call
- [ ] endpoints under `/api/v1/ai` (JWT)
- [ ] AI never changes order/payment state or totals
- [ ] any AI ordering requires explicit CONFIRM before reserve (if wired later)

✅ PASS / ❌ FAIL: _______

---

# “Stop building” red flags (instant FAIL)
- [ ] Any router uses DB session directly
- [ ] Any router calls httpx directly
- [ ] Any endpoint sets order.status="paid" outside webhook
- [ ] Money stored as float/decimal in DB
- [ ] Currency accepted from client
- [ ] Webhook skips signature verification or amount match
- [ ] Missing idempotency (duplicate webhook double-updates)
