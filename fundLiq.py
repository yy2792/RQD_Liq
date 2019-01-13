import unittest
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import bisect
import re
import copy
import pandas as pd

def isnan(num):
    return num != num

# ignore lock up, given a redem frequency, what is the closest redem day for a specific date
def approach_day(start_date, redemfreq):

    temp_year = start_date.year
    temp_month = start_date.month
    temp_day = start_date.day
    res = None

    if redemfreq == 'M':
        if temp_month == 12:
            res = date(temp_year, 12, 31)
        else:
            res = date(temp_year, temp_month + 1, 1) - timedelta(days = 1)

    elif redemfreq == 'Q':
        qrts = [date(temp_year, 3, 31), date(temp_year, 6, 30),
                date(temp_year, 9, 30), date(temp_year, 12, 31)]
        # find the rightmost value less than start_date
        idx = bisect.bisect_left(qrts, start_date)
        res = qrts[idx]

    elif redemfreq == 'S':
        sems = [date(temp_year, 6, 30), date(temp_year, 12, 31)]

        idx = bisect.bisect_left(sems, start_date)
        res = sems[idx]

    elif redemfreq == 'A':
        res = date(temp_year, 12, 31)

    else:
        raise MyError('RedemFreq must be M or Q or S or A')

    return res


# for consistent datetime
def transfer_date(timeinput):
    # for test, if invest_date is passed in as a string, transfer it to timestamp
    if not isinstance(timeinput, date):
        if isinstance(timeinput, str):
            redate = re.compile('\d{4}-\d{2}-\d{2}')
            if redate.search(timeinput):
                return datetime.strptime(timeinput, '%Y-%m-%d').date()
            else:
                raise MyError("invest_date should be timestamp or in the format 'Y-m-d'")
        elif isinstance(timeinput, datetime):
            return timeinput.date()
        else:
            raise MyError("Illegal time format")
    else:
        return timeinput


class Fund:

    FreqMap = {'monthly': 'M', 'quarterly':'Q', 'semiannual':'S', 'annual':'A'}

    def __init__(self, name, redemfreq, setperiod, gate=None, lockup=None):

        if redemfreq.lower() in self.FreqMap:
            redemfreq = self.FreqMap[redemfreq.lower()]

        if isnan(gate):
            gate = None

        if isnan(lockup):
            lockup = None

        self.attr_check(name, redemfreq, setperiod, gate, lockup)

        self.__name = name
        self.__RedemFreq = redemfreq.upper()
        self.__SetPeriod = setperiod
        self.__gate = gate
        self.__lockup = lockup

    # check if all the inputs are legal
    @classmethod
    def attr_check(cls, name, RedemFreq, SetPeriod, gate, lockup):

        if RedemFreq.upper() not in ['M', 'Q', 'S', 'A']:
            raise MyError('RedemFreq must be M or Q or S or A')

        if gate is not None:
            if gate < 0 or gate > 1:
                raise MyError('gate must be None or between 0 and 1')

    def __str__(self):
        rp_str = '''
        fund name: {0}
        RedemFreq: {1}
        SetPeriod: {2}
        Gate: {3}
        Lockup: {4}
        '''.format(self.__name, self.__RedemFreq, self.__SetPeriod,
                   self.__gate, self.__lockup)
        return rp_str

    def __repr__(self):
        return self.__str__()

    # given a specific invest_date, return the legal date for redemption (lock up)
    def est_legal_redem(self, invest_date):
        if self.__lockup is None:
            return invest_date

        return invest_date + relativedelta(months=self.__lockup)

    # given a specific date, and investment date, return the estimated redemption date
    def est_first_redem(self, invest_date, decision_date):
        # invest_date and decision date should all be in timestamp

        legal_start_date = self.est_legal_redem(invest_date)
        temp_start_date = decision_date

        # if decision date comes before legal start_dte, replace decision date with legal start
        if temp_start_date < legal_start_date:
            temp_start_date = legal_start_date

        res = approach_day(temp_start_date, self.__RedemFreq)

        return res

    # given a specific date, and investment date, return the estimated settlement date
    def est_first_settle(self, invest_date, decision_date):

        res = self.est_first_redem(invest_date, decision_date)
        res += timedelta(days=self.__SetPeriod)

        return res

    def get_gate(self):
        temp_gate = copy.deepcopy(self.__gate)
        return temp_gate

    def get_name(self):
        temp_name = copy.deepcopy(self.__name)
        return temp_name

    def get_setperiod(self):
        temp_setperiod = copy.deepcopy(self.__SetPeriod)
        return temp_setperiod

    def set_attr(self, redemfreq=None, setperiod=None, gate=None, lockup=None):

        if redemfreq:
            self.__RedemFreq = redemfreq
        if setperiod:
            self.__SetPeriod = setperiod
        if gate:
            self.__gate = gate
        if lockup:
            self.__lockup = lockup

    def __eq__(self, other):
        if self.__name == other.__name and self.__lockup == other.__lockup and \
            self.__SetPeriod == other.__SetPeriod and self.__RedemFreq == other.__RedemFreq and \
            self.__gate == other.__gate:

            return True
        else:
            return False


