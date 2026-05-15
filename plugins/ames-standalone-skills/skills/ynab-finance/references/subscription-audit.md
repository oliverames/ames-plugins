# Subscription Audit

A structured pass to inventory all active subscriptions across YNAB transaction history plus external sources, identify duplicates and orphans, and surface candidates for cancellation. Distinct from monthly close — this is a cross-cutting audit that spans 3-12 months.

## When to run this

- User mentions "cancel subscriptions", "audit subs", "review what I'm paying for"
- Quarterly per `monthly-close.md` (the "review subscription list — cancel anything unused" checkbox)
- Whenever a credit-card statement feels heavier than expected

## Pre-requisites: confirm the identity surface

Subscriptions hide behind multiple identities. Before pulling any data, ask the user to confirm which identities are in scope. Typical buckets:

| Identity type | Examples | Where subs hide |
|---|---|---|
| Personal email | `<name>@gmail.com` | Direct-vendor receipts; ChatGPT, Strava, Netflix, etc. |
| Personal Apple ID | `<name>@<personal-domain>` | App Store subscriptions billed via Apple Services |
| Business Apple ID | `<name>@<consulting-domain>` | App Store subscriptions on business Apple ID; Microsoft 365 via App Store |
| LLC business email | `<name>@<llc-domain>` | Direct-vendor receipts; LinkedIn Premium, Adobe CC, MS365 Apps for business |
| Spouse / shared Apple ID | Family Sharing apple IDs | Family subscription confirmations |
| Alumni / education email | `<name>@<edu-domain>` | EDU-priced subs (e.g., Mistral via .edu, JetBrains Student) |

The same vendor commonly has **multiple separate subscriptions across identities** (e.g., three concurrent Microsoft 365 plans on three identities). Catching duplicates is the highest-impact part of the audit.

## Time window

Default to **6 months** of history. Trade-offs:

| Window | Catches | Misses |
|---|---|---|
| 3 months | Monthlies, quarterlies | Annual renewals |
| **6 months (default)** | Monthlies + biannuals + most annuals | Some 12-month renewals |
| 12 months | All annual renewals | Adds noise from one-off purchases |

## Workflow

### 1. YNAB scheduled (manual entries only)

```
list_scheduled_transactions
```

**Caveat:** this only returns manually-created recurring entries. Auto-imported subs do NOT appear here. Use this as a baseline of explicit recurring items the user has set up themselves.

### 2. Subscription-category transactions

```
list_categories  → find category groups: "Subscriptions", "Devices & Phones", "Annual & Goals"
get_transactions(categoryId=<each subscription category>, sinceDate=<6mo ago>)
```

This catches subs the user has already organized into YNAB categories.

### 3. Aggregator-payee transactions

Apple App Store and Paddle handle large fractions of software subs. Find their payee IDs once, then pull all activity:

```
search_payees(query="apple")
search_payees(query="paddle")
get_transactions(payeeId=<Apple Services>, sinceDate=<6mo ago>)
get_transactions(payeeId=<Paddle>, sinceDate=<6mo ago>)
```

If `get_transactions` overflows the response cap, prefer `summary: true` first, then drill into specific date ranges.

### 4. LLC / Work Expenses category

```
get_transactions(categoryId=<💻 Work Expenses>, sinceDate=<6mo ago>)
```

Many business subs (LinkedIn Premium, Adobe CC, Google Cloud, domain registrars, dev tools) hit this category and need to be evaluated separately because:
- They may be tax-deductible — cancellation lowers business deductions
- They may be billed to a different card (business credit) than personal subs
- They may be paid via a direct vendor relationship, not aggregator

### 5. Gmail cross-reference

YNAB alone misses subs that hide in batched aggregator receipts (e.g., one Apple Services charge = 5 itemized subs in a Gmail receipt). Cross-reference:

| Search | Reveals |
|---|---|
| `from:no_reply@email.apple.com subject:receipt after:YYYY/MM/DD` | Apple App Store charges with itemized subs |
| `from:paddle.com after:YYYY/MM/DD` | Paddle-billed software (CleanMyMac, Fastmail, MacPaw, Setapp, Mimestream) |
| `from:invoice+statements after:YYYY/MM/DD` | Direct-vendor Stripe receipts (Anthropic, Tailscale, Raycast, Mistral) |
| `subject:(subscription OR renewal OR "auto-renew" OR "your plan") after:YYYY/MM/DD -category:promotions` | Generic subscription mail |
| `from:microsoft-noreply@microsoft.com after:YYYY/MM/DD` | All Microsoft account activity |

### 6. Identity-specific direct-vendor sweep

For each identity in scope, search Gmail for receipts addressed to that identity:

```
to:<identity> (subject:invoice OR subject:receipt OR subject:subscription) after:YYYY/MM/DD
```

Catches business subs that hit the LLC card but route receipts to the business email.

### 7. Specific high-value vendors

Some vendors don't surface via the generic sweeps. Always check explicitly:

- NVIDIA / GeForce NOW (`from:nvidia.com`)
- PlayStation Plus (`from:playstation.com`)
- ButcherBox / HelloFresh / meal kits
- Backblaze / cloud storage
- Anthropic Claude (`from:invoice+statements@mail.anthropic.com`)
- OpenAI / ChatGPT (`from:noreply@tm.openai.com`)
- Adobe (`from:message@adobe.com`)
- LinkedIn Premium

## Categorization of findings

For each identified subscription, place into one of:

| Bucket | Action |
|---|---|
| Already cancelled | Verify charge has stopped; note in inventory |
| Active and used | Keep; no action |
| Duplicate (same service on multiple identities) | Cancel the redundant copies; pick one canonical |
| Orphan (e.g., Adobe storage after main CC cancelled) | Cancel; was billing without delivering value |
| Free trial about to convert | Cancel before charge if not keeping |
| Unused or rarely used | Cancel |
| Pause-eligible (e.g., ButcherBox, meal kits) | Pause rather than cancel if user may resume |

## Refund opportunity check

Apple App Store: 60-day refund window for accidental renewals via reportaproblem.apple.com. Most useful for:

- Annual subs that just auto-renewed
- Subs that converted from a free trial within 60 days

Direct vendors vary; check vendor T&Cs.

## Output

A markdown inventory grouped by:

1. Already cancelled / ending (verify no new charges)
2. Active recurring — monthly
3. Active recurring — annual
4. Apple App Store batch (itemized)
5. LLC / business expenses
6. Cancellation candidates with monthly impact + cancellation path

Save to `~/Documents/Subscription Audit/YYYY-MM-DD_subscription-inventory.md`.

## Common drift patterns to flag

- **Same vendor on multiple identities**: Microsoft 365 commonly has 3 concurrent plans (personal Premium, Apps for business, Personal via App Store). Cancelling one does not cancel the others.
- **Orphan add-ons**: Adobe Storage charges after main CC is suspended. iCloud+ separate from Apple One Family inclusion.
- **Trial-converted subs**: Subscription Confirmed on day 1 → first charge ~30 days later under "Trial Over" memo. Easy to miss.
- **Apple Pay'd at a faraway location**: e.g., EverWash car wash sub started while traveling, billing continues at the original location.
