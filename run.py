import pandas as pd
import os
from datetime import date

if __name__ == "__main__":

    dirname = os.path.dirname(__file__)
    filePath = dirname + '/inputs/RQD_Liquidity Case.xlsx'

    df_tranche = pd.read_excel(filePath, 'Tranche Investment Data')

    print(df_tranche.loc[1,'Date of Investment'].year)