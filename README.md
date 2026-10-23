# Nykaa Financial Analysis Pipeline

I built this project to analyse Nykaa (FSN E-Commerce Ventures Ltd) from FY20 to FY26. I take the raw Screener.in files, clean them in Excel Power Query, store them in MySQL, and do the analysis in Python with pandas and matplotlib.

## Why I built this

Most finance reporting I have seen depends on spreadsheets that people rebuild by hand every time. I wanted a flow I can repeat: clean the data once, store it in a database, and re-run the analysis when new numbers come in.

## How the pipeline works

```
Screener.in Excel export (wide format, many tabs)
   → Excel Power Query: remove junk rows and columns, unpivot the years, fix fiscal-year labels
   → CSV export: one file per statement
   → MySQL: five tables, each in Metric | Year | Value format (quarters also have Quarter)
   → Python (mysql-connector + pandas): pivot long to wide, join on Year, calculate ratios
   → matplotlib: multi-panel charts saved in the charts/ folder
```

The five MySQL tables are `incomestatement_annual`, `balancesheet_annual`, `cashflow_annual`, `quarters_annual` and `workingcapital_annual`.

I kept working capital (Debtors, Inventory, Working Capital) in its own table because Debtors and Inventory are already part of Other Assets in the balance sheet, and Working Capital is a derived number. Putting them together could double count. I also set a primary key on (Metric, Year) so that importing the same file twice gives an error instead of duplicate rows.

Indian financial years run April to March and are named by the year they end, so Mar-26 is FY26. All figures are in Rs crore and consolidated.

## Data quality checks

- Kept rupee values and ratios apart, so one column never mixes crores with percentages.
- Removed the "Total" rows after unpivoting, otherwise summing line items counts things twice.
- Changed Screener's quarter labels to fiscal year and quarter (Jun = Q1, Sep = Q2, Dec = Q3, Mar = Q4). Jun, Sep and Dec columns belong to the next fiscal year.
- Checked that total liabilities equal total assets in every year.
- Checked that operating + investing + financing cash flow equals net cash flow in every year (the biggest difference was 0.01).
- Compared my ROE, debtor days and inventory turnover with Screener's numbers. They matched, but Screener is also my source for the inputs, so this checks my calculation and not the source itself.
- Hand-calculated one year of every ratio. This caught a real mistake: my cost-basis inventory days came out near 30 instead of about 109, because I had used x100 instead of x365.
- Used DECIMAL(15,2) for money so there are no floating-point rounding problems.
- Ratios are calculated only in Python. I never write them back into MySQL.

## Ratios I calculated

- Profitability: net profit margin, operating margin, ROE
- Growth: YoY sales growth, YoY expense growth
- Cost structure: raw material, employee cost, selling and admin, interest and depreciation as % of sales
- Leverage and debt servicing: debt-to-equity, interest coverage
- Working capital: debtor days, inventory turnover, inventory days, operating cycle
- Cash flow: operating cash flow vs net profit, free cash flow, payable days, cash conversion cycle

## Key findings

- Sales grew from about 1,768 crore (FY20) to about 10,022 crore (FY26), and operating margin improved from 4.7% to 7.5%.
- The operating margin fell in FY22 (6.5% to 4.3%). Selling and admin went up from 15.9% to 23.5% of sales, and raw material cost went up from 62.8% to 66.0%. This was right after the IPO, so IPO-related spending could be the reason, but I have not confirmed it.
- ROE fell from 12.6% (FY21) to 3.1% (FY22) because the IPO money made equity about 2.7 times bigger while net profit dropped. It fell again to 1.4% in FY23 and then recovered to 13.9% in FY26, because net profit grew about ten times on a fairly stable equity base. FY20 ROE was about -5% because of a net loss.
- Debt-to-equity was about 1.28 in FY20, fell to 0.44 in FY22, went up to 1.01 in FY25 and came down to 0.86 in FY26. Screener's borrowings include lease liabilities. For FY26, borrowings of about Rs 747 cr plus leases of about Rs 491 cr give the 0.86. Without leases it would be about 0.52.
- Interest coverage improved from 1.8x (FY20) to 6.4x (FY26), because operating profit grew faster than interest cost.

