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

### Always re-query for IDs immediately before applying an update

Two related failure modes both have the same fix:

**Stale-snapshot bug.** You ran `review_unapproved` once, captured the IDs in `ready_to_approve`, then categorized N transactions from `needs_category_first`. Those N transactions moved from `needs_category_first` into `ready_to_approve`. If your approval batch was built from the original snapshot, those N are silently excluded. **Fix**: re-run `review_unapproved` between Pass 1 (categorize) and Pass 2 (approve), and build the approval batch from the fresh snapshot.

**Remembered-ID bug.** Over a long session, transaction IDs accumulate in the context window. When asked to update a specific transaction by payee/amount/date description, it's tempting to reach into context memory and grab the ID. That ID might belong to a *different* transaction that's also in context. **Fix**: even when an ID seems to be in context, run a fresh `get_transactions(payeeId=..., sinceDate=...)` query right before calling `update_transaction`/`update_transactions`. The extra call is cheap; the wrong-transaction-update is expensive (silently corrupts data, requires a revert).

Both failures look the same on the surface: the `update_transactions` call returns success, but the wrong rows changed. The cost is a verification pass later to spot the discrepancy. Re-querying just before the write closes the gap.

## Amazon-transaction identification via Gmail (reusable pattern)

YNAB Amazon transactions don't include item descriptions, so memos and categories often end up generic. Each Amazon transaction's `import_payee_name_original` field carries the order ID suffix (e.g. `AMAZON MKTPL*BJ3EI8X12` or `Amazon.com*BF8CM1PQ1`), which can be matched to a Gmail order confirmation to identify the item and route it to the right category.

### Workflow

1. `get_transactions(payeeId=<Amazon>, sinceDate=...)` to pull the YNAB transactions
2. Gmail search:
   - `from:auto-confirm@amazon.com after:YYYY/MM/DD before:YYYY/MM/DD` (order confirmations)
   - `from:shipment-tracking@amazon.com after:YYYY/MM/DD before:YYYY/MM/DD` (shipment notices — useful when the order subject is truncated; shipment subjects often have a fuller item name)
3. Match each YNAB charge to a Gmail order by:
   - **Date**: Amazon usually ships 0-3 days before the YNAB charge posts
   - **Amount**: exact match in the order confirmation body (or the shipment receipt body)
   - **Order ID**: when multiple charges land on the same day, disambiguate using the order ID suffix from `import_payee_name_original`
4. Subject lines like `Ordered: "Item description..."` are usually enough to write a clean memo. Fall back to `get_thread(messageFormat: FULL_CONTENT)` only if the subject is too truncated to identify the item.
5. Propose memo + category for each, then apply via batch `update_transactions`.

### When to use this pattern

- During a monthly close, when a backlog of Amazon transactions sits unapproved and uncategorized
- During a household budget review, when one person's category looks inflated and needs disaggregation
- After a multi-shipment order, where Amazon bills each shipment separately and the charges look like unrelated mystery line items

### Common matching gotchas

- **Same amount, different orders**: Subscribe & Save items recur (e.g., two Bounty $44.21 charges 2 days apart). Use order ID suffix to disambiguate.
- **Multi-shipment orders**: One Amazon order can split into 3-5 charges as items ship separately. The order confirmation email lists the total, but each charge is just one shipment's subtotal + tax.
- **Returns**: Amazon refunds show as positive amounts (`amount > 0`); they typically land in the same category as the original purchase, which is correct YNAB behavior. Don't recategorize unless the original was wrong.

### Reusable for non-Amazon vendors

The same pattern works for any vendor that sends per-order email confirmations: Apple Store hardware, Amazon Fresh, Whole Foods, ButcherBox, etc. The key inputs are an `import_payee_name_original` carrying an order identifier and a vendor-side email with searchable headers. For aggregator-billed subs (Apple App Store) where the vendor doesn't email separately, this pattern won't help — fall back to on-device subscription management.

## Handling YNAB drift

When historical transactions for a recurring payee + amount have drifted into a different category from their canonical home (e.g., Apple Services $27.63 Apple One charge ends up in "Oliver" personal instead of "🍏 Apple One"), include a recategorization step:

