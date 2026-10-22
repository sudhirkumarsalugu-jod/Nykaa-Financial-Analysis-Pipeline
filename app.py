# pyright: reportMissingModuleSource=false, reportMissingImports=false
import pandas as pd
import mysql.connector as mysql
import matplotlib.pyplot as plt
import os

os.makedirs("charts", exist_ok=True)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

#-----Sql Connection ---------

conn = mysql.connect(
    host = "localhost",
    user= "root",
    password = "Encrypted@405",
    database = "nykaa_analysis")

if conn :
    print("Connected Sucessfully ")
else:
    print("Not Connected ")

cursor = conn.cursor()
#----Data Injection-----
df_pnl = pd.read_sql("select * from incomestatement_annual",con= conn)
df_pnl_detailed = pd.read_sql("select * from incomestatement_detailed",con= conn)
df_balancesheet = pd.read_sql("select * from balancesheet_annual",con= conn)
df_cashflow = pd.read_sql("select * from cashflow_annual",con= conn)
df_quarters = pd.read_sql("select * from quarters_annual",con= conn)
df_workincapital = pd.read_sql("select * from Working_capital_annual",con=conn)

#-----Changing Data Structure------
df_pnl_wide = df_pnl.pivot(index="Year",columns="Metric",values="Value")
df_pnl_detailed_wide = df_pnl_detailed.pivot(index="Year",columns="Metric",values="Value")
df_balancesheet_wide = df_balancesheet.pivot(index="Year",columns="Metric",values="Value")
df_workincapital_wide = df_workincapital.pivot(index="Year",columns="Metric",values="Value")
df_cashflow_wide = df_cashflow.pivot(index="Year",columns="Metric",values = "Value")

#--creating required ratios of pnl statement ----
df_pnl_wide['Net Profit Margin']= df_pnl_wide['Net profit']/df_pnl_wide['Sales']*100
df_pnl_wide['Net Operating Margin']= df_pnl_wide['Operating Profit']/df_pnl_wide['Sales']*100
df_pnl_wide['Sales (prev year)'] = df_pnl_wide['Sales'].shift(1)
df_pnl_wide['YoY Growth %'] = (df_pnl_wide['Sales']-df_pnl_wide['Sales (prev year)'])/df_pnl_wide['Sales (prev year)']*100
df_pnl_wide['Expense (prev year)'] = df_pnl_wide['Expenses'].shift(1)
df_pnl_wide['YoY Expense %'] = (df_pnl_wide['Expenses']-df_pnl_wide['Expense (prev year)'])/df_pnl_wide['Expense (prev year)']*100
df_pnl_wide["Interest % of sales"] = df_pnl_wide['Interest']/df_pnl_wide['Sales']*100
df_pnl_wide["Depriciation % of sales"] = df_pnl_wide['Depreciation']/df_pnl_wide['Sales']*100

#------------more ratios------------
df_pnl_detailed_wide['Raw Material % of sales'] = df_pnl_detailed_wide['Raw Material Cost']/df_pnl_detailed_wide['Sales']*100
df_pnl_detailed_wide['Power and Fuel % of sales'] = df_pnl_detailed_wide['Power and Fuel']/df_pnl_detailed_wide['Sales']*100
df_pnl_detailed_wide['Employee Cost % of Sales'] = df_pnl_detailed_wide['Employee Cost']/df_pnl_detailed_wide['Sales']*100
df_pnl_detailed_wide['Selling and admin % of sales'] = df_pnl_detailed_wide['Selling and admin']/df_pnl_detailed_wide['Sales']*100
df_pnl_detailed_wide['Other Expenses% of sales'] = df_pnl_detailed_wide['Other Expenses']/df_pnl_detailed_wide['Sales']*100

#===================================
#               CHARTS               
#=================================== 

fig1, axes = plt.subplots(2, 2, figsize=(14, 10))

# Chart 1: Sales vs Expenses
df_pnl_wide['Sales'].plot(ax=axes[0][0])
df_pnl_wide['Expenses'].plot(ax=axes[0][0])
axes[0][0].legend()
for year, Expense_value in zip(df_pnl_wide.index, df_pnl_wide['Expenses']):
    axes[0][0].text(year, Expense_value -500, str(round(Expense_value, 1)))
for year, sales_value in zip(df_pnl_wide.index, df_pnl_wide['Sales']):
    axes[0][0].text(year, sales_value + 800, str(round(sales_value, 1)))
axes[0][0].set_title("Sales vs Expense By Year")
axes[0][0].set_yticks([])
axes[0][0].set_ylabel("Values (in crores)")
axes[0][0].set_xlabel("Years")
axes[0][0].set_ylim(top=axes[0][0].get_ylim()[1] * 1.20)


# Chart 2: Operating Margin %
# Chart 2: Operating Margin %
df_pnl_wide['Net Operating Margin'].plot(ax=axes[0][1])
axes[0][1].set_title("Operating Margin %")

for year, operating_margin in zip(df_pnl_wide.index, df_pnl_wide['Net Operating Margin']):
    axes[0][1].text(year, operating_margin + 0.3, str(round(operating_margin, 1)))

