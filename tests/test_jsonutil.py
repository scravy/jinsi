import unittest
from dataclasses import dataclass

from jinsi.jsonutil import dumpjson, loadjson_all


class X:
    def __init__(self, *items):
        self._items = items

    def items(self):
        count = 0
        for item in self._items:
            yield count, item
            count += 1

@dataclass
class Z:
    foo: int
    bar: str


class JsonDumpTests(unittest.TestCase):

    def test_jsondump(self):
        self.assertEqual(dumpjson(X(1, "abc", 3)), '{"0":1,"1":"abc","2":3}')

    def test_loadall(self):
        result = tuple(loadjson_all("{}{}[]"))
        expected = ({}, {}, [])
        self.assertEqual(expected, result)

    def test_loadall_lines(self):
        result = tuple(loadjson_all("{}\n{}\n[]\n"))
        expected = ({}, {}, [])
        self.assertEqual(expected, result)

    def test_loadall_leading_whitespace(self):
        result = tuple(loadjson_all("\n{}\n{}\n[]\n"))
        expected = ({}, {}, [])
        self.assertEqual(expected, result)

    def test_dataclass(self):
        with self.assertRaises(TypeError):
            dumpjson(Z(1, 'quux'))
        res = dumpjson(Z(1, 'quux'), encode_dict=True)
        self.assertEqual('{"foo":1,"bar":"quux"}', res)


if __name__ == '__main__':
    unittest.main()
