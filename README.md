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

* The first file gives prediction for settlement date for each future redemption, given the decision date to redem as 
2017-05-31.

* The second file gives the weighted average time to liquidity for each fund.

* The last file gives the weighted average time to liquidity for the whole portfolio.

Below plots visualize the projections for tranches, funds, and whole portfolio.

```

fund_level_liquidity_2017-05-31.png
fund_level_liquidity_2017-05-31.png
fund_level_liquidity_2017-05-31.png

```

## Project description

### Calculation and assumptions

* The project assumes that on the date we decide to redeem the investment,
the NAV for each tranche after the decision date does not change. (The given NAV
is the NAV on the decision date and it does not change until the redemption date)

* Weighted average time to liquidity is calculated as the NAV value weighted average of time from decision date to 
settlement date for each future cash flow (no matter we calculate on the fund base, tranche base or portfolio base). No time value is considered.


### Method

The project creates a class named Portfolio, essentially the in a portfolio instance we hold a list of fund instances,
each fund has the information for liquidity restrictions. A portfolio instances also holds a list 
of tranches, each tranche will be associated with a certain fund.

Fund has the information of redemption frequency, settlement period, gate, lockup,
tranche instance has the information of when invested in, nav. 

In run.py, we provide read_input function and read_df_to_port function which reads two dataframes,
each belongs to the given spreadsheet, function returns a portfolio instance.

```bash

df_fund, df_tranche = read_input(excel_path)

example_port = read_df_to_port(df_fund, df_tranche)

```

One can see what funds inside the portfolio by running 

```bash

example_port.get_fund_names()

```

For a given fund, the instance can print all tranches information 
associated with the fund

```bash

example_port.print_tranche(fundname)

```

As we now have all the liquidity restriction information for fund, 
and the investment and investment date for a tranche, given a decision date,
we can project what the future settlement (redemption) dates will be like.

Given a tranche (each tranche has a unique id), the portfolio instance will 
look at that tranche instance, pull the information for the associated fund,
consider the restrictions and give out settlement date projection.

The method tranche_level_project is given, when given a decision date,
the method will give all the projections for settlement date and cash flow redemption value.
result is a list of dictionary as in the json file.

```bash

example_port.tranche_level_project(decision_date)

```

Based on the settlement date, redemption value projection, we can calculate
the value weighted time to liquidity, for a certain fund, or for the whole portfolio.

```bash

example_port.weight_avg_liquidity_fund_level(decision_date)

example_prot.weight_avg_liqudity_portfolio(decision_date)

```

The result are given as a list of dictionaries for fund level, with key as fund name,
value is the liquidity measure.


