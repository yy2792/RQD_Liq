import unittest


class Fund:

    def __init__(self, name, RedemFreq, SetPeriod, gate, lockup):
        self.__name = name
        self.__RedemFreq = RedemFreq
        self.__SetPeriod = SetPeriod
        self.__gate = gate
        self.__lockup = lockup

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




class TestFundFunctions(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_(self):



if __name__ == "__main__":

    unittest.main()


