import pandas as pd
import numpy as np
import sys
from io import StringIO

def csv_to_df (csv):
	file_Str = StringIO(csv)
	df = pd.read_csv(file_Str, sep=',')
	return df

def remaining_to_values (ledgerDf, bankDf, asso):
	asso_dict = asso.to_dict()
	asso_ledger_value = list(asso_dict.values())

	ledgerIndex = []
	ledgerIndexDebit = []
	ledgerIndexCredit = []
	for index in range(len(asso_ledger_value)):
		if index not in asso_ledger_value:
			ledgerIndex.append(index)
			ledgerIndexDebit.append(ledgerDf.loc[index, "Debit"])
			ledgerIndexCredit.append(ledgerDf.loc[index, "Credit"])

	bankIndex = []
	bankIndexDeposit = []
	bankIndexWithdraw = []
	for key, value in asso_dict.items():
		if np.isnan(value):
			bankIndex.append(int(key))
			bankIndexDeposit.append(bankDf.loc[int(key), "Deposit"])
			bankIndexWithdraw.append(bankDf.loc[int(key), "Withdraw"])

	ledgerDict = {
		"Index": ledgerIndex,
		"Credit": ledgerIndexCredit,
		"Debit": ledgerIndexDebit
	}
	bankDict = {
		"Index": bankIndex,
		"Withdraw": bankIndexWithdraw,
		"Deposit": bankIndexDeposit
	}

	resultLedgerDf = pd.DataFrame(ledgerDict)
	resultLedgerDf = resultLedgerDf.set_index("Index")
	resultBankDf = pd.DataFrame(bankDict)
	resultBankDf = resultBankDf.set_index("Index")

	print(resultLedgerDf)
	print(resultBankDf)

	return resultLedgerDf, resultBankDf