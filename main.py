import pandas as pd
import numpy as np
import datetime

#get client ID
acc = 105

#open data, prepare dataframes
expensesDF = pd.read_csv("Data/expenses.csv")
clientDF = pd.read_csv("Data/clients.csv")
accountsDF = pd.read_csv("Data/accounts.csv")
incomeDF = pd.read_csv("Data/income.csv")
pensionDF = pd.read_csv("Data/pension.csv")

#filter all DF's for acc
expensesDF = expensesDF.loc[expensesDF["Client ID"] == acc]
clientDF = clientDF.loc[clientDF["Client ID"] == acc]
accountsDF = accountsDF.loc[accountsDF["Client ID"] == acc]
incomeDF = incomeDF.loc[incomeDF["Client ID"] == acc]
pensionDF = pensionDF.loc[pensionDF["Client ID"] == acc]

#set globbal default retirement age, date, etc
retirement = 65
yearsinretirement = 25
now = datetime.datetime.now()
retirementdate = int(clientDF["DOB"]) + retirement
years_to_ret = retirementdate - now.year

#calculation to return yearly balances of account, with interest and rips
def simplecompyearly(balance, percent, rip, yrs):
    rate = 1 + (percent/100)
    x = 1
    yearly = [balance]
    while x < yrs+1:
        comprate = rate ** x
        endbal = balance*comprate
        endbal = endbal + (rip*12)
        yearly.append(endbal)
        x += 1
    return yearly

#calculate the yearly income totals, including the rate of increase up to retirement
def income_yearly_balance():
    x2 = np.asarray(incomeDF)
    c = 0
    df = pd.DataFrame()
    while c < (np.size(x2, 0)):
        data = np.array(simplecompyearly(
            x2[c, 2]*12, x2[c, 3], 0, years_to_ret))
        i = 0
        dffinal = pd.DataFrame()
        while i < (np.size(data, 0)):
            dffinal[i] = [now.year + i, data[i]]
            i += 1
        dffinal = dffinal.transpose()
        dffinal.columns = ["year", x2[c, 1]]
        df[x2[c, 1]] = dffinal[x2[c, 1]]
        c += 1
    years = []
    df['Total Income'] = df.sum(axis=1)
    i = 0
    while i < len(df.index):
        years.append(now.year + i)
        i += 1
    df.insert(0, "Year", years, True)
    return (df)

#calculate and return the expenses per year up to retirement
def expensesyearly():
    df = expensesDF
    df["Date Stop"] = df["Date Stop"].fillna("1/1/3000")
    df["Date Start"] = df["Date Start"].fillna("1/1/2000")
    df = np.asarray(df)
    data = pd.DataFrame()
    i = 0
    while i < (years_to_ret+1):
        exp = 0
        for x in df:
            StopDate = x[3]
            StopDate = int(StopDate[-4:])
            StartDate = x[4]
            StartDate = int(StartDate[-4:])
            if StopDate > (now.year+i) and StartDate < (now.year+i):
                exp += (x[2]*12)
            else:
                pass
        data[i] = [now.year+i, exp]
        i += 1
    data = data.transpose()
    data.columns = ["Year", "Expenses"]
    return (data)

#create one final dataframe to include all income and expenses up to retirement
def income_expenses():
    expenses = expensesyearly()
    income = income_yearly_balance()
    income["Total Expenses"] = expenses["Expenses"]
    income["Net Cashflow"] = income["Total Income"] - income["Total Expenses"]
    return(income)

#calculate min rrif payment via dictonary and return the payment, based on age and balance of rrif account
def rifpayments(balance, age):
    dict = {65:	4.00, 66: 4.17, 67:	4.35, 68: 4.55, 69:	4.76, 70:	5.00,    71:	5.28,    72:	5.40,    73: 5.53,    74:	5.67,    75:	5.82,
            76:	5.98,    77:	6.17,    78:	6.36,    79:	6.58,    80:	6.82,    81:	7.08,    82:	7.38,    83:	7.71,    84:	8.08,    85:	8.51,    86:	8.99,
            87:	9.55,    88:	10.21,    89:	10.99,    90:	11.92,    91:	13.06,    92:	14.49,    93:	16.34,    94:	18.79,    95:	20.00,    96:	20.00,    97:	20.00,
            98:	20.00,    99:	20.00,    100: 20.00}
    percent = (dict[age]/100)
    payment = balance*percent
    return (payment)

#calculate the yearly income in retirement from pensions, cpp, oas etc.
def retirementincome():
    x2 = np.asarray(pensionDF)
    c = 0
    df = pd.DataFrame()
    while c < (np.size(x2, 0)):
        data = np.array(simplecompyearly(
            x2[c, 2]*12, x2[c, 3], 0, yearsinretirement))
        i = 0
        dffinal = pd.DataFrame()
        while i < (np.size(data, 0)):
            dffinal[i] = [retirementdate + i, data[i]]
            i += 1
        dffinal = dffinal.transpose()
        dffinal.columns = ["year", x2[c, 1]]
        df[x2[c, 1]] = dffinal[x2[c, 1]]
        c += 1
    years = []
    df['Total Income'] = df.sum(axis=1)
    i = 0
    while i < len(df.index):
        years.append(retirementdate + i)
        i += 1
    df.insert(0, "Year", years, True)
    return (df)

#calculate the ending balance of all RRSP accounts at the retirement date. this becomes the starting balance for RRIF accounts
def rrsptorif():
    df = accountsDF
    data = np.asarray(df)
    ending = []
    for x in data:
        endbalance = (simplecompyearly(x[2], x[4], x[5], yearsinretirement))
        endbalance = endbalance[-1]
        ending.append(endbalance)
    end = pd.DataFrame(ending)
    end.columns = ["Balance"]
    df["End Balance"] = end["Balance"].values
    return (df)

