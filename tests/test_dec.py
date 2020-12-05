#!/usr/bin/env python3

import unittest

from jinsi.dec import Dec


class DecTest(unittest.TestCase):

    def test_dec(self):
        self.assertEqual("0.33333333333333333", str(Dec(1) / Dec(3)))


if __name__ == '__main__':
    unittest.main()
