from fundLiq import *
import warnings


class Portfolio:
    '''
    a portfolio class essentially has two parts
    a dictionary of funds, each fund stores fund
    level information, the other part is all the
    tranches inside the Portfolio, each tranche
    has a fundname as a key to match fund
    '''

    def __init__(self):
        self.__fundLists = {}
        # tranche is stored in a dictionary, key is fund name,
        # value is a dictionary of existing tranches, key is
        # tranche id
        self.__tranches = {}
        # each tranche has a unique id, and associated with its fund name
        self.__tranches_id = {}

    # region change and add attr

    def add_fund(self, fund):

        if fund.get_name() in self.__fundLists:
            warnings.warn('''
                        The fund is already stored in the portfolio,
                        now you are updating it, for updating please
                        call method update_fund''')

        else:
            self.__fundLists[fund.get_name()] = fund
            self.__tranches[fund.get_name()] = {}

    # update any fund info inside the class
    def update_fund(self, name, redemfreq=None, setperiod=None, gate=None, lockup=None):

        if name in self.__fundLists:
            self.__fundLists[name].set_attr(redemfreq, setperiod, gate, lockup)
        else:
            raise MyError('updating a fund that does not exist before')

    def get_fundLists(self):
        # for debug, return a copy of attribute fundList
        temp_fundLists = copy.deepcopy(self.__fundLists)
        return temp_fundLists

    # return all fund name inside the portfolio
    def get_fund_names(self):
        # return all existing fund names
        return [x for x in self.__fundLists]

    # add in a tranche
    def add_tranche(self, tranche):

        fund_name = tranche.get_fundname()
        tranche_id = tranche.get_id()

        if tranche_id in self.__tranches_id:
            raise MyError('This tranche already exists inside the \
            internal tranche table')

        if fund_name not in self.__fundLists:
            raise MyError('the fund of this tranche does not exist \
            in the internal fund table')

        self.__tranches_id[tranche_id] = fund_name
        self.__tranches[fund_name][tranche_id] = tranche

    # update an exisitng tranche's nav
    def update_tranche_nav(self, id, nav):
        # only nav can be updated
        fund_name = self.__tranches_id[id]
        self.__tranches[fund_name][id].update_nav(nav=nav)

    # print all the tranches inside the portfolio
    def print_tranche(self, fundname):
        # print out what tranches exist for a certain fund
        print(self.__tranches[fundname])

    # endregion

    def project_settle(self, fund_name, decision_date):

        decision_date = transfer_date(decision_date)

        res = {}

        for id, tranche in self.__tranches[fund_name].items():
            res[id] = tranche.project_settle(self.__fundLists[fund_name], decision_date)

        return res

    # fund level average liquidity
    def weight_avg_liquidity_fund(self, fund_name, decision_date):

        decision_date = transfer_date(decision_date)

        sum_nav = 0
        sum_days = 0

        project_dates = self.project_settle(fund_name, decision_date)

        for id, tranche in self.__tranches[fund_name].items():

            sum_nav += tranche.get_nav()

            for temp_pair in project_dates[id]:
                temp_days = (temp_pair[0] - decision_date).days
                sum_days += temp_days * temp_pair[1]

        return sum_days / float(sum_nav)

    # portfolio level avg liquidity
    def weight_avg_liquidity_portfolio(self, decision_date):

        decision_date = transfer_date(decision_date)

        sum_nav = 0
        sum_days = 0

        # adding up all the weighted time to liquidity for each redemption in each tranche
        for fund_name in self.__fundLists:

            # for a single fund, all the settlements dats
            project_dates = self.project_settle(fund_name, decision_date)

            for id, tranche in self.__tranches[fund_name].items():

                sum_nav += tranche.get_nav()

                for temp_pair in project_dates[id]:
                    temp_days = (temp_pair[0] - decision_date).days
                    sum_days += temp_days * temp_pair[1]

        return sum_days / float(sum_nav)




