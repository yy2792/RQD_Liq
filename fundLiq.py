import unittest
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import bisect


# ignore lock up, given a redem frequency, what is the closest redem day for a specific date
def approach_day(start_date, redemfreq):

    temp_year = start_date.year
    temp_month = start_date.month
    temp_day = start_date.day
    res = None

    if redemfreq == 'M':
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


class Fund:

    FreqMap = {'monthly': 'M', 'quarterly':'Q', 'semiannual':'S', 'annual':'A'}

    def __init__(self, name, redemfreq, setperiod, gate, lockup=None):

        if redemfreq.lower() in self.FreqMap:
            redemfreq = self.FreqMap[redemfreq.lower()]

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
                   self.__lockup, self.__lockup)
        return rp_str

    def __repr__(self):
        return self.__str__()

    # given a specific invest_date, return the legal date for redemption (lock up)
    def est_legal_redem(self, invest_date):
        if self.__lockup is None:
            return invest_date

        return invest_date + relativedelta(months=self.__lockup)

    # given a specific date, and investment date, return the estimate redemption date
    def est_first_redem(self, invest_date, decision_date):
        # invest_date and decision date should all be in timestamp

        legal_start_date = self.est_legal_redem(invest_date)
        temp_start_date = decision_date

        # if decision date comes before legal start_dte, replace decision date with legal start
        if temp_start_date < legal_start_date:
            temp_start_date = legal_start_date

        res = approach_day(temp_start_date, self.__RedemFreq)

        return res


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








if __name__ == "__main__":

    unittest.main()


