---
name: ynab-finance
description: >-
  Household finance management powered by YNAB. Covers monthly reviews,
  reconciliation, income/expense reporting, net worth tracking, savings
  rate, cash flow, and budget variance analysis.
when_to_use: >-
  Doing a monthly spending review, reconciling accounts, creating
  income/expense summaries, generating net worth statements, analyzing
  budget variances, preparing financial snapshots, planning for the next
  month, checking savings rate, reviewing cash flow, doing a month-end
  close, comparing budget vs actual spending, or any YNAB-related
  financial task. Also trigger for "how much did I spend", "am I on
  budget", "financial health check", or "what's my net worth".
---

# YNAB Finance

Household finance management: monthly reviews, reconciliation, income/expense reporting, net worth tracking, and variance analysis.

## Shared Context

- **Budget ID**: `f388de30-0c03-4628-a411-cff616b26bc6`
- **Data source**: All financial data comes from YNAB tools (`get_transactions`, `list_accounts`, `list_categories`, `get_month`, etc.). Investment, property, and loan data is provided by the user directly.
- **Formatting**: Use fixed-width columns for financial tables. Right-align dollar amounts. Show negative values in parentheses.
- **Savings rate formula**: `(Total Income - Total Spending) / Total Income x 100`

## Workflows

Pick the workflow that matches the user's request, then read the corresponding reference file:

| Request | Reference |
|---------|-----------|
| Monthly spending review, month-end close, budget planning | `references/monthly-close.md` |
| Income vs expense summary, savings rate report | `references/income-statement.md` |
| Net worth statement, financial snapshot, cash flow | `references/net-worth.md` |
| Reconcile accounts against bank statements | `references/reconciliation.md` |
| Why was spending over/under budget, spending trends | `references/variance-analysis.md` |
| Audit subscriptions across identities, cancel unused, find duplicates | `references/subscription-audit.md` |
| Assign categories to new payees, fix `Uncategorized` queue, propose/approve in batches | `references/categorization-workflow.md` |

If the request spans multiple workflows (e.g., "do my month-end review"), start with `monthly-close.md` — it references the others as sub-steps.

## Identity inventory

This budget owner operates across multiple email identities (personal Gmail, personal Apple ID domain, LLC consulting domain, alumni .edu, etc.). The same vendor frequently has independent subscriptions on different identities. Before any subscription or vendor audit, confirm which identities are in scope — cancellation on one identity does NOT propagate to the others. See `references/subscription-audit.md` for the identity-surface checklist.

## Transaction Approval Workflow

### Before approving a batch

Never batch-approve transactions based on vague phrasing like "the other items" or "everything else." Always:

1. List the exact transactions you intend to approve (payee, amount, category)
2. Wait for explicit confirmation before calling `update_transactions` with `approved: true` on more than 3 transactions at once
3. State clearly which transactions you are **not** approving and why

**Never fabricate transaction IDs.** Always extract them from a `review_unapproved`, `get_transactions`, or saved tool-result file. A failed batch with "transaction does not exist in this budget" on most entries is the signature of fabricated IDs. When tool results are too large for inline use (over ~50KB), parse the saved file with Python/jq to build the batch payload — never type IDs by hand.

For the full categorize-then-approve cadence, see `references/categorization-workflow.md`.

### Flags from `review_unapproved`

Pay attention to the `flags` field on each transaction:

| Flag | Meaning | Action |
|------|---------|--------|
| `manually_entered` | Not from bank import; was hand-keyed | Confirm it's intentional |
| `match_broken` | Has a stale match reference | API CAN approve, recategorize, and edit memo. Only the stale `matched_transaction_id` field is API-immutable (no schema input for it). Get user sign-off before approving — the broken link points at something, verify what. UI cleanup of the link is a separate cosmetic step the user owns. |
| `no_prior_amount_match` | First time this amount has appeared for this payee | Flag for user review before approving |
| `category_drift:was_X` | Payee was previously in a different category | Ask if recategorization was intentional |
| `new_payee` | No transaction history for this payee | Confirm payee and category before approving |
| `scheduled_transaction_realized` | Originated from a scheduled entry | Verify amount and category match expectations |

Transactions with `match_broken` or `manually_entered` + `no_prior_amount_match` should always require explicit user sign-off before approval, regardless of how many other clean transactions are being approved.

### Drift detection

When `category_drift` fires, surface the drift with evidence: list how many prior charges for the same payee + amount went to category A vs the current one going to B. Common drift sources:

- Recurring subs (Apple One, AppleCare) miscategorized to a generic personal-spending category by YNAB's auto-categorize when the payee has many one-off purchases there
- Aggregator-payee charges (Apple Services, Apple) where YNAB can't disambiguate between an app sub renewal and a one-time app purchase

Get user OK before fixing drift, then apply the recategorization in the same batch as approval (one `update_transactions` call with both `categoryId` and `approved: true`).

### Payee disambiguation: `import_payee_name_original`

When the cleaned `payee_name` is truncated, ambiguous, or doesn't ring a bell, look at the transaction's `import_payee_name_original` — the raw merchant string from the bank import. It encodes:

- **Payment processor**: `AplPay` (Apple Pay), `SP` (Square), `TST*` (Toast POS), etc.
- **Merchant name** (often longer than the cleaned `payee_name`)
- **City + state** (always the last two components)