#calculate expenses in retirement
def retirementexpenses():
    df = expensesDF
    df["Date Stop"] = df["Date Stop"].fillna("1/1/3000")
    df["Date Start"] = df["Date Start"].fillna("1/1/2000")
    df = np.asarray(df)
    data = pd.DataFrame()
    i = 0
    while i < yearsinretirement+1:
        exp = 0
        for x in df:
            StopDate = x[3]
            StopDate = int(StopDate[-4:])
            StartDate = x[4]
            StartDate = int(StartDate[-4:])
            if StopDate > (retirementdate+i) and StartDate < (retirementdate+i):
                exp += (x[2]*12)
            else:
                pass
        data[i] = [retirementdate+i, exp]
        i += 1
    data = data.transpose()
    data.columns = ["Year", "Expenses"]
    return (data)

#calculate the balance of the RRIF accounts each year, taking into account RRIF payments, and growth
def withdrawlamt(starting, intrate, yrs):
    i = 1
    balance = starting
    yearly = [balance]
    income = [rifpayments(balance, 65)]
    total = pd.DataFrame()
    rate = 1 + ((intrate)/100)
    date = [retirementdate]
    while i < yrs+1:
        wdl = rifpayments(balance, 65+i)
        netchange = (balance*rate) - balance - wdl
        balance = balance + netchange
        date.append(retirementdate+i)
        yearly.append(balance)
        income.append(wdl)
        if balance < 0:
            break
        i += 1
    total["Date"] = date
    total["Balance"] = yearly
    total["Payment"] = income
    i = 0
    return total

#combine RRIF withdrawls over all RRIF accounts and retun a sum to add to income
def rifincome():
    df = rrsptorif()
    df = df.loc[df["TYPE"] == "RRSP"]
    x2 = np.asarray(df)
    i = 0
    RemainingBalance = pd.DataFrame()
    Payment = pd.DataFrame()
    for x in x2:
        data = withdrawlamt(x[7], x[4], yearsinretirement)
        RemainingBalance.insert(0, x[1], data["Balance"])
        Payment.insert(0, x[1], data["Payment"])
        i += 1
    Payment["Total Payment"] = Payment.sum(axis=1)
    return (RemainingBalance, Payment)

#include income, expenses, rif payments to determine if there is a shortfall to sell nonreg
def retirementcashflow():
    df2 = retirementexpenses()
    df = retirementincome()
    bal, payments = rifincome()
    df["Rif Payment"] = payments["Total Payment"]
    df["Expenses"] = df2["Expenses"]
    df["Net Cashflow"] = df["Total Income"] + df["Rif Payment"]- df ["Expenses"]
    return (df)

#if there is a cashflow shortfall, sell nonreg assets to cover
def sellnonreg():
    cashflow = retirementcashflow()
    accounts = rrsptorif()
    accounts = accounts.loc[accounts["TYPE"] != "RRSP"]
    totalbalance = accounts["End Balance"].sum()
    accounts["Adjusted Rate"] = (
        accounts["End Balance"]/totalbalance)*accounts["Return"]
    adjrate = accounts["Adjusted Rate"].sum()
    df = pd.DataFrame()
    df["Cashflow"] = cashflow["Net Cashflow"]
    x2 = np.asarray(cashflow)
    i = 0
    shape = np.shape(x2)[0]
    investmentbalance = []
    incomefromnonreg = []
    while i < shape:
        if df.iloc[i, -1] < 0:
            totalbalance = totalbalance*(1+(adjrate/100)) + (df.iloc[i, -1])
            investmentbalance.append(totalbalance)
            incomefromnonreg.append(df.iloc[i, -1])
        else:
            totalbalance = totalbalance*(1+(adjrate/100))
            investmentbalance.append(totalbalance)
            incomefromnonreg.append(0)
        i += 1
    df["Investment Balance"] = investmentbalance
    df["Investment Income"] = incomefromnonreg
    return (df)

#includes cashflow DF with non-reg balances and liquidations. final Retirement calculations.
def completeretirement():
    cashflow = retirementcashflow()
    investmentaccounts = sellnonreg()
    complete = pd.DataFrame()
    complete = cashflow
    complete["Investment Balance"] = investmentaccounts["Investment Balance"]
    complete["Investment Liquidations"] = (investmentaccounts["Investment Income"])*(-1)
    return (complete)

#given accounts listed, return yearly balance of accounts untill retirement date
def account_yearly_balance():
    x2 = np.asarray(accountsDF)
    c = 0
    df = pd.DataFrame()
    while c < (np.size(x2, 0)):
        data = np.array(simplecompyearly(
            x2[c, 2], x2[c, 4], x2[c, 5], years_to_ret))
        i = 0
        dffinal = pd.DataFrame()
        while i < (np.size(data, 0)):
            dffinal[i] = [now.year + i, data[i]]
            i += 1
        dffinal = dffinal.transpose()
        dffinal.columns = ["year", x2[c, 1]]
        df[x2[c, 1]] = dffinal[x2[c, 1]]
        c += 1
    years = []
    df['Total'] = df.sum(axis=1)
    i = 0
    while i < len(df.index):
        years.append(now.year + i)
        i += 1
    df.insert(0, "Year", years, True)
    return (df)

#call the final functions to create final dataframes
FinalRetirement = completeretirement()
FinalIncomeExp = income_expenses()
Investments_to_retirement = account_yearly_balance()

#write dataframes for use in other apps
FinalRetirement.to_csv("Output/Retirement.csv")
FinalIncomeExp.to_csv("Output/Cashflow.csv")
Investments_to_retirement.to_csv("Output/Current.csv")
