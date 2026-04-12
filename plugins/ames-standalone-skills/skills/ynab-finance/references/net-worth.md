# Net Worth & Cash Flow

Simplified household financial summaries for tracking net worth, cash flow, and overall financial health.

## Net Worth Statement

Your net worth is the single most important number in personal finance: what you own minus what you owe.

### Format

```
NET WORTH STATEMENT
As of: [Date]

ASSETS
  Liquid
    Checking accounts                 $XX,XXX
    Savings accounts                  $XX,XXX
    Money market / CDs                $XX,XXX
  Investments
    Brokerage accounts                $XX,XXX
    Retirement (401k, IRA, Roth)      $XX,XXX
    HSA                               $XX,XXX
    529 / education savings           $XX,XXX
  Property
    Home (estimated value)            $XXX,XXX
    Vehicles (estimated value)        $XX,XXX
    Other property                    $XX,XXX
                                      --------
TOTAL ASSETS                          $XXX,XXX

LIABILITIES
  Short-term
    Credit card balances              $XX,XXX
    Other short-term debt             $XX,XXX
  Long-term
    Mortgage balance                  $XXX,XXX
    Auto loans                        $XX,XXX
    Student loans                     $XX,XXX
    Other loans                       $XX,XXX
                                      --------
TOTAL LIABILITIES                     $XXX,XXX

NET WORTH                             $XXX,XXX
  Change from last month:             +$X,XXX
  Change from last year:              +$XX,XXX
```

### Data Sources

- **YNAB accounts**: Checking, savings, credit cards (use `list_accounts`)
- **Investment accounts**: User provides or pulls from brokerage statements
- **Property values**: User provides estimates (Zillow, recent appraisal)
- **Loan balances**: User provides from loan servicer statements

### Tracking Over Time

Track net worth monthly to see the trend. Components to watch:
- **Liquid net worth**: Assets minus liabilities, excluding home equity and retirement. This is your financial flexibility.
- **Debt payoff progress**: Are loan balances decreasing on schedule?
- **Investment growth**: Contributions plus market gains/losses
- **Home equity**: Property value minus mortgage balance

## Monthly Cash Flow Summary

Where the money came from and where it went.

### Format

```
MONTHLY CASH FLOW
Month: [Month]

INFLOWS
  Paychecks (take-home)               $X,XXX
  Side income                         $X,XXX
  Interest / dividends                $X,XXX
  Reimbursements                      $X,XXX
  Other                               $X,XXX
                                      ------
TOTAL INFLOWS                         $X,XXX

OUTFLOWS
  Fixed expenses
    Housing (mortgage/rent)            $X,XXX
    Insurance                          $X,XXX
    Car payments                       $X,XXX
    Subscriptions                      $X,XXX
    Childcare / tuition                $X,XXX

  Variable expenses
    Groceries                          $X,XXX
    Dining out                         $X,XXX
    Gas / transportation               $X,XXX
    Utilities                          $X,XXX
    Shopping                           $X,XXX
    Entertainment                      $X,XXX
    Health / medical                   $X,XXX
    Kids activities                    $X,XXX
    Other                              $X,XXX

  Savings & debt payoff
    Retirement contributions           $X,XXX
    Extra debt payments                $X,XXX
    Emergency fund                     $X,XXX
    Other savings goals                $X,XXX
                                      ------
TOTAL OUTFLOWS                        $X,XXX

NET CASH FLOW                         $X,XXX
```
