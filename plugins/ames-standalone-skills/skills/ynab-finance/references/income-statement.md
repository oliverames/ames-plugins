# Income & Expense Summary

Generate a monthly income and expense summary with period-over-period comparison. Shows where money came in and where it went, with net savings rate.

## Workflow

### 1. Gather Data from YNAB

Use `get_transactions` and budget tools to pull:
- All transactions for the specified month
- Same data for the prior month (for comparison)
- Budget category balances for the month
- Account balances (checking, savings, credit cards)

### 2. Generate Income Summary

```
INCOME & EXPENSE SUMMARY
Month: [Month]

INCOME
                              This Month    Last Month    Change     Change %
                              ----------    ----------    ------     --------
  Take-home pay               $X,XXX        $X,XXX        $XXX       X.X%
  Side income                  $X,XXX        $X,XXX        $XXX       X.X%
  Interest / dividends         $X,XXX        $X,XXX        $XXX       X.X%
  Other income                 $X,XXX        $X,XXX        $XXX       X.X%
                              ----------    ----------
TOTAL INCOME                   $X,XXX        $X,XXX        $XXX       X.X%
```

### 3. Generate Expense Summary

Group expenses by YNAB category groups:

```
EXPENSES (by category group)
                              This Month    Last Month    Budget     Over/Under
                              ----------    ----------    ------     ----------
  Housing                      $X,XXX        $X,XXX        $X,XXX     $XXX
  Transportation               $X,XXX        $X,XXX        $X,XXX     $XXX
  Groceries & dining           $X,XXX        $X,XXX        $X,XXX     $XXX
  Utilities                    $X,XXX        $X,XXX        $X,XXX     $XXX
  Subscriptions                $X,XXX        $X,XXX        $X,XXX     $XXX
  Kids                         $X,XXX        $X,XXX        $X,XXX     $XXX
  Health                       $X,XXX        $X,XXX        $X,XXX     $XXX
  Fun money                    $X,XXX        $X,XXX        $X,XXX     $XXX
  Other                        $X,XXX        $X,XXX        $X,XXX     $XXX
                              ----------    ----------    ------
TOTAL EXPENSES                 $X,XXX        $X,XXX        $X,XXX     $XXX
```

### 4. Bottom Line

```
NET SAVINGS                    $X,XXX        $X,XXX        $XXX       X.X%
Savings Rate                   XX.X%         XX.X%
```

### 5. Highlights

Call out:
- Categories where spending was significantly over or under budget
- Any unusual or one-time expenses
- Month-over-month trends worth noting
- Savings rate trend

### 6. Output

Provide:
1. Formatted income and expense summary with comparisons
2. Net savings and savings rate
3. Top 3-5 notable variances from budget
4. Suggested follow-up: offer to drill into any category for variance analysis