1. Identify the canonical category by looking at prior months' transactions for the same payee + amount
2. Surface the drift to the user with a sample (e.g., "5 prior $27.63 charges went to Apple One; this latest one went to Oliver")
3. Get user OK before recategorizing
4. Apply category fix in the same batch as approval

The `category_drift:was_X` flag from `review_unapproved` surfaces these candidates automatically.

## Handling `match_broken`

`match_broken` means a transaction's `matched_transaction_id` field references a stale or deleted record. **That field is read-only via the YNAB API** — there is no `update_transaction` input for it. **But the rest of the transaction is fully mutable**: `categoryId`, `memo`, `approved`, `flagColor`, `cleared` all work normally via the API.

**Action:** Get explicit user sign-off on what the transaction is (the broken link points at something — verify before approving), then proceed normally with `update_transactions`. The cosmetic match-broken state will persist in YNAB's UI until the user clears it manually, but it does NOT block approval or recategorization in the audit workflow.

Common patterns:

- **Manually-entered installment with a stale scheduled template** (e.g., an Apple Watch payment that auto-imports + has a scheduled-template realization): verify with the user what the charge is, then `update_transactions({ id, approved: true })`. The user can untangle the scheduled template in YNAB web UI later — or leave the cosmetic flag alone if it's not bothering them.
- **`manually_entered + match_broken + scheduled_transaction_realized` together**: often a true duplicate. Verify with the user. If duplicate, delete the manually-entered side; if not, approve.
- **`match_broken` on a transfer pair**: rare. Pull both sides via `get_transactions(accountId=X)` for both linked accounts, verify the transfer is real, then approve. See "Common audit patterns → Transfer-pair cleared-state diagnostic" in SKILL.md.

## Handling new payees

When a payee is `new_payee`, the proposed category should be verified with the user, even if the category is obvious. Reason: this is the moment to catch a wrong import payee assignment that would otherwise propagate (e.g., a one-time car wash assigned to a recurring "Car Maintenance" category when it should be Personal Spending → Oliver).

Watch for:

- Out-of-state merchants on a primarily local card (potential fraud or forgotten trial)
- Square / SP processor charges with truncated names — verify by checking `import_payee_name_original`'s city/state for sanity
- Apple Pay charges that look like subscriptions but are one-time purchases

## Splitting transactions

`update_transaction` and `update_transactions` do not accept a `subtransactions` field — YNAB's API only allows splits at create-time. To convert an existing single-category transaction into a split (e.g., a $100 check covering passport fees for two kids), use the **delete + recreate workaround**:

1. Capture the original transaction's fields: `account_id`, `date`, `amount`, `payee_id`/`payee_name`, `cleared`, `import_id`
2. `delete_transaction(transactionId)` — YNAB soft-deletes and retains the `import_id` reservation, so the bank can't re-import the deleted record as a phantom
3. `create_transaction({ accountId, date, amount, payeeId, cleared, approved, importId: "<new-marker>", subtransactions: [{amount, categoryId, memo}, ...] })` — supply a NEW `importId` (e.g., `"split-<date>-<context>"`) so the new record has its own deduplication anchor

The subtransaction amounts must sum to the parent amount (negative for outflow splits). Each subtransaction can carry its own `categoryId`, `payeeId`, `payeeName`, and `memo`.

**Direct-split-at-create is always preferred** when you control the transaction lifecycle. The delete + recreate path is the recovery move for transactions that already exist as singles in YNAB.

**Cleared status note**: if the original was `cleared` (bank-confirmed), set the new one to `cleared` too so reconciliation math stays consistent. If `uncleared`, leave the new one `uncleared` and let the bank resolve.

**Don't try to work around splitting by adjusting amounts** — that would break reconciliation against the bank statement.

## Verification before approving large batches

Before calling `update_transactions` with `approved: true` on more than ~10 transactions:

1. Show the user a sample grouped by payee + category + count + total
2. Wait for explicit confirmation
3. Surface any concerning flags in the sample (especially `match_broken` and `category_drift`)
4. Approve only the clean ones; leave flagged ones for manual user review

The "summary first, then approve" cadence reads cleanly to users and prevents bulk errors.