## Charts

- Sales vs expenses, operating margin, expense contribution to sales (stacked), sales trend
- ROE, debt-to-equity, interest coverage, operating profit vs interest
- Working capital: inventory days and debtor days (stacked) with the operating cycle line

The images are in the `charts/` folder.

# Working Capital Analysis (FY20 to FY26)

Metrics I calculated (I used year-end balances for all of them, like Screener does; FY20 has no opening balance):

- Debtor Days = Debtors / Sales x 365
- Inventory Turnover = Sales / Inventory
- Inventory Days (Sales basis) = Inventory / Sales x 365
- Inventory Days (Cost basis) = Inventory / Net Material Cost x 365
- Operating Cycle (Sales basis) = Debtor Days + Inventory Days (Sales basis)

*Net Material Cost = Raw Material Cost - Change in Inventory. It is only a proxy for COGS, not a reported COGS figure.*

Chart: `charts/working_capital_chart.png`

### Findings

- The operating cycle came down from 112 days to 70 days between FY20 and FY26. Around three quarters of this came from inventory days (92 to 60), and the rest from debtor days (20.3 to 10.5).
- Debtor days are low in every year (about 9 to 14 days after FY20). Collections did not get slower even though sales grew about 5.7 times. My guess is that most of Nykaa's online sales are prepaid or cash on delivery, but this is only a guesstimate.
- FY22 is the one year that went the other way. The operating cycle rose from 85.9 to 93.8 days. The whole increase came from inventory (74.5 to 84.7 days), because inventory went from Rs 498 cr to Rs 876 cr while sales grew about 55%. Debtor days actually fell that year. I think the company may have stocked up ahead of growth around the IPO period, but I have not confirmed this, so it stays a hypothesis.
- Inventory days on the cost basis are higher than on the Sales basis in every year (FY26: 108.9 vs 59.8), because Net Material Cost is only about 55% of Sales, so the denominator is smaller.

# Cash Flow and Earnings Quality (FY20 to FY26)

## Operating cash flow vs net profit

My first prediction was that operating cash flow (OCF) would be higher than net profit. It turned out to be higher in only 4 of the 7 years.

| FY | OCF (Rs cr) | Net profit (Rs cr) | OCF / Net profit | What I take from it |
|---|---|---|---|---|
| FY20 | 6.15 | -16.61 | -0.37x | Ratio means nothing (loss year), so I compare the rupees instead |
| FY21 | 133.18 | 61.55 | 2.16x | Can be used |
| FY22 | -353.96 | 41.08 | -8.62x | Only the sign matters: profit was positive but cash was negative |
| FY23 | -140.24 | 19.26 | -7.28x | Only the sign matters |
| FY24 | 0.25 | 32.27 | 0.01x | Profit gave almost no operating cash |
| FY25 | 466.63 | 66.08 | 7.06x | Only the direction, because the small profit makes the ratio look huge |
| FY26 | 644.30 | 199.44 | 3.23x | The most believable size, but it still needs an explanation |

This ratio breaks when profit is negative or very small, so in those years I look at the sign or the rupee amounts and not the size of the ratio.

## Free cash flow

Free cash flow = operating cash flow - capex. For capex I used the line "Fixed assets purchased" from Screener's expanded Cash from Investing section. I did not use the whole investing total. In FY22 the investing total was -603 but fixed assets purchased were only -94, because most of the rest went into other investments and subsidiaries. Capex is in whole rupees, so my free cash flow is approximate. I typed these values into the code by hand and noted the source.

| FY | FCF (Rs cr, approx.) |
|---|---|
| FY20 | -40 |
| FY21 | 91 |
| FY22 | -448 |
| FY23 | -348 |
| FY24 | -111 |
| FY25 | 340 |
| FY26 | 490 |

Free cash flow was negative from FY22 to FY24. I read this as a fast-growing company building up inventory and capacity with IPO money, not as a business in trouble.

## Payables and the cash conversion cycle

