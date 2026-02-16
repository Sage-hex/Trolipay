# AGENTS.md — ChatCommerce v1 STRICT IMPLEMENTATION RULES

## Source of Truth

- SPEC_v1_TECH_STRICT.md is the authoritative specification.
- If any prompt conflicts with the spec, follow SPEC_v1_TECH_STRICT.md.

---

## HARD CONSTRAINTS (MUST NOT BE BROKEN)

### API

- ALL routes MUST be under /api/v1 (including webhooks).
- Webhooks MUST be:
  - /api/v1/webhooks/paystack
  - /api/v1/channels/telegram/webhook/{token}
  - /api/v1/channels/whatsapp/webhook

---

### MONEY

- All money stored ONLY as integer kobo.
- All money fields MUST end with `_kobo`.
- Admin input MUST be whole naira integers only.
- Conversion: kobo = naira \* 100.
- platform_fee_kobo = ceil(total_kobo \* 0.015).
- business_payout_kobo = total_kobo - platform_fee_kobo.
- Currency is fixed to "NGN" in v1.
- Currency MUST NOT be accepted from client input.

---

### PAYMENT TRUTH

Order becomes `paid` ONLY inside Paystack webhook handler after ALL checks:

1. Verify header `x-paystack-signature`.
2. Compute HMAC SHA512 of RAW request body using PAYSTACK_SECRET_KEY.
3. Compare using constant-time comparison.
4. Validate payment reference exists.
5. Validate payment amount == order.total_kobo.
6. Enforce idempotency:
   - If payment already success, return OK without modifying order.
7. Only then:
   - payment.status = success
   - order.status = paid
   - generate receipt

There MUST NOT be any manual "mark paid" endpoint.

---

### PAYSTACK SPLIT STRATEGY (Pipeline A)

- Backend creates subaccount and stores subaccount_code.
- During transaction initialize:
  - Use subaccount field.
  - Set transaction_charge = platform_fee_kobo.
- If split initialization fails:
  - Fallback: initialize without subaccount.
  - Still record platform_fee_kobo and business_payout_kobo.
  - Do NOT block payment.

---

### MULTI-TENANCY

- Admin endpoints derive business_id ONLY from JWT.
- business_id MUST NEVER be accepted in request bodies.
- Every repository query MUST scope by business_id.
- Cross-tenant access MUST return 404 consistently.

---

### ORDER EXPIRY (MANDATORY)

- expires_at = now + 60 minutes at reserve.
- On ANY pay-init or set-delivery:
  - If now > expires_at AND not paid:
    - Set order.status = expired.
    - Reject operation.

---

### SEPARATION OF CONCERNS

- Routers:
  - Validate + auth + call service + return response.
  - NO DB calls.
  - NO external HTTP calls.
- Services:
  - Business logic.
  - Call repos and integration clients.
- Repositories:
  - DB only.
- Integration clients:
  - HTTP only.
  - No DB access.

---

### STORAGE

- Use local filesystem only:
  - media/products
  - media/receipts
- Serve via /media.
- Filenames MUST be uuid-based and unguessable.

---

### CHANNEL SECURITY

- Telegram webhook MUST validate secret token in URL path.
- WhatsApp webhook MUST implement GET verification handshake.

---

### EMAIL REQUIREMENT

- Paystack init requires customer email.
- If email missing:
  - Return 400 with error code EMAIL_REQUIRED.

---

### GEMINI

- Gemini MUST NOT be implemented before payment loop is stable.
- Gemini is assist-only.
- Gemini MUST NOT modify order/payment state.
- AI-based ordering MUST require explicit customer CONFIRM before reserve.

---

## STRICT BUILD ORDER (DO NOT SKIP)

1. bootstrap + config + db + /health + /media
2. models + migrations
3. money helpers + tests
4. auth
5. business endpoints
6. products
7. delivery zones
8. payout setup
9. orders + expiry enforcement
10. payments init + webhook validation
11. receipts
12. telegram adapter
13. whatsapp adapter
14. gemini (optional, off by default)

---

## CODEX RESPONSE FORMAT

When implementing a block:

- Implement ONLY that block.
- Provide:
  1. file tree of changes
  2. full content of new/changed files
  3. run commands
- No unrelated refactors.
