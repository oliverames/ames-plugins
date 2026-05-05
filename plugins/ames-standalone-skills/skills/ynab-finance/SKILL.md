---
name: ynab-finance
description: Household finance management powered by YNAB. Use when doing a monthly spending review, reconciling accounts, creating income/expense summaries, generating net worth statements, analyzing budget variances, preparing financial snapshots, planning for the next month, checking savings rate, reviewing cash flow, doing a month-end close, comparing budget vs actual spending, or any YNAB-related financial task. Also trigger for "how much did I spend", "am I on budget", "financial health check", or "what's my net worth".
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

If the request spans multiple workflows (e.g., "do my month-end review"), start with `monthly-close.md` — it references the others as sub-steps.

## Transaction Approval Workflow

### Before approving a batch

Never batch-approve transactions based on vague phrasing like "the other items" or "everything else." Always:

1. List the exact transactions you intend to approve (payee, amount, category)
2. Wait for explicit confirmation before calling `update_transactions` with `approved: true` on more than 3 transactions at once
3. State clearly which transactions you are **not** approving and why

### Flags from `review_unapproved`

Pay attention to the `flags` field on each transaction:

| Flag | Meaning | Action |
|------|---------|--------|
| `manually_entered` | Not from bank import; was hand-keyed | Confirm it's intentional |
| `match_broken` | Has a stale match reference | Do not approve; ask user to verify |
| `no_prior_amount_match` | First time this amount has appeared for this payee | Flag for user review before approving |
| `category_drift:was_X` | Payee was previously in a different category | Ask if recategorization was intentional |
| `new_payee` | No transaction history for this payee | Confirm payee and category before approving |
| `scheduled_transaction_realized` | Originated from a scheduled entry | Verify amount and category match expectations |

Transactions with `match_broken` or `manually_entered` + `no_prior_amount_match` should always require explicit user sign-off before approval, regardless of how many other clean transactions are being approved.

### Gmail receipt verification

When verifying a charge via Gmail:
- Search: `from:no_reply@email.apple.com subject:receipt after:YYYY/MM/DD` for Apple charges (not broad "Apple" searches which return trade-in, subscription expiry, and other noise)
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
