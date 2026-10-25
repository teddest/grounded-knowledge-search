---
title: Relay Usage Limits
document_id: relay-usage-limits
category: product
status: current
version: 2025.1
effective_date: 2025-02-20
audience: customers-and-support
owner: Product Operations
---

# Record limits

A Relay workspace may store up to 500,000 active records on the Standard plan and 2,000,000 active records on the Enterprise plan. Archived records count toward storage capacity until they are permanently deleted.

# Export limits

A workspace may have two export jobs running at the same time. A third request remains queued until one of the existing jobs completes or fails. The export service rejects archives larger than 50 GB; Support Engineering reviews larger export requirements.

# API request limits

The public API permits 600 requests per minute per workspace on Standard and 2,000 requests per minute per workspace on Enterprise. A client that exceeds its limit receives a rate-limit response and should retry with exponential backoff.

# Approaching a limit

Relay displays a warning when a workspace reaches 80 percent of a plan limit. Support should confirm the metric and plan before recommending an upgrade. A warning is not proof that a limit has been exceeded.