Screener has no trade payables line (it is hidden inside Other Liabilities, along with advances, provisions and lease liabilities), so I could not use it directly. I took consolidated trade payables by hand from the company's results filings, and from the October 2021 Red Herring Prospectus for FY20 and FY21. Each total is the sum of two reported lines (micro and small enterprises, and other creditors). Inventory and receivables in those filings matched my Screener data. The values are in a small DataFrame in my code, with the source written next to each year.

- Payable Days = Trade Payables / Net Material Cost x 365
- Cash Conversion Cycle = Inventory Days (Cost basis) + Debtor Days - Payable Days

| FY | Trade payables (Rs cr) | Payable days | Cash conversion cycle (days) |
|---|---|---|---|
| FY20 | 313.27 | 112.7 | 67.9 |
| FY21 | 316.21 | 77.3 | 55.9 |
| FY22 | 362.05 | 62.0 | 97.1 |
| FY23 | 265.39 | 33.8 | 105.8 |
| FY24 | 386.69 | 38.7 | 94.4 |
| FY25 | 634.83 | 51.8 | 75.2 |
| FY26 | 732.50 | 48.6 | 70.8 |

- From FY20 to FY26, inventory days got about 51 days better and debtor days about 10 days better. But payable days fell by about 64 days, so the cash conversion cycle ended almost where it started (about 68 to about 71 days). It was highest in FY23 at about 106 days.
- I do not know why payable days fell. That is still a hypothesis.
- Payables also include suppliers other than stock suppliers (marketing, for example), while my base is only net material cost, so these days are approximate. This cycle is also a different measure from the sales-basis operating cycle above.

## Why OCF is different from net profit

Gap = OCF - net profit. I split the gap into working capital changes (estimated from year-end balance sheet differences), depreciation (a cost that uses no cash), and whatever is left unexplained. When an asset like inventory or debtors goes up, it uses cash. When a liability like payables goes up, it releases cash.

| FY | Gap | Inventory, debtors and payables | Depreciation | Unexplained |
|---|---|---|---|---|
| FY21 | 71.63 | -28.02 | 71.59 | 28.06 |
| FY22 | -395.04 | -349.58 | 96.41 | -141.87 |
| FY23 | -159.50 | -295.18 | 173.26 | -37.58 |
| FY24 | -32.02 | -143.68 | 224.23 | -112.57 |
| FY25 | 400.55 | 17.64 | 266.40 | 116.51 |
| FY26 | 444.86 | -169.72 | 320.33 | 294.25 |

- OCF was lower than profit in FY22, FY23 and FY24, and negative in FY22 and FY23. The inventory build is the main thing I could measure (FY22 inventory went up by about Rs 378 cr), but it only explains part of the gap, and it is an estimate.
- In FY23, payables also fell by about Rs 97 cr, so Nykaa paid its suppliers down and that used more cash.
- In FY25, payables went up by about Rs 248 cr. That explains about two thirds of what was unexplained before, and about Rs 117 cr is left. In FY26 about Rs 294 cr is still unexplained.
- Things I have **not** tested, so they are only hypotheses: employee stock option expense (a non-cash cost), other current assets and liabilities, tax paid, and whether interest paid is shown under financing instead of operating activities.
- My working capital figures come from balance sheet differences, not from the cash flow statement's own lines, so the whole bridge is an estimate.

## Status and next steps

Done: the data pipeline (five tables), P&L, balance sheet and quarterly tables, ratio analysis, working capital, cash flow and earnings quality, free cash flow, payables and cash conversion cycle, and the charts.

In progress: a simple forecast and DCF valuation with a sensitivity table. The DCF only reflects my own assumptions, so I treat the result as a range to question and not as a price target.

Next: quarterly analysis (seasonality and growth), common-size statements, a DuPont breakdown of ROE, a peer comparison, and maybe AI-written commentary based on the ratio tables.

## Data source

Financial statements from Screener.in (public company data). Consolidated trade payables come from FSN E-Commerce Ventures' published results filings and its October 2021 Red Herring Prospectus. This analysis is for learning and my portfolio, and it is not investment advice.

## Tech stack

Excel Power Query, MySQL, Python (pandas, matplotlib, mysql-connector-python)