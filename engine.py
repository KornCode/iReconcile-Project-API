import pandas as pd
import numpy as np
from pandas import isnull
from datetime import date, timedelta

class ReconcileEngine():
    def __init__(self, listLedgerDF, listBankDF, errAmount = 0, errDay = 0):
        self.bankDF = listBankDF
        self.ledgerDF = listLedgerDF
        self.solution = {}

        # comvert 'DD Month YY' string to Date type
        self.bankDF['Date'] = pd.to_datetime(self.bankDF['Date'])
        self.ledgerDF['Date'] = pd.to_datetime(self.ledgerDF['Date'])

        self.bankDF['associate'] = np.nan
        self.ledgerDF['associate'] = np.nan

        self.bankDF['Desc'] = self.bankDF['Desc'].astype(str)
        self.ledgerDF['Desc'] = self.ledgerDF['Desc'].astype(str)

        # Should have something automatic detect Description or Item
        bankColName = self.seperate_word(self.bankDF, "Desc")
        ledgerColName = self.seperate_word(self.ledgerDF, "Desc")

        self.ledgerDF = self.ledgerDF.reset_index()

        self.check_number(self.ledgerDF, self.bankDF, errAmount, errDay)
        self.matching(self.ledgerDF, self.bankDF, ledgerColName, bankColName)

    def seperate_word(self, df, column_name):
        """Create new Dataframe Column with separate word"""
        word_sep = []
        for index in df.index:
            word_sep.append([x.lower() for x in list(df.loc[index, column_name])])
            df[str(column_name)+'_sep'] = pd.Series(word_sep)
        return str(column_name)+'_sep'
    
    def compare_list(self, list_word1, list_word2):
        """Compare set of word and return score"""
        score = 0
        set1 = set(list_word1)
        set2 = set(list_word2)
        for x in set1:
            for y in set2:
                if (x == y):
                    score += 1
        return score

    def associate(self, df, o, d):
        """associate, a = origin_index, b = destination_index"""
        isAssign = False

        # Check if that original already has value?
        if (not (isnull(df['associate'][o]))):
            pass
        # Check If destination index already used or not?
        elif(len(df.loc[df['associate'] == d]) == 1):
            pass
        else:
            df['associate'][o] = int(d)
            isAssign = True

        return isAssign

    def matching(self, ledgerDF, bankDF, ledgerCol, bankCol):
        series = ledgerDF[ledgerCol]
        series2 = bankDF[bankCol]
        for row2 in series2.iteritems():
            best_score = 0
            cur_score = 0
            for row in series.iteritems():
                cur_score = self.compare_list(row2[1], row[1])
                if cur_score > best_score :
                    best_score = cur_score
                    best_row = row
            self.associate(self.bankDF, row2[0], best_row[0])

    def check_number(self, ledgerDF, bankDF, errAmount, errDay):
        for i in bankDF.index:
            for j in ledgerDF.index:
                boolDate = bankDF.loc[i, 'Date'].date() == ledgerDF.loc[j, 'Date'].date()
                rowDeposit = bankDF.loc[i, 'Deposit']
                rowDebit = ledgerDF.loc[j, 'Debit']
                rowWithdrawals = bankDF.loc[i, 'Withdraw']
                rowCredit = ledgerDF.loc[j, 'Credit']

                if (isnull(rowDeposit) & isnull(rowDebit)):
                    boolMoneyIn = True
                elif (rowDeposit == rowDebit):
                    boolMoneyIn = True
                elif (rowDeposit - errAmount <= rowDebit <= rowDeposit + errAmount):
                    boolMoneyIn = True
                else: 
                    boolMoneyIn = False

                if (isnull(rowWithdrawals) & isnull(rowCredit)):
                    boolMoneyOut = True
                elif (rowWithdrawals == rowCredit):
                    boolMoneyOut = True
                elif (rowWithdrawals - errAmount <= rowCredit <=  rowWithdrawals + errAmount):
                    boolMoneyOut = True
                else: 
                    boolMoneyOut = False

                if (errDay > 0 & (not boolDate)):
                    bankDate = bankDF.loc[i, 'Date'].date()
                    ledgerDate = ledgerDF.loc[j, 'Date'].date()
                    margin = timedelta(days = errDay)
                    boolDate = bankDate - margin <=  ledgerDate <= bankDate + margin

                if (boolDate and boolMoneyIn and boolMoneyOut):
                    isAssign = self.associate(self.bankDF, i, j)
                    if isAssign: 
                        break
                    else: 
                        continue

if __name__ == "__main__":
    pass