class Tranche:

    def __init__(self, fundname, invest_date, nav, id = None):

        invest_date = transfer_date(invest_date)

        # for now let's say we can't short a fund
        if nav < 0:
            raise MyError('nav should be positive for {0}'.format(fundname))

        self.__fundname = fundname
        self.__invest_date = invest_date
        self.__nav = nav
        self.__id = id

    def update_nav(self, nav=None):
        if nav:
            self.__nav = nav

    def get_nav(self):
        temp_nav = copy.deepcopy(self.__nav)
        return temp_nav

    def project_redem(self, fund, decision_date):

        # this functon projects the future redemption, as
        # the investment is marked on the redemption date,
        # we assume the NAV won't change after the request date
        # then each redemption amount is fixed with gate

        decision_date = transfer_date(decision_date)

        # assert tranche invests in the passed in fund
        if fund.get_name() != self.__fundname:
            raise MyError('The passed in fund does not match this tranche')

        temp_decision_date = decision_date
        temp_gate = fund.get_gate()
        temp_deposit = copy.deepcopy(self.__nav)

        if temp_deposit <= 0:
            return []

        if temp_gate is None:
            deduce_amount = temp_deposit
        else:
            deduce_amount = temp_deposit * float(temp_gate)

        res = []

        # sometimes this will end up with a very small number, hence we add a cap on the loop
        while temp_deposit > 1e-9:
            first_redem = fund.est_first_redem(self.__invest_date, temp_decision_date)

            if first_redem is None:
                raise MyError('illegal decision date')

            if deduce_amount <= temp_deposit:
                temp_deposit -= deduce_amount
                res.append((first_redem, deduce_amount))
            else:
                # won't happen in our test sample, but if the last redem is larger than
                # the deposit, what we pull out is only the deposit left
                res.append((first_redem, temp_deposit))
                temp_deposit = 0

            temp_decision_date = first_redem + timedelta(days=1)

        return res

    def project_settle(self, fund, decision_date):
        temp_res = self.project_redem(fund, decision_date)

        res = [(x[0] + timedelta(days=fund.get_setperiod()), x[1]) for x in temp_res]

        return res

    def get_id(self):
        temp_id = copy.deepcopy(self.__id)
        return temp_id

    def get_fundname(self):
        temp_fundname = copy.deepcopy(self.__fundname)
        return temp_fundname

    def __str__(self):
        rp_str = "tranche_id_{0}-fund_name_{1}-invest_date_{2}-NAV_{3}"\
            .format(self.__id, self.__fundname, self.__invest_date, self.__nav)
        return rp_str

    def __repr__(self):
        return self.__str__()


class MyError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message