class TestPortfolioFunctions(unittest.TestCase):

    def test_add_fund(self):
        fd = Fund('testFund', 'M', 45, 0.25, 12)
        pf = Portfolio()
        pf.add_fund(fd)

        fd2 = Fund('testFund2', 'Q', 30, 0.25)
        pf.add_fund(fd2)

        self.assertEqual(pf.get_fund_names(), [fd.get_name(), fd2.get_name()])

    def test_add_tranche(self):

        tc1 = Tranche('testFund', '2017-01-01', 100, 1)
        tc2 = Tranche('testFund', '2017-02-01', 300, 2)
        tc3 = Tranche('testFund2', '2017-03-01', 100, 3)

        pf = Portfolio()
        fd = Fund('testFund', 'M', 45, 0.25, 12)
        fd2 = Fund('testFund2', 'Q', 30, 0.25)

        pf.add_fund(fd)
        pf.add_fund(fd2)

        pf.add_tranche(tc1)
        pf.add_tranche(tc2)
        pf.add_tranche(tc3)

        print('testing add tranche function')
        pf.print_tranche('testFund')

        tc4 = Tranche('testFund3', '2018-01-01', 100, 4)

        try:
            pf.add_tranche(tc4)
        except MyError as er:
            self.assertEqual('the fund of this tranche does not exist \
            in the internal fund table', er.message)

        try:
            pf.add_tranche(tc1)
        except MyError as er:
            self.assertEqual('This tranche already exists inside the \
            internal tranche table', er.message)

        pf.update_tranche_nav(3, 300)
        self.assertEqual(tc3.get_nav(), 300)

    def test_update_fund(self):

        tc1 = Tranche('testFund', '2017-01-01', 100, 1)
        tc2 = Tranche('testFund', '2017-02-01', 300, 2)
        tc3 = Tranche('testFund2', '2017-03-01', 100, 3)

        pf = Portfolio()
        fd = Fund('testFund', 'M', 45, 0.25, 12)
        fd2 = Fund('testFund2', 'Q', 30, 0.25)

        pf.add_fund(fd)
        pf.add_fund(fd2)

        pf.add_tranche(tc1)
        pf.add_tranche(tc2)
        pf.add_tranche(tc3)

        print(pf.get_fundLists())
        self.assertEqual(pf.get_fundLists(), {'testFund': fd, 'testFund2':fd2})

        # when we change the global fd, the fd inside portfolio also changes
        fd2.set_attr(lockup=12)
        print(pf.get_fundLists())
        self.assertEqual(pf.get_fundLists(), {'testFund': fd, 'testFund2': fd2})

        # also we do it inside portfolio class
        pf.update_fund('testFund', lockup=36)
        print(fd)
        self.assertEqual(pf.get_fundLists(), {'testFund': fd, 'testFund2': fd2})

    def test_project_settle(self):

        tc1 = Tranche('testFund1', '2017-01-01', 100, 1)
        tc2 = Tranche('testFund1', '2017-02-01', 300, 2)
        tc3 = Tranche('testFund2', '2017-03-01', 100, 3)

        pf = Portfolio()
        fd = Fund('testFund1', 'M', 45, 0.25, 12)
        fd2 = Fund('testFund2', 'Q', 0, 1)

        pf.add_fund(fd)
        pf.add_fund(fd2)

        pf.add_tranche(tc1)
        pf.add_tranche(tc2)
        pf.add_tranche(tc3)

        res = pf.project_settle('testFund1', date(2017, 11, 1))

        # for tc1, the lockup day ends at 2018.1.1, redem at 2018.1.31
        # after 45 days, the settlement begins at 3.17, next redem at
        # 2018.2.28, after 45 days, the settlement begins at 4.14,
        # next redem at 2018.3.31, the settle happens at 5.15...

        self.assertEqual([x[0] for x in res[1]], [date(2018, 3, 17), date(2018, 4, 14), \
                                                  date(2018, 5, 15), date(2018, 6, 14)])

        # for tc2, no lockup, first settle at 2.28, after 45 days gives 4.14....
        self.assertEqual([x[0] for x in res[2]], [date(2018, 4, 14), date(2018, 5, 15), \
                                                  date(2018, 6, 14), date(2018, 7, 15)])

        res2 = pf.project_settle('testFund2', date(2017, 11, 1))

        self.assertEqual(date(2017, 12, 31), res2[3][0][0])

    def test_weight_avg_liquidity_fund(self):

        tc1 = Tranche('testFund1', '2017-01-01', 100, 1)
        tc2 = Tranche('testFund1', '2017-02-01', 300, 2)
        tc3 = Tranche('testFund2', '2017-03-01', 100, 3)

        pf = Portfolio()
        fd = Fund('testFund1', 'M', 45, 0.25)
        fd2 = Fund('testFund2', 'Q', 0, 1, 12)

        pf.add_fund(fd)
        pf.add_fund(fd2)

        pf.add_tranche(tc1)
        pf.add_tranche(tc2)
        pf.add_tranche(tc3)

        # for fund1, in all the nav has value of 400

        project_date = pf.project_settle('testFund1', date(2017, 11, 1))
        pdates1 = [x[0] for x in project_date[1]]
        pdates2 = [x[0] for x in project_date[2]]

        ptimes1 = [(x - date(2017, 11, 1)).days for x in pdates1]
        ptimes2 = [(x - date(2017, 11, 1)).days for x in pdates2]

        res = 0
        for i in ptimes1:
            res += i * 25
        for i in ptimes2:
            res += i * 75

        res /= float(400)

        self.assertEqual(pf.weight_avg_liquidity_fund('testFund1', date(2017, 11, 1)), res)

        # for fund2, 12 months lockup, 2018-02-01
        temp_time = (date(2018, 3, 31) - date(2017, 11, 1)).days
        res2 = pf.weight_avg_liquidity_fund('testFund2', date(2017, 11, 1))

        self.assertEqual(temp_time, res2)

    def test_weight_avg_liquidity_portfolio(self):

        tc1 = Tranche('testFund1', '2017-01-01', 100, 1)
        tc2 = Tranche('testFund1', '2017-02-01', 300, 2)
        tc3 = Tranche('testFund2', '2017-03-01', 100, 3)

        pf = Portfolio()
        fd = Fund('testFund1', 'M', 45, 0.25)
        fd2 = Fund('testFund2', 'Q', 0, 1, 12)

        pf.add_fund(fd)
        pf.add_fund(fd2)

        pf.add_tranche(tc1)
        pf.add_tranche(tc2)

        # as we haven't added tc3, the result for portfolio level should be
        # the same as the fund level

        res1 = pf.weight_avg_liquidity_fund('testFund1', '2017-11-01')
        res2 = pf.weight_avg_liquidity_portfolio('2017-11-01')

        self.assertEqual(res1, res2)

        pf.add_tranche(tc3)

        res3 = res1 * 400 + pf.weight_avg_liquidity_fund('testFund2', '2017-11-01') * 100
        res3 /= float(500)

        res4 = pf.weight_avg_liquidity_portfolio('2017-11-01')

        self.assertEqual(res3, res4)






if __name__ == "__main__":

    unittest.main()