axes[0][1].set_ylabel("Values in %")
axes[0][1].set_yticks([])
axes[0][1].set_ylim(top=axes[0][1].get_ylim()[1] * 1.20)

# Chart 3: Stacked bar + Sales line
df_pnl_detailed_wide["Net Material Cost"] = df_pnl_detailed_wide["Raw Material Cost"] - df_pnl_detailed_wide["Change in Inventory"]

expense_columns = [
    "Net Material Cost", "Other Mfr. Exp", "Power and Fuel",
    "Employee Cost", "Selling and admin", "Other Expenses",
]
running_total = 0

for c in expense_columns:
    axes[1][0].bar(df_pnl_detailed_wide.index, df_pnl_detailed_wide[c], bottom=running_total, label=c)
    running_total = running_total + df_pnl_detailed_wide[c]

for year, total_value in zip(df_pnl_detailed_wide.index, running_total):
    axes[1][0].text(year, total_value - 150, str(round(total_value, 0)), color="black", ha="center")


df_pnl_wide['Sales'].plot(ax=axes[1][0])
axes[1][0].set_ylabel("Rs crore")
axes[1][0].set_title("Sales vs. Expense Composition")
axes[1][0].legend()

# Chart 4:Sales
axes[1][1].set_title("Sales Trend")
df_pnl_detailed_wide['Sales'].plot(ax=axes[1][1])
for year, sales_value in zip(df_pnl_wide.index, df_pnl_wide['Sales']):
    axes[1][0].text(year, total_value - 150, str(round(total_value, 0)), color="white", ha="center", fontsize=9, fontweight="bold")

axes[1][1].set_yticks([])
axes[1][1].set_ylim(top=axes[1][1].get_ylim()[1] * 1.10)
axes[1][1].set_ylabel("Values in Crores")

fig1.tight_layout()
fig1.savefig("charts/pnl_ratio_chart.png", dpi=200, bbox_inches="tight")

#-----------------------------------------------------------------------------------------#
#                       BALANCE SHEET                           
#-----------------------------------------------------------------------------------------

df_combined_bs = pd.merge(df_pnl_wide, df_balancesheet_wide, left_index=True, right_index=True)

#=============================================
#               Balancesheet Ratio 
#=============================================

df_combined_bs['ROE%'] = df_combined_bs['Net profit']/(df_combined_bs['Equity Share Capital']+df_combined_bs['Reserves'])*100

df_combined_bs['Debt to Equity'] = df_combined_bs['Borrowings'] / (df_combined_bs['Equity Share Capital']+df_combined_bs['Reserves'])

df_pnl_wide['Interest Coverage'] = df_pnl_wide['Operating Profit'] / df_pnl_wide['Interest']


#=================================================
#            Balancesheet Charts
#=================================================

fig2, axes = plt.subplots(2, 2, figsize=(14, 10))

# Chart 1: ROE trend
df_combined_bs['ROE%'].plot(ax=axes[0][0])
axes[0][0].set_title("ROE % Trend")
axes[0][0].set_ylabel("ROE (%)")
axes[0][0].set_xlabel("Year")
axes[0][0].axhline(0, color="red", linestyle="--")

# Chart 2: Debt to Equity
df_combined_bs['Debt to Equity'].plot(ax=axes[0][1])
axes[0][1].set_title("Debt to Equity Ratio Trend")
axes[0][1].set_ylabel("Debt / Equity (x)")
axes[0][1].set_xlabel("Year")
axes[0][1].axhline(1.0, color="red", linestyle="--")

# Chart 3: Interest Coverage
df_pnl_wide['Interest Coverage'].plot(ax=axes[1][0])
axes[1][0].set_title("Interest Coverage")
axes[1][0].set_ylabel("Times covered (x)")
axes[1][0].set_xlabel("Year")
axes[1][0].set_ylim(bottom=0)
axes[1][0].axhline(1.0, color="red", linestyle="--")

# Chart 4: Operating Profit vs Interest
df_pnl_wide['Operating Profit'].plot(ax=axes[1][1])
df_pnl_wide['Interest'].plot(ax=axes[1][1])
axes[1][1].set_ylabel("Rs crore")
axes[1][1].set_xlabel("Year")
axes[1][1].set_title("Operating Profit vs Interest")
axes[1][1].legend()

fig2.tight_layout()
fig2.savefig("charts/balancesheet_ratio_chart.png", dpi=200, bbox_inches="tight")


#-----------Working Capital Ratios--------------

