import pandas as pd
import os
from portfolioLiq import *
import json

def read_input(path):

    df_tranche = pd.read_excel(filePath, 'Tranche Investment Data')
    df_fund = pd.read_excel(filePath, 'Fund Terms')

    df_tranche.loc[:, 'Date of Investment'] = df_tranche['Date of Investment'].apply(lambda x: x.date())

    return df_fund, df_tranche

def read_df_to_port(df_fund, df_tranche):

    res_port = Portfolio()

    for index, row in df_fund.iterrows():

        temp_fund = Fund(row[0], row[1], row[2], row[3], row[4])
        res_port.add_fund(temp_fund)

    for index, row in df_tranche.iterrows():

        # first use index as the id for tranches
        temp_tranche = Tranche(row[0], row[1], row[2], index)
        res_port.add_tranche(temp_tranche)

    return res_port



if __name__ == "__main__":

    dirname = os.path.dirname(__file__)
    filePath = dirname + '/inputs/RQD_Liquidity Case.xlsx'

    df_fund, df_tranche = read_input(filePath)

    res_port = read_df_to_port(df_fund, df_tranche)

    # task 1 a, tranche level projections

    # assume decision date to redem is 2017.5.31

    print('Tranche Level Settlement Projection')

    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()

    res = res_port.tranche_level_project('2017-05-31')

    with open('Tranche_Level_Settle_Projection.json', 'w') as jsonfile:
        json.dump(res, jsonfile, indent = 4, default=default)
