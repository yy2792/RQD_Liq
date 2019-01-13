import pandas as pd
import os
from portfolioLiq import *

def read_input(path):

    df_tranche = pd.read_excel(filePath, 'Tranche Investment Data')
    df_


if __name__ == "__main__":

    dirname = os.path.dirname(__file__)
    filePath = dirname + '/inputs/RQD_Liquidity Case.xlsx'

    df_tranche = pd.read_excel(filePath, 'Tranche Investment Data')

    print(df_tranche)