# RQD_Liq

This project reads fund liquidity restrictions, tranche investments information
from spreadsheet, and provides tranche level, fund level, portfolio level
settlement time, weighted average time to liquidity projection.

## Getting Started 

First instructions to get the project set up and running on your local
machine are given. 

### Prerequisites

This project is coded in Python3, requirement.txt file includes package requirements
for the project.

User can choose to create a virtual environment to set up the project

```

python3 -m virtualenv env

.\env\Scripts\activate

(env) pip install -r requirements.txt

```

### Running the program

There are 4 python files in the directory, fundLiq.py defines fund class, and tranche class,
portfolioLiq.py defines a portfolio class wrapping up fund and tranche classes. File run.py reads
excel file RQD_Liquidity Case.xlsx, and gives out three json files as the 
result.

For visualization, plot.py file gives out plots for fund level, tranche level, portfolio
level liquidity projections.


```

python run.py
python plot.py

```

### Result Preview

Outputs for run.py 

```

Tranche_Level_Settle_Projection_2017-05-31.json
Fund_level_weight_avg_liquidity_2017-05-31.json
Portfolio_level_weight_avg_liquidity_2017-05-31.json

```

The first file gives prediction for settlement date for each future redemption, given the decision date to redem as 
2017-05-31.

The second file gives the weighted average time to liquidity for each fund.

The last file gives the weighted average time to liquidity for the whole portfolio.

Below plots visualize the projections for tranches, funds, and whole portfolio.

```

fund_level_liquidity_2017-05-31.png
fund_level_liquidity_2017-05-31.png
fund_level_liquidity_2017-05-31.png

```


