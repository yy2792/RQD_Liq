import pandas as pd
import os
from portfolioLiq import *
from plot import *
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

    #dirname = os.path.dirname(__file__)

    filePath = 'RQD_Liquidity Case.xlsx'

    df_fund, df_tranche = read_input(filePath)

    res_port = read_df_to_port(df_fund, df_tranche)

    # region task1a

    # tranche level projections
    # assume decision date to redem is 2017.5.31

    print('Tranche Level Settlement Projection： ')

    decision_date = '2017-05-31'

    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()

    res = res_port.tranche_level_project(decision_date)

    with open('Tranche_Level_Settle_Projection_{}.json'.format(decision_date), 'w') as jsonfile:
        json.dump(res, jsonfile, indent = 4, default=default)

    print('result saved to Tranche_Level_Settle_Projection_{}.json'.format(decision_date))

    # endregion

    # region task1b
    # for each fund, calculate weighted avg time to liqudity
    print('Fund Level Liquidity Calculation')

    res = res_port.weight_avg_liquidity_fund_level(decision_date)

    with open('Fund_level_weight_avg_liquidity_{}.json'.format(decision_date), 'w') as jsonfile:
        json.dump(res, jsonfile, indent = 4, default=default)

    print('result saved to Fund_level_weight_avg_liquidity_{}.json'.format(decision_date))

    # endregion

    # region task1c

    print('Portfolio Level Liquidity Calculation')

    res_num = res_port.weight_avg_liquidity_portfolio(decision_date)

    res = {'Portfolio': round(res_num, 5)}

    with open('Portfolio_level_weight_avg_liquidity_{}.json'.format(decision_date), 'w') as jsonfile:
        json.dump(res, jsonfile, indent = 4, default=default)

    print('result saved to Portfolio_level_weight_avg_liquidity_{}.json'.format(decision_date))

    # endregion




