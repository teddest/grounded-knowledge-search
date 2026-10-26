---
title: Failed Payment Procedure
document_id: failed-payment-procedure
category: billing
status: current
version: 2025.1
effective_date: 2025-02-01
audience: support-and-finance
owner: Finance Operations
---

# First failed attempt

When a recurring payment fails, Relay marks the invoice as payment-failed and sends the billing contact an email. The subscription remains active during the first retry period. Support should confirm the billing contact, payment-method last four digits, and invoice ID without requesting the full card number.

# Retry schedule

Relay retries the payment automatically after 24 hours and again after 72 hours. The billing contact can update the payment method from Settings > Billing. A successful retry clears the payment-failed state.

# Suspension

If all retries fail, the workspace enters a seven-day grace period. During grace, the workspace remains usable but displays a billing warning. At the end of grace, the workspace becomes read-only. Support must not manually remove the read-only state without Finance Operations approval.

# Escalation

Support escalates immediately when the customer reports an unauthorized charge, a duplicate charge, an account compromise, or a payment that succeeded at the bank but remains failed in Relay. Routine retry questions remain with Support unless the retry schedule has been exhausted.

# Refund relationship

A failed payment is not itself a refund event. If the customer was charged and requests a refund, Support follows the current Refund and Credit Policy and records the invoice ID.
