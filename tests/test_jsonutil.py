import unittest

from jinsi import dumpjson


class X:
    def __init__(self, *items):
        self._items = items

    def items(self):
        count = 0
        for item in self._items:
            yield count, item
            count += 1


class JsonDumpTests(unittest.TestCase):

    def test_jsondump(self):
        self.assertEqual(dumpjson(X(1, "abc", 3)), '{"0":1,"1":"abc","2":3}')
