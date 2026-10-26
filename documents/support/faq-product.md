---
title: Product Frequently Asked Questions
document_id: product-faq
category: product
status: current
version: 2025.2
effective_date: 2025-03-05
audience: customers-and-support
owner: Product Operations
---

# Who can export data?

Workspace Owners and Workspace Administrators can start workspace exports from Settings > Data > Export. Members and viewers cannot start exports.

# What happens to a cancelled workspace?

A cancelled workspace becomes read-only when its billing period ends. It remains available for 30 days before scheduled deletion. Administrators should export data during that period.

# Why is an export still processing?

Large exports are prepared asynchronously. A workspace can have two running export jobs. A third job waits in the queue. If an export fails, retry once and give Support the job ID if it fails again.

# What happens when an API client exceeds its limit?

The API returns a rate-limit response. The client should retry with exponential backoff. The request limit depends on the workspace plan.