Example: `Ls Onion Rive` is truncated and useless. But `AplPay LS ONION RIVEMONTPELIER VT` reveals the merchant was in Montpelier VT via Apple Pay — enough context to ask the user "I see two ~$16 charges at L.S. Onion River in Montpelier; what was this?"

## Common audit patterns

### Pending returns

When a purchase will be refunded but the refund hasn't posted yet:

1. Set `flag_color: "yellow"` and add a memo like `"Pending return — <item description>"` via `update_transactions`
2. Optionally recategorize to a `💰 Reimbursements` holding category (or leave in the original category)
3. When the refund posts (positive activity from the same merchant), it offsets automatically — the category nets out once both sides land

The yellow flag survives across reconciliation passes and is easy to spot when scanning the budget for unresolved items.

### Manual entry for non-imported transactions (Venmo, checks, cash)

Some payment methods don't auto-import: Venmo from a linked bank account, personal checks, cash. When the user has just made such a payment but it hasn't appeared in YNAB:

1. `create_transaction({ accountId: <source>, date: <today>, amount: -<dollars>, payeeName: "<descriptive>", categoryId: <target>, memo: "<context>", cleared: "uncleared", approved: true })`
2. Leave `importId` unset — the bank will reuse its own import_id when it eventually syncs, and YNAB matches on payee + amount + date
3. The transaction stays `uncleared` until the bank confirms, then YNAB promotes it to `cleared`

This keeps the audit's budget math accurate immediately rather than waiting 1-2 business days for the bank sync.

### Transfer-pair cleared-state diagnostic

A transfer between two on-budget accounts (or to an off-budget loan) creates two linked records: an outflow on the source and an inflow on the destination. Each side has independent `cleared` state:

| Outflow side | Inflow side | Diagnosis |
|---|---|---|
| `cleared` | `cleared` | Healthy — both confirmed |
| `cleared` | `uncleared` | Common: source bank confirmed but destination account hasn't synced yet. Loan accounts often lag weeks. Leave to clear naturally, or manually mark inflow `cleared` if you're confident. |
| `uncleared` | `cleared` | Rare. Source-side sync issue. Investigate. |
| `uncleared` | `uncleared` | Transfer in flight. Wait. |

Before deleting an "uncleared transfer" as a phantom, pull `get_transactions(accountId=<destination>)` and confirm the prior-month history. If every prior month shows a matching cleared transfer of the same amount + cadence and the uncleared one is the only one with that date+amount, it's legitimate — not a duplicate. Deleting it would orphan a real payment record.

### Payee-category drift from auto-categorization

Some merchants are systematically miscategorized by YNAB's auto-categorizer because they bill multiple distinct products under one payee:

- **Apple / Apple Services**: bills iCloud+, Apple One, Apple Care, individual app subscriptions, device installments all under one payee. The dollar amount is the only reliable disambiguator. Encourage the user to save a per-amount decoder table to auto-memory (e.g., `$29.99 → iCloud+`, `$27.63 → Apple One`, `$45.33 → Apple Watch payment`) so future audits don't re-derive it.
- **City of <town>**: collects property taxes AND water/sewer charges under one payee. `import_payee_name_original` is the canonical disambiguator — example: cleaned `payee_name` of "City of Montpelier" with raw `import_payee_name_original` of `External Withdrawal CITY OF MONTPELI - PROP TAX` reveals it's property tax, even though YNAB's auto-cat may have routed it to Water/Sewer.
- **Amazon**: bundles unrelated items per shipment; use the Amazon-via-Gmail workflow (`references/categorization-workflow.md`) to identify each charge by matching order ID suffixes.

When a user-specific decoder is needed, encourage saving it to auto-memory so future audits load it automatically.

### Gmail receipt verification

When verifying a charge via Gmail:
- Search: `from:no_reply@email.apple.com subject:receipt after:YYYY/MM/DD` for Apple charges (not broad "Apple" searches which return trade-in, subscription expiry, and other noise)
- **Apple receipt bodies are not retrievable**: even with `messageFormat: FULL_CONTENT`, the `get_thread` tool returns only the snippet for Apple receipt emails (heavily-styled HTML/MIME content the tool truncates). Do not call `get_thread` expecting the full itemized receipt — match by amount + date + recipient_email instead, and cross-reference with `import_payee_name_original` on the YNAB transaction.
- If `FULL_CONTENT` returns only a snippet (no dollar amount visible), state explicitly: "Email body not retrievable; could not verify amount via receipt"
- Do not claim verification succeeded if the email body was inaccessible

## Key Metrics

Track these across all workflows:

| Metric | Target |
|--------|--------|
| Savings rate | 20%+ |
| Fixed expense ratio | Under 50% of income |
| Debt-to-income ratio | Under 36% |
| Emergency fund coverage | 3-6 months |
| Credit card utilization | Under 30% |

## Financial Health Indicators

- **Green**: Net worth increasing, savings rate at/above target, no carried credit card balances, emergency fund at 3+ months
- **Yellow**: Net worth flat, savings rate below target, credit card balance growing, dipping into emergency fund
- **Red**: Net worth declining 3+ months, spending exceeds income, minimum payments only, no emergency fund
