---
title: Workspace Export and Roles
document_id: workspace-export-roles
category: product
status: current
version: 2025.2
effective_date: 2025-03-01
audience: customers-and-support
owner: Product Operations
---

# Export capability

Relay workspace administrators can export workspace records from **Settings > Data > Export**. An export creates a downloadable archive containing eligible records in JSON and CSV formats. Large exports are prepared asynchronously, and Relay emails the requesting administrator when the archive is ready.

# Export permissions

The Workspace Owner and Workspace Administrator roles can start an export. Members and viewers cannot start exports. A support agent cannot export customer data from the customer workspace unless the customer grants temporary administrator access through the approved support process.

# Export limitations

Exports do not include passwords, authentication secrets, encrypted payment details, or data from another workspace. Audit events record the requesting user, export scope, and completion status. An export link expires after 72 hours.

# Failed exports

If an export fails, the administrator should retry once. If the retry fails, the administrator records the export job ID and contacts Support. Support escalates repeated failures to Support Engineering with the job ID, workspace ID, and approximate start time.

# Deletion and exports

An export request does not pause the workspace deletion schedule. For a cancelled workspace, an administrator must request the export during the 30-day read-only period described in the Workspace Data Retention Policy.
