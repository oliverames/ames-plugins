# Categorization Workflow

Distinct from approval. Categorization assigns a `categoryId` to a transaction. Approval marks it confirmed. Always categorize first, approve second.

## When to use

- `review_unapproved` returns `needs_category_first` transactions
- Routine monthly close has a backlog of `Uncategorized` transactions
- A user-initiated "review my new payees" request

## The two-pass pattern

### Pass 1: Categorize (no approval)

For each uncategorized transaction:

1. **Identify the payee** using both `payee_name` (cleaned) and `import_payee_name_original` (raw bank string — often more informative; contains city, state, processor flags like "AplPay" or "SP" for Square)
2. **Propose a category** based on payee context (location, amount, recurrence)
3. **Confirm with user before applying** — never assume

Confidence tiers help structure the user conversation:

| Tier | Treatment |
|---|---|
| High confidence (unambiguous payee + clear category match) | Group together, ask for blanket approval |
| Medium confidence (right category group but needs sub-choice, e.g., which kid) | Ask one question per group |
| Low confidence (payee is truncated, unfamiliar, or could be any of several categories) | Ask the user what each was |

Apply via `update_transactions(transactions: [{id, categoryId}])`. **Do NOT set `approved: true` in this pass.**

### Pass 2: Approve

After categorization is correct, run a second `update_transactions` call setting `approved: true` for each previously-categorized transaction. This separation:

- Lets the user spot-check categorizations before they become "settled"
- Honors the skill's "never approve >3 at once without explicit confirmation" rule
- Matches YNAB's mental model

### Combined pass (allowed when user has explicitly approved both)

Once the user has approved both categories AND the batch approval, you may combine them into a single `update_transactions` call with both `categoryId` and `approved: true` per entry.

## ID handling — critical

**Never fabricate transaction IDs.** Always extract real IDs from:

1. `review_unapproved` output, or
2. A `get_transactions` result, or
3. A saved tool-result file

If a tool result overflowed and was saved to disk, parse the JSON file (Python or jq) to extract IDs and category IDs together, then write the batch payload to a temp file before passing it to `update_transactions`. This avoids transcription errors on long lists.

A failed batch with "transaction does not exist in this budget" on most entries is the signature of fabricated IDs — verify against the source data file before retrying.

## Handling YNAB drift

When historical transactions for a recurring payee + amount have drifted into a different category from their canonical home (e.g., Apple Services $27.63 Apple One charge ends up in "Oliver" personal instead of "🍏 Apple One"), include a recategorization step:

1. Identify the canonical category by looking at prior months' transactions for the same payee + amount
2. Surface the drift to the user with a sample (e.g., "5 prior $27.63 charges went to Apple One; this latest one went to Oliver")
3. Get user OK before recategorizing
4. Apply category fix in the same batch as approval

The `category_drift:was_X` flag from `review_unapproved` surfaces these candidates automatically.

## Handling `match_broken`

`match_broken` transactions cannot be fixed via the YNAB API. The matched-transaction reference is stale and needs YNAB's reconciliation UI to resolve.

**Action:** Do NOT call `update_transactions` to approve these. Tell the user to fix in YNAB's web or iOS app:

- For `manually_entered + match_broken + scheduled_transaction_realized` (typical pattern for installment payments): delete the manually-entered duplicate, keep the scheduled-realized version
- For `match_broken` on a transfer pair: reconcile the pair manually so YNAB re-links them

Leaving these unapproved in the batch is correct — they should remain visible in the unapproved queue until the user resolves them.

## Handling new payees

When a payee is `new_payee`, the proposed category should be verified with the user, even if the category is obvious. Reason: this is the moment to catch a wrong import payee assignment that would otherwise propagate (e.g., a one-time car wash assigned to a recurring "Car Maintenance" category when it should be Personal Spending → Oliver).

Watch for:

- Out-of-state merchants on a primarily local card (potential fraud or forgotten trial)
- Square / SP processor charges with truncated names — verify by checking `import_payee_name_original`'s city/state for sanity
- Apple Pay charges that look like subscriptions but are one-time purchases

## Splitting transactions

The MCP doesn't support split transactions in update calls (as of v1.7.0). When a single charge needs to be split across multiple categories (e.g., a grocery run that includes household items, or kids' clothing for both Henry and Emmett):

1. Categorize to the most-dominant category for now
2. Tell the user to split in YNAB's UI

Don't try to work around this with adjusting amounts — it would break reconciliation.

## Verification before approving large batches

Before calling `update_transactions` with `approved: true` on more than ~10 transactions:

1. Show the user a sample grouped by payee + category + count + total
2. Wait for explicit confirmation
3. Surface any concerning flags in the sample (especially `match_broken` and `category_drift`)
4. Approve only the clean ones; leave flagged ones for manual user review

The "summary first, then approve" cadence reads cleanly to users and prevents bulk errors.
