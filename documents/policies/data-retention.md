---
title: Workspace Data Retention Policy
document_id: data-retention-policy
category: security-and-privacy
status: current
version: 2025.2
effective_date: 2025-03-10
audience: customers-and-support
owner: Security and Privacy
---

# Active workspaces

Relay retains customer workspace data while the subscription is active. Customers can delete individual records when their role permits the operation. Deletion events are recorded in the audit log.

# Cancelled workspaces

When a subscription ends, the workspace enters read-only status for 30 days. During this period, an administrator can export eligible data or request reactivation. At the end of the 30-day period, the workspace is scheduled for deletion.

# Deletion schedule

Scheduled deletion removes primary workspace data within seven days after the retention period ends. Encrypted backups may retain deleted records for up to 35 additional days before their normal rotation. Backup copies are not available through the product interface.

# Legal and security holds

A legal hold, active security investigation, or written request from the Security and Privacy owner pauses scheduled deletion. Support must not place or remove a hold. Requests must be escalated to Security and Privacy with the workspace ID and reason.

# Customer communication

Support should explain the 30-day read-only period and the additional backup rotation period without promising an exact deletion timestamp. Questions about regulatory deletion requirements belong with Security and Privacy.