class TestApproachDateFunction(unittest.TestCase):

    def setUp(self):
        pass

    def testQuarter(self):
        # closer to end
        test1 = date(2017, 11, 17)
        result1 = date(2017, 12, 31)
        self.assertEqual(approach_day(test1, 'Q'), result1)

        # closer to beginning
        test2 = date(2018, 1, 1)
        result2 = date(2018, 3, 31)
        self.assertEqual(approach_day(test2, 'Q'), result2)

        # closer to beginning
        test3 = date(2018, 4, 1)
        result3 = date(2018, 6, 30)
        self.assertEqual(approach_day(test3, 'Q'), result3)

        # corner case
        test4 = date(2018, 12, 31)
        result4 = date(2018, 12, 31)
        self.assertEqual(approach_day(test4, 'Q'), result4)

        test5 = date(2018, 8, 15)
        result5 = date(2018, 9, 30)
        self.assertEqual(approach_day(test5, 'Q'), result5)

    def testSemi(self):
        test1 = date(2018, 1, 1)
        result1 = date(2018, 6, 30)
        self.assertEqual(approach_day(test1, 'S'), result1)

        test1 = date(2018, 6, 30)
        result1 = date(2018, 6, 30)
        self.assertEqual(approach_day(test1, 'S'), result1)

        test1 = date(2018, 7, 1)
        result1 = date(2018, 12, 31)
        self.assertEqual(approach_day(test1, 'S'), result1)

        test1 = date(2018, 12, 31)
        result1 = date(2018, 12, 31)
        self.assertEqual(approach_day(test1, 'S'), result1)

    def testMon(self):
        test1 = date(2018, 2, 1)
        result1 = date(2018, 2, 28)
        self.assertEqual(approach_day(test1, 'M'), result1)

        test1 = date(2018, 6, 28)
        result1 = date(2018, 6, 30)
        self.assertEqual(approach_day(test1, 'M'), result1)

    def testYear(self):
        result1 = date(2018, 12, 31)
        for i in range(1, 13):
            test1 = date(2018, i, 10)
            self.assertEqual(approach_day(test1, 'A'), result1)