df_workincapital_wide['Debtor Days'] = (df_workincapital_wide['Debtors']/df_pnl_detailed_wide['Sales'])*365
df_workincapital_wide['Inventory turn-over']= df_pnl_wide['Sales']/df_workincapital_wide['Inventory']
df_workincapital_wide['Inventory Days (sales basis)'] = 365/df_workincapital_wide['Inventory turn-over']
df_workincapital_wide['Inventory Days (cost basis)'] = df_workincapital_wide['Inventory']/df_pnl_detailed_wide['Net Material Cost']*365
df_workincapital_wide['Operating Cycle (sales basis)'] = df_workincapital_wide['Debtor Days']+df_workincapital_wide['Inventory Days (sales basis)']
df_workincapital_wide['Change in Inventory'] = df_workincapital_wide['Inventory']-df_workincapital_wide['Inventory'].shift(1)
df_workincapital_wide['Change in Debtors'] = df_workincapital_wide['Debtors']-df_workincapital_wide['Debtors'].shift(1)
df_workincapital_wide['Cash effect of Inventory'] = df_workincapital_wide['Change in Inventory']*-1
df_workincapital_wide['Cash effect of Debtors'] = df_workincapital_wide['Change in Debtors']*-1
df_workincapital_wide['WC cash effect'] = df_workincapital_wide['Cash effect of Debtors']+df_workincapital_wide['Cash effect of Inventory']


#print(df_workincapital_wide[['Debtor Days','Inventory Days (sales basis)','Operating Cycle (sales basis)']].round(1))

#================================================
#             Working capital Charts 
#================================================

fig3, axes = plt.subplots(figsize=(10,6))
wc_running_total = 0
days_column = ['Inventory Days (sales basis)','Debtor Days']

for d in days_column:
    axes.bar(df_workincapital_wide.index,df_workincapital_wide[d],bottom= wc_running_total, label = d)
    wc_running_total = wc_running_total+df_workincapital_wide[d]

for year, days  in zip(df_workincapital_wide.index, wc_running_total):
    axes.text(year, days +2 ,f"{days:.1f}", ha="center")

axes.plot(df_workincapital_wide.index, df_workincapital_wide['Operating Cycle (sales basis)'], marker="o", color="black", label="Operating Cycle")
axes.set_ylabel("Days")
axes.set_xlabel("Year")
axes.set_xticks(df_workincapital_wide.index) and axes.set_xticklabels([f"FY{str(y)[-2:]}" for y in df_workincapital_wide.index])
axes.legend()
axes.set_title("Operating Cycle: Inventory Days + Debtor Days (Sales basis)")

fig3.tight_layout()
fig3.savefig("charts/working_capital_chart.png", dpi=200, bbox_inches="tight")
#plt.show()


#---------------Cash Flow Ratios------------
df_combined_2 = pd.merge(df_pnl_wide,df_cashflow_wide,left_index= True , right_index= True) #merging both tables


df_combined_2['cash conversion ratio'] = df_combined_2['Cash from Operating Activity']/df_combined_2['Net profit']

#print(df_combined_2[['Net profit','Cash from Operating Activity','cash conversion ratio']].round(2))

#print(df_cashflow_wide.round(2))

#print(df_workincapital_wide[['Debtors','Change in Debtors','Inventory', 'Change in Inventory','Cash effect of Inventory','Cash effect of Debtors','WC cash effect']])

#print(df_pnl_wide['Depreciation'])



#creating a conparison table 

df_comparison = df_workincapital_wide[["WC cash effect"]].join(df_pnl_wide[["Depreciation", "Net profit"]]).join(df_cashflow_wide[["Cash from Operating Activity"]])

df_comparison['Gap'] = df_comparison['Cash from Operating Activity']-df_comparison['Net profit']
df_comparison['Unexplained'] = df_comparison['Gap']-df_comparison['WC cash effect']-df_comparison['Depreciation']

#creting trade payble from sources 

data = {'Year':[2020,2021,2022,2023,2024,2025,2026],
    'Trade Payables':[313.27,316.21,362.05,265.39,386.69,634.83,732.50],
    'source filing':['FY20 results(RHP) consolidated ','RHP and the FY22 results','FY22 and FY23 results.','FY23 results(Nykaa)','FY25 results (comparative column)','FY25 results(Nykaa)','FY26 Results(NSE)']}


Trade_Payables = pd.DataFrame(data)
Trade_Payables = Trade_Payables.set_index("Year")

#joining trade payables to pnl(wide)

df_combined_3 = pd.merge(df_pnl_detailed_wide['Net Material Cost'],Trade_Payables,left_index=True,right_index=True)

df_cash_conversion = pd.merge(df_combined_3['Trade Payables'],df_workincapital_wide[['Debtor Days','Inventory Days (cost basis)']],left_index=True,right_index=True)

df_cash_conversion['Payable Days'] = Trade_Payables['Trade Payables']/df_combined_3['Net Material Cost']*365
df_cash_conversion['Cash conversion cycle (days)'] = df_cash_conversion['Inventory Days (cost basis)']+df_cash_conversion['Debtor Days']-df_cash_conversion['Payable Days']

df_comparison['Trade Payables'] = Trade_Payables['Trade Payables']
df_comparison['Cash effect of Payables'] = df_comparison['Trade Payables']-df_comparison['Trade Payables'].shift(1)
df_comparison['WC Total(Inc Payables)'] = df_workincapital_wide['WC cash effect'] + df_comparison['Cash effect of Payables']
df_comparison['Unexplained(New)'] = df_comparison['Gap']-df_comparison['WC Total(Inc Payables)']-df_comparison['Depreciation']
print(df_comparison)
