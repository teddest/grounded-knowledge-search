# Grounded Knowledge Search

This repository contains an educational document-search application and a fictional policy and procedure corpus.

## Dataset

**Northstar Relay** is the example dataset. It covers billing, onboarding, product behavior, support escalation, security, and incident response.

## Project planning

The implementation is planned with [OpenSpec](https://github.com/Fission-AI/OpenSpec). The proposal, design, requirements, and PR-sized task plan are in `openspec/changes/document-search-foundation/`.

## Document conventions

Each document begins with YAML front matter containing metadata that a search system can index:

- `title`
- `document_id`
- `category`
- `status`
- `version`
- `effective_date`
- `audience`
- `owner`

The 2024 and 2025 refund policies intentionally overlap. The 2025 policy is current and should take precedence when a question asks for the current policy. The 2024 policy remains useful for historical questions.

## Suggested search questions

- Can an annual customer receive a refund after 30 days?
- What happens after a payment fails?
- When should support escalate a failed payment?
- What changed in the refund policy between 2024 and 2025?
- How do I export a workspace?
- Which role can export customer data?
- What is the process for onboarding a new customer?
- How long are deleted workspace records retained?
- What should support do during a security incident?
- Is there a policy for exceptions to the standard refund window?

This corpus is synthetic and contains no real customer or company data.
