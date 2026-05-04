# Month-End Review

A structured monthly review process for family finances — a lightweight "close" to review spending, reconcile accounts, update the budget, and plan ahead.

## Monthly Review Checklist

### 1. Reconcile Accounts (15 min)

- [ ] Reconcile checking account(s) against bank statement
- [ ] Reconcile credit card(s) against statements
- [ ] Reconcile savings account(s)
- [ ] Review and clear any uncleared transactions older than 7 days
- [ ] Verify YNAB balances match bank balances

For detailed reconciliation steps, see `references/reconciliation.md`.

### 2. Transaction Review (20 min)

Run `review_unapproved` first, then work through the queue systematically. Do NOT bulk-approve everything at once.

**Approval workflow:**
1. Group unapproved transactions by payee or category
2. Confirm categories with user per group before approving — some payees are ambiguous (e.g., a gym with a food-sounding name, a streaming credit miscategorized as a subscription)
3. Fix any miscategorizations FIRST, then approve — never approve then fix
4. For transfers to credit card accounts, "Uncategorized" is correct YNAB behavior — they don't need a spending category

**Income verification:**
- Call `get_transactions(month=..., sinceDate=...)` and filter for positive amounts
- Every external deposit (payroll, tax refunds, transfers in) should be in "Inflow: Ready to Assign"
- Flag any positive transaction landing in a spending category — it may be a misrouted deposit

**What `get_transactions(type='uncategorized')` returns:**
- Mostly internal transfers: credit card payments, loan payments, debt account starting balances
- This is expected YNAB behavior, not errors — don't chase these as miscategorizations

**Approved but miscategorized (easy to miss):**
- `review_unapproved` only surfaces unapproved transactions — already-approved transactions can still be wrong
- Scan approved transactions for payees that could be miscategorized: gyms with restaurant-sounding names, statement credits (e.g., an "AMEX DUNKIN' CREDIT" auto-categorized as a streaming bundle), refunds landing in the wrong category

### 3. Review Spending (15 min)

- [ ] Review budget vs actual for each category group
- [ ] Identify categories that were significantly over budget
- [ ] Identify categories that were significantly under budget
- [ ] Note any one-time or unusual expenses

**Prior month overspends roll silently into current month TBB.** Before reviewing the current month, check whether last month ended with any negative category balances — they reduce this month's Ready to Assign without any visible warning. Cover them retroactively using a surplus category (e.g., a month where Daycare only had one payment, Electricity didn't bill, etc.) to prevent invisible debt.

For detailed variance analysis, see `references/variance-analysis.md`.

### 4. Review Income (5 min)

- [ ] Verify all expected paychecks arrived and are in "Inflow: Ready to Assign"
- [ ] Record any side income or reimbursements
- [ ] Calculate total income for the month

### 5. Calculate Key Numbers (5 min)

- [ ] Net savings for the month (income minus spending)
- [ ] Savings rate percentage
- [ ] Update net worth tracking (if maintained separately from YNAB)

For a full income/expense summary, see `references/income-statement.md`.

### 6. Prepare Next Month (10 min)

- [ ] Cover any remaining category overspends from prior month
- [ ] Budget fixed obligations first (mortgage, loans, insurance, subscriptions)
- [ ] Fund known upcoming expenses for the next two weeks
- [ ] Assign personal spending budgets and groceries
- [ ] Hold remaining TBB for mid-month paychecks rather than over-allocating early

**Predicting upcoming charges:**
Do NOT rely on YNAB's scheduled transactions list — it only captures manually-entered recurring items; auto-imported charges (subscriptions, utilities, insurance) won't appear there. Instead, pull the prior month's transactions for the equivalent date window (e.g., to predict May 4-18 charges, query April 4-18) and identify what hit. This gives accurate payee names, amounts, and timing.

**Subscription due-date tip:** YNAB returns `goal_day` on categories with monthly goals — this is the expected charge date for that category. Use it to prioritize funding order.

- [ ] Adjust category goals if consistent over/underspending

## Monthly Review Schedule

The review works best in the first week after month-end:

| Day | Activity |
|-----|----------|
| **Day 1-2** | Wait for all month-end transactions to post (credit cards, autopay) |
| **Day 3-4** | Reconcile all accounts, review spending |
| **Day 5** | Update budget for next month, set goals |

## What to Look For

### Spending Patterns

- **Creeping categories**: Spending gradually increasing without a clear reason
- **Seasonal bumps**: Expected increases (holiday shopping, summer activities) — plan for these next year
- **New recurring costs**: Subscriptions or memberships added this month
- **Impulse spending**: Lots of small unplanned purchases adding up

### Budget Accuracy

- **Consistently over budget (3+ months)**: The budget is too low. Increase it or find ways to cut.
- **Consistently under budget (3+ months)**: The budget is too high. Reallocate to savings or other goals.
- **Volatile categories**: Some variation is normal (groceries, gas). Set the budget to the average and accept small swings.

## Quarterly Deep Dive

Every three months, go deeper:

- [ ] Update net worth statement with current investment and property values
- [ ] Review insurance coverage (life, health, auto, home)
- [ ] Check progress on annual financial goals
- [ ] Review subscription list — cancel anything unused
- [ ] Compare year-to-date spending to annual plan
- [ ] Check credit reports (free at annualcreditreport.com)

## Year-End Review

Once a year, do a comprehensive review:

- [ ] Full year income vs spending summary
- [ ] Net worth change for the year
- [ ] Review and update financial goals
- [ ] Plan next year's budget based on this year's actuals
- [ ] Review tax withholding (are you getting a big refund or owing?)
- [ ] Review beneficiaries on accounts and insurance
- [ ] Update estate planning documents if needed
