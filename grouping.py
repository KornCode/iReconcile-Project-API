from itertools import combinations 
import pandas as pd
import json

class FindGroupSum():
    def __init__(self, bankDf, ledgerDf):
        global resultGroup
        resultGroup = []
        self.ledgerDf = ledgerDf
        self.bankDf = bankDf

        #Bank
        listDep = self.getNotNullList(bankDf, 'Deposit')
        listWit = self.getNotNullList(bankDf, 'Withdraw')

        #Ledger
        listCre = self.getNotNullList(ledgerDf, 'Credit')
        listDe = self.getNotNullList(ledgerDf, 'Debit')

        #Bank
        combDep = self.getCombList(listDep)
        combWit = self.getCombList(listWit)

        #Ledger
        combCre = self.getCombList(listCre)
        combDe = self.getCombList(listDe)

        state1=True
        while(state1):
            combDep = self.getCombList(listDep)
            combDe = self.getCombList(listDe)
            state1 = self.oneCompare(listDep, listDe, combDep , combDe , 'Deposit', 'Debit')
            
        state2=True
        while(state2):
            combWit = self.getCombList(listWit)
            combCre = self.getCombList(listCre)
            state2 = self.oneCompare(listWit, listCre, combWit , combCre , 'Withdraw', 'Credit')

        
        self.unableBank = listDep + listWit
        self.unableLedger = listDe + listCre
        self.resultGroup = resultGroup
        print("resultGroup = " , resultGroup )
        print("unableBank = ", self.unableBank )
        print("unableLedger = ", self.unableLedger )

    def getNotNullList(self, df, colname):
        return df[~df[colname].isnull()].index.tolist()


    def getCombList(self, listInput):
        listOutput = []
        for j in range(len(listInput)):
            comb = combinations(listInput, j+1) 
            listOutput.extend(list(comb))
        return listOutput


    def oneCompare(self, listBank, listLedger, combBank , combLedger , cBank, cLedger):

        def removeIndex(my_list, indexes):
            for e in indexes: 
                my_list.remove(e)

        if (len(listBank) == 0) or (len(listLedger)==0):
            print("empty")
            return False
        
        for i in combBank:
            nBank = self.bankDf[cBank][list(i)].sum()
            for j in combLedger:
                nLedger =  self.ledgerDf[cLedger][list(j)].sum()
                if(nBank == nLedger):
                    print(list(i), nLedger,end=' matched ')
                    print(list(j), nBank)
                    jsonform = {
                        "bank":list(i),
                        "ledger":list(j)
                    }
                    resultGroup.append(jsonform)
                    removeIndex(listBank, list(i))
                    removeIndex(listLedger, list(j))
                    print(listBank, listLedger)
                    return True
        return False
                

if __name__ == "__main__":
    pass
