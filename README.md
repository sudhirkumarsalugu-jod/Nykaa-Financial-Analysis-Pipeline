# Nykaa Financial Analysis Pipeline

An end-to-end financial data pipeline and ratio analysis of Nykaa (FSN E-Commerce Ventures Ltd), covering FY20 to FY26. Raw Screener.in exports are cleaned in Excel Power Query, stored in a structured MySQL database, and analysed in Python (pandas, matplotlib).

## Why this project

Financial reporting often depends on spreadsheets that are rebuilt by hand every cycle. This project builds a repeatable flow instead: clean the data once, store it in a database, and re-run the analysis when new figures arrive.

## Pipeline

```
Screener.in export (wide format, multiple tabs)
        |
Excel Power Query: remove junk rows/columns, unpivot years, fix fiscal-year labels
        |
CSV export (one file per statement)
        |
MySQL: one table per statement (Metric | Year | Value)
        |
Python (mysql-connector + pandas): pivot, join, calculate ratios
        |
matplotlib: multi-panel charts
```

## Data quality steps

- Separated raw rupee figures from ratios, so one column never mixes crores with percentages.
- Removed "Total" rows after unpivoting to avoid double counting when summing line items.
- Converted Screener's quarter-end labels to fiscal year and quarter (Jun = Q1, Sep = Q2, Dec = Q3, Mar = Q4; Jun/Sep/Dec columns belong to the next fiscal year).
- Reconciled Balance Sheet totals (Total liabilities = Total assets for every year).
- Cross-checked calculated ROE against Screener's published ROE for every year.
- Hand-verified one year of every calculated ratio against the raw inputs.
- Used DECIMAL(15,2) for money values to avoid floating-point rounding.

## Database tables

| Table | Contents |
|---|---|
| incomestatement_annual | P&L line items by year |
| balancesheet_annual | Balance Sheet line items by year |
| cashflow_annual | Cash flow line items by year |
| quarters_annual | Quarterly P&L with fiscal year and quarter |

## Ratios calculated

- Profitability: net profit margin, operating margin, ROE
- Growth: YoY sales growth, YoY expense growth
- Cost structure: raw material, employee cost, selling and admin, interest and depreciation as % of sales
- Leverage and debt servicing: debt-to-equity, interest coverage

## Key findings

1. **Sales grew from about 1,768 crore (FY20) to about 10,022 crore (FY26)**, with operating margin improving from 4.7% to 7.5%.
2. **The FY22 operating margin dip (6.5% to 4.3%)** came from two cost lines: selling and admin rose from 15.9% to 23.5% of sales, and raw material cost rose from 62.8% to 66.0%. This coincides with the post-IPO period; the link to IPO-related spending is a likely explanation, not a confirmed one.
3. **ROE fell from 12.6% (FY21) to 3.1% (FY22)** because IPO proceeds expanded equity about 2.7 times while net profit declined. It fell to 1.4% in FY23 on lower profit, then recovered to 13.9% in FY26 on net profit growing about ten times against a stable equity base.
4. **Debt-to-equity** reached a low of 0.44 in FY22, rose to 1.01 in FY25 and eased to 0.86 in FY26.
5. **Interest coverage improved from 1.8x (FY20) to 6.4x (FY26)**, because operating profit grew faster than interest cost, so the added borrowing remained affordable.

## Charts

- Sales vs expenses, operating margin, expense contribution to sales (stacked), sales trend
- ROE, debt-to-equity, interest coverage, operating profit vs interest

(Chart images are in the `charts/` folder.)

## Tech stack

Excel Power Query, MySQL, Python (pandas, matplotlib, mysql-connector-python)



## Status and next steps

Completed: data pipeline, P&L, Balance Sheet and quarterly tables, ratio analysis, visualisation.

Planned: cash flow analysis (operating cash flow against net profit), debtor and inventory days, forecasting, DCF valuation, and a peer comparison.

## Data source

Financial statements from Screener.in (public company data). Analysis is for learning and portfolio purposes and is not investment advice.

