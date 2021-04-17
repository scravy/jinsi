import unittest
from datetime import date

import jinsi


class DatesTest(unittest.TestCase):
    def test_date(self):
        result = jinsi.load1s("""
        value: 2020-02-20
        """)
        self.assertEqual(result['value'], date(2020, 2, 20))


if __name__ == '__main__':
    unittest.main()
