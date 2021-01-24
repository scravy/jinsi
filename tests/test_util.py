import unittest

from jinsi.util import load_all


class UtilTest(unittest.TestCase):
    def test_load_all(self):
        x = load_all("""{}{}""")
        self.assertEqual([{}, {}], [*x])


if __name__ == '__main__':
    unittest.main()
