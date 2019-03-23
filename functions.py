import pandas as pd
import sys
from io import StringIO

def csv_to_df (csv):
	file_Str = StringIO(csv)
	df = pd.read_csv(file_Str, sep=',')
	return df