class TestFundFunctions(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_est_legal_redem(self):
        fd = Fund('testFund', 'M', 45, 0.25, 12)
        test1 = fd.est_legal_redem(date(2017, 1, 1))
        result1 = date(2018, 1, 1)
        self.assertEqual(test1, result1)

        test2 = fd.est_legal_redem(date(2017, 12, 3))
        result2 = date(2018, 12, 3)
        self.assertEqual(test2, result2)

        fd2 = Fund('testFund2', 'M', 45, 0.25)
        test3 = fd2.est_legal_redem(date(2017, 12, 3))
        result3 = date(2017, 12, 3)
        self.assertEqual(test3, result3)

    def test_est_first_redem(self):
        # invest in 2017.1.1, quarterly, earliest redem is 2017.12.31
        fd1 = Fund('testFund1', 'Q', 45, 0.25)
        test1 = fd1.est_first_redem(date(2017, 1, 1), date(2017, 11, 17))
        result1 = date(2017, 12, 31)
        self.assertEqual(test1, result1)

        # invest in 2017.1.1, lockup 6 months, quarterly, earliest redem is 2017.9.30
        fd2 = Fund('testFund2', 'Q', 45, 0.25, 6)
        test2 = fd2.est_first_redem(date(2017, 1, 1), date(2017, 3, 17))
        result2 = date(2017, 9, 30)
        self.assertEqual(test2, result2)

        # invest in 2016.12.30, lockup 6 months, quarterly, earliest redem is 2017.6.30
        fd2 = Fund('testFund2', 'Q', 45, 0.25, 6)
        test3 = fd2.est_first_redem(date(2016, 12, 30), date(2017, 3, 17))
        result3 = date(2017, 6, 30)
        self.assertEqual(test3, result3)

    def test_est_first_settle(self):

        # invest in 2017.1.1, quarterly, earliest redem is 2017.12.31, settle is 2018.2.14
        fd1 = Fund('testFund1', 'Q', 45, 0.25)
        test1 = fd1.est_first_settle(date(2017, 1, 1), date(2017, 11, 17))
        result1 = date(2018, 2, 14)
        self.assertEqual(test1, result1)

    def test_set_attr(self):
        fd1 = Fund('one', 'Q', 45, 0.25)
        self.assertEqual(fd1.get_setperiod(), 45)

        fd1.set_attr(setperiod=30)
        self.assertEqual(fd1.get_setperiod(), 30)

class TestTrancheFunctions(unittest.TestCase):

    def test_init(self):
        fd = Fund('testFund', 'M', 45, 0.25, 12)
        Tranche('testFund', '2017-01-01', 3000)

        # for now we do not accept shorting funds
        fd1 = Fund('testFund1', 'A', 45, 0.2, 12)

        try:
            tc1 = Tranche('testFund1', '2017-01-01', -5)
        except MyError as Er:
            self.assertEqual('nav should be positive for testFund1', Er.message)

    def test_project_redem(self):
        fd1 = Fund('testFund1', 'Q', 45, 0.25)
        tc = Tranche('testFund1', '2017-01-01', 10)

        test1 = tc.project_redem(fd1, '2017-11-17')
        result1 = [(date(2017, 12, 31), 2.5),
                   (date(2018, 3, 31), 2.5),
                   (date(2018, 6, 30), 2.5),
                   (date(2018, 9, 30), 2.5)]

        self.assertEqual(test1, result1)

        # in this test case, the lock up period is 12 months,
        # hence though on 2017.01.01 we decide to redem,
        # the earliest day for redemption will be 2018.12.31
        fd2 = Fund('testFund2', 'A', 45, 0.2, 12)
        tc2 = Tranche('testFund2', '2017-01-01', 10)

        test2 = tc2.project_redem(fd2, '2017-11-17')
        result2 = [(date(2018, 12, 31), 2),
                   (date(2019, 12, 31), 2),
                   (date(2020, 12, 31), 2),
                   (date(2021, 12, 31), 2),
                   (date(2022, 12, 31), 2)]

        self.assertEqual(test2, result2)

        fd3 = Fund('testFund3', 'A', 45, 0.2, 12)
        tc3 = Tranche('testFund3', '2017-01-01', 0)

        test3 = tc3.project_redem(fd3, '2017-11-17')
        result3 = []

        self.assertEqual(test3, result3)

        # passed in a wrong fund
        try:
            tc2.project_redem(fd1, date(2017, 11, 17))
        except MyError as Er:
            self.assertEqual('The passed in fund does not match this tranche', Er.message)

        # when gate is 0.33, we need to pull 4 times,
        # last time we get 1
        fd4 = Fund('testFund4', 'A', 45, 0.33, 12)
        tc4 = Tranche('testFund4', '2017-01-01', 100)

        test4 = tc4.project_redem(fd4, '2017-11-17')
        result4 = [(date(2018, 12, 31), 33),
                   (date(2019, 12, 31), 33),
                   (date(2020, 12, 31), 33),
                   (date(2021, 12, 31), 1)]

        self.assertEqual(test4, result4)

        # when gate is 0.4, we need to pull 3 times,
        # last time we get 20
        fd5 = Fund('testFund4', 'm', 45, 0.4, 12)
        tc5 = Tranche('testFund4', '2017-01-01', 100)

        test5 = tc5.project_redem(fd5, '2017-11-17')
        result5 = [(date(2018, 1, 31), 40),
                   (date(2018, 2, 28), 40),
                   (date(2018, 3, 31), 20)]

        self.assertEqual(test5, result5)

    def test_project_settle(self):
        fd1 = Fund('testFund1', 'Q', 4, 0.25)
        tc = Tranche('testFund1', '2017-01-01', 10)

        test1 = tc.project_settle(fd1, '2017-11-17')
        result1 = [(date(2018, 1, 4), 2.5),
                   (date(2018, 4, 4), 2.5),
                   (date(2018, 7, 4), 2.5),
                   (date(2018, 10, 4), 2.5)]

        self.assertEqual(test1, result1)


if __name__ == "__main__":

    unittest.main()


