import pandas as pd
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from datetime import datetime, date


def plot_fund(df, start, path):
    fundset = set(df['fund'])

    all_funds_df = {}

    min_date = None
    max_date = None

    min_redem = None
    max_redem = None

    for fundname in fundset:
        temp_df = df[df['fund'] == fundname]
        all_items = []
        for index, row in temp_df.iterrows():
            all_items += [(start, 0)] + row['projection']

        df_all = pd.DataFrame(all_items, columns=['date', 'redem'])

        df_all = df_all.groupby('date').sum().reset_index()

        df_all.loc[:, 'date'] = df_all['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        df_all.loc[:, 'redem'] = df_all['redem'].apply(lambda x: float(x))

        df_all.sort_values(by='date')
        df_all.loc[:, 'redem'] = df_all['redem'].cumsum()

        if min_date is None:
            min_date = min(df_all['date'])
        else:
            min_date = min(min(df_all['date']), min_date)

        if max_date is None:
            max_date = max(df_all['date'])
        else:
            max_date = max(max(df_all['date']), max_date)

        if min_redem is None:
            min_redem = min(df_all['redem'])
        else:
            min_redem = min(min(df_all['redem']), min_redem)

        if max_redem is None:
            max_redem = max(df_all['redem'])
        else:
            max_redem = max(max(df_all['redem']), max_redem)

        all_funds_df[fundname] = df_all

    max_date = date(max_date.year, 12, 31)
    min_date = date(min_date.year, min_date.month, 1)

    # These are the "Tableau 20" colors as RGB.
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    plt.figure(figsize=(12, 14))
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.xlim(min_date, max_date)
    plt.ylim(min_redem, max_redem)

    # for fund in all_funds_df:
    plt.xticks(fontsize=14)

    rank = 0

    for fund in all_funds_df:
        df_temp = all_funds_df[fund]
        plt.plot(df_temp['date'], df_temp['redem'], "-", marker='o', lw=2.5,
                 color=tableau20[rank], alpha=0.3, label=fund, markersize=12)
        rank += 1
        plt.tick_params(axis="both", which="both", bottom=False, top=False,
                        labelbottom=True, left=False, right=False, labelleft=True)

    plt.legend()

    plt.title("fund level time to liquidity {}".format(start), {'fontsize': 15})

    plt.savefig(path, bbox_inches="tight")


def plot_tranches(df, start, path):

    trancheset = set(df['id'])

    min_date = None
    max_date = None

    min_redem = None
    max_redem = None

    all_tranches_df = {}

    all_items = []

    for tranche in trancheset:
        temp_df = df[df['id'] == tranche]
        all_items = []
        for index, row in temp_df.iterrows():
            all_items += [(start, 0)] + row['projection']

        df_all = pd.DataFrame(all_items, columns=['date', 'redem'])

        df_all = df_all.groupby('date').sum().reset_index()

        df_all.loc[:, 'date'] = df_all['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        df_all.loc[:, 'redem'] = df_all['redem'].apply(lambda x: float(x))

        df_all.sort_values(by='date')
        df_all.loc[:, 'redem'] = df_all['redem'].cumsum()

        if min_date is None:
            min_date = min(df_all['date'])
        else:
            min_date = min(min(df_all['date']), min_date)

        if max_date is None:
            max_date = max(df_all['date'])
        else:
            max_date = max(max(df_all['date']), max_date)

        if min_redem is None:
            min_redem = min(df_all['redem'])
        else:
            min_redem = min(min(df_all['redem']), min_redem)

        if max_redem is None:
            max_redem = max(df_all['redem'])
        else:
            max_redem = max(max(df_all['redem']), max_redem)

        all_tranches_df[tranche] = df_all

    max_date = date(max_date.year, 12, 31)
    min_date = date(min_date.year, min_date.month, 1)

    # These are the "Tableau 20" colors as RGB.
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    plt.figure(figsize=(12, 14))
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.xlim(min_date, max_date)
    plt.ylim(min_redem, max_redem)

    # for fund in all_funds_df:
    plt.xticks(fontsize=14)

    rank = 0

    for tranche in all_tranches_df:
        df_temp = all_tranches_df[tranche]
        plt.plot(df_temp['date'], df_temp['redem'], "-", marker=rank % 11, lw=2.5,
                 color=tableau20[rank % 20], alpha=0.3, label=tranche, markersize=12)
        rank += 1
        plt.tick_params(axis="both", which="both", bottom=False, top=False,
                        labelbottom=True, left=False, right=False, labelleft=True)

    plt.legend()

    plt.title("tranche level time to liquidity {}".format(start), {'fontsize': 15})

    plt.savefig(path, bbox_inches="tight")



if __name__ == "__main__":

    # region plot

    decision_date = '2017-05-31'

    data = pd.read_json('Tranche_Level_Settle_Projection_{}.json'.format(decision_date))

    path = 'fund_level_liquidity_{}.png'.format(decision_date)

    plot_fund(data, decision_date, path)
    
    path = 'tranche_level_liquidity_{}.png'.format(decision_date)

    plot_tranches(data, decision_date, path)

    # endregion
