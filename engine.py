import pandas as pd
import numpy as np
from pandas import isnull
from datetime import date, timedelta

class ReconcileEngine():
    def __init__(self, listBankDF, listLedgerDF, normalCheck = False, nameCheck = False, errAmount = 0, errDay = 0):
        self.bankDF = listBankDF
        self.ledgerDF = listLedgerDF
        self.solution = {}

        self.bankDF['Date'] = pd.to_datetime(self.bankDF['Date'])
        self.ledgerDF['Date'] = pd.to_datetime(self.ledgerDF['Date'])

        self.bankDF['associate'] = np.nan
        self.ledgerDF['associate'] = np.nan

        self.bankDF['Desc'] = self.bankDF['Desc'].astype(str)
        self.ledgerDF['Desc'] = self.ledgerDF['Desc'].astype(str)

        #Should have something automatic detect Description or Item
        bankColName = self.seperate_word(self.bankDF,"Desc")
        ledgerColName = self.seperate_word(self.ledgerDF,"Desc")

        #Has to specific Name that contain NSF Problem
        (self.bankDF , self.onlyNSF) = self.remove_nsf(self.bankDF,"Desc")

        # self.bankDF = self.bankDF.reset_index()
        self.ledgerDF = self.ledgerDF.reset_index()

        if (normalCheck): self.check_number(self.ledgerDF, self.bankDF, errAmount, errDay)
        if (nameCheck): self.matching(self.ledgerDF,self.bankDF,ledgerColName,bankColName)
        
        # get NSF cheque row back & correct index
        __list = [self.bankDF, self.onlyNSF]
        self.bankDF = pd.concat(__list)
        self.bankDF = self.bankDF.reset_index()

    
    def printBankDF(self):
        # print(self.bankDF)
        pass

    def printLedgerDF(self):
        # print(self.ledgerDF)
        pass

    def printSolution(self):
        # print(self.solution)
        pass

    def seperate_word(self, df, column_name):
        """Create new Dataframe Column with separate word"""
        word_sep = []
        for index, row in df.iterrows():
            word_sep.append([x.lower() for x in list(row[column_name])])
            df[str(column_name)+'_sep'] = pd.Series(word_sep)
        return str(column_name)+'_sep'
    
    def compare_list(self, list_word1, list_word2):
        """Compare set of word and return score"""
        score = 0
        set1 = set(list_word1)
        set2 = set(list_word2)
        for x in set1:
            for y in set2:
                if(x==y):
                    score = score + 1
        return score

    def remove_nsf(self, df, colname):
        _df = df[~df[colname].str.contains("NSF")]
        __df = df[df[colname].str.contains("NSF")]
        return _df,__df

    def associate(self, df, o, d):
        """associate, a = origin_index, b = destination_index"""
        # Check if that original already has value?
        isAssign = False
        if (not (isnull(df['associate'][o]))):
            # print(' original index', str(o) , 'already has reconciled')
            pass
        # Check If destination index already used or not?
        elif(len(df.loc[df['associate'] == d]) == 1):
            # print(' destination index', str(d) , 'already has reconciled')
            pass
        else:
            df['associate'][o] = int(d)
            isAssign = True
        return isAssign

    def matching(self, ledgerDF, bankDF, ledgerCol, bankCol):
        # print("Doing name item check....")
        series = ledgerDF[ledgerCol]
        series2 = bankDF[bankCol]
        for row2 in series2.iteritems():
            best_score = 0
            cur_score = 0
            for row in series.iteritems():
                cur_score = self.compare_list(row2[1],row[1])
                if cur_score > best_score :
                    best_score = cur_score
                    best_row = row
            self.associate(self.bankDF,row2[0],best_row[0])
            # print("BEST ARE ", row2[0],''.join(row2[1]) ," BY ", best_row[0],''.join(best_row[1])," SCORE= ",best_score)
    
    def check_number(self, ledgerDF, bankDF, errAmount, errDay):
        for indexBank, rowBank in bankDF.iterrows():
            for indexLedger, rowLedger in ledgerDF.iterrows():
                # boolDate = rowBank['Date'].date() == rowLedger['Date'].date()
                # rowDeposit = float(str(rowBank['Deposit']).replace(',',''))
                # rowDebit = float(str(rowLedger['Debit']).replace(',',''))
                # rowWithdrawals = float(str(rowBank['Withdraw']).replace(',',''))
                # rowCredit = float(str(rowLedger['Credit']).replace(',',''))

                boolDate = rowBank['Date'].date() == rowLedger['Date'].date()
                rowDeposit = rowBank['Deposit']
                rowDebit = rowLedger['Debit']
                rowWithdrawals = rowBank['Withdraw']
                rowCredit = rowLedger['Credit']

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
                    bankDate = rowBank['Date'].date()
                    ledgerDate = rowLedger['Date'].date()
                    margin = timedelta(days = errDay)
                    boolDate = bankDate - margin <=  ledgerDate <= bankDate + margin

                # print(boolDate , rowBank['Date'].date(), rowLedger['Date'].date())
                # print(boolMoneyIn, rowDeposit , rowDebit)
                # print(boolMoneyOut, rowWithdrawals, rowCredit)

                if (boolDate and boolMoneyIn  and boolMoneyOut):
                    # print("compare by date, money.. "+ str(indexBank) \
                    #     +" equal to " + str(indexLedger))
                    isAssign = self.associate(self.bankDF,indexBank,indexLedger)
                    if isAssign: break
                    else: continue
                # else:print("not match")

if __name__ == "__main__":
    